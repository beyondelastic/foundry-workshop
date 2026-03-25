import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    FileSearchTool,
    PromptAgentDefinition,
    WebSearchApproximateLocation,
    WebSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = name if not fallback else f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def get_keep_agent_setting() -> bool:
    value = os.getenv("KEEP_AGENT", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def get_or_create_vector_store(openai_client, store_name: str, file_path: Path):
    for vector_store in openai_client.vector_stores.list(limit=100, order="desc"):
        if vector_store.name == store_name:
            print(f"Vector store reused: {vector_store.id}")
            return vector_store, False

    vector_store = openai_client.vector_stores.create(name=store_name)
    print(f"Vector store created: {vector_store.id}")

    with file_path.open("rb") as file_handle:
        openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=file_handle,
        )

    return vector_store, True


def run_agent(openai_client, agent_name: str, prompt: str) -> str:
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=prompt,
        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
    )
    return response.output_text


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    keep_agent = get_keep_agent_setting()
    product_file_path = (
        Path(__file__).resolve().parents[1] / "06-simple-rag" / "product_info.md"
    )
    vector_store_name = "WorkshopMultiAgentStore"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        vector_store, created_vector_store = get_or_create_vector_store(
            openai_client,
            vector_store_name,
            product_file_path,
        )

        research_agent = project_client.agents.create_version(
            agent_name="WorkshopResearchAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a research assistant. Use web search to gather short, current guidance for outdoor trip planning. Return only three concise bullets."
                ),
                tools=[
                    WebSearchTool(
                        user_location=WebSearchApproximateLocation(
                            country="GB",
                            city="London",
                            region="London",
                        )
                    )
                ],
            ),
            description="Research agent for workshop multi-agent handoff lab.",
        )

        product_agent = project_client.agents.create_version(
            agent_name="WorkshopProductAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a product recommendation assistant. Use the uploaded product notes to recommend one product. Base the recommendation on the user scenario and the research notes you receive."
                ),
                tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
            ),
            description="Product agent for workshop multi-agent handoff lab.",
        )

        try:
            scenario = (
                "A participant is planning a rainy spring weekend hiking trip in the UK and wants one product recommendation from the catalog."
            )

            research_notes = run_agent(
                openai_client,
                research_agent.name,
                (
                    f"Scenario: {scenario}\n"
                    "Find recent public guidance for what matters most on this type of trip. Return exactly three bullets."
                ),
            )

            print("Research agent output:\n")
            print(research_notes)

            final_recommendation = run_agent(
                openai_client,
                product_agent.name,
                (
                    f"Scenario: {scenario}\n\n"
                    f"Research notes:\n{research_notes}\n\n"
                    "Using the uploaded product notes, recommend exactly one product. Explain why it fits in 3 to 4 bullets."
                ),
            )

            print("\nProduct agent output:\n")
            print(final_recommendation)
        finally:
            if keep_agent:
                print(
                    f"\nAgents kept: {research_agent.name} (version {research_agent.version}), {product_agent.name} (version {product_agent.version})"
                )
                print(
                    f"Vector store kept: {vector_store.id}. Set KEEP_AGENT=false to restore cleanup behavior."
                )
            else:
                project_client.agents.delete_version(
                    agent_name=research_agent.name,
                    agent_version=research_agent.version,
                )
                project_client.agents.delete_version(
                    agent_name=product_agent.name,
                    agent_version=product_agent.version,
                )
                if created_vector_store:
                    openai_client.vector_stores.delete(vector_store.id)


if __name__ == "__main__":
    main()