import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
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
        uploaded_file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=file_handle,
        )
    print(f"File uploaded: {uploaded_file.id}")

    return vector_store, True


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    asset_file_path = Path(__file__).with_name("product_info.md")
    keep_agent = get_keep_agent_setting()
    vector_store_name = "WorkshopClinicalSupplyStore"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        vector_store, created_vector_store = get_or_create_vector_store(
            openai_client,
            vector_store_name,
            asset_file_path,
        )

        agent = project_client.agents.create_version(
            agent_name="WorkshopFileSearchAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a healthcare operations assistant that answers from the "
                    "uploaded clinical supply notes whenever the question can be "
                    "answered from that document."
                ),
                tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
            ),
            description="Workshop example for simple file-search RAG.",
        )
        print(f"Agent created: {agent.name} (version {agent.version})")

        try:
            conversation = openai_client.conversations.create()
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=(
                    "Which item is best for transporting refrigerated vaccine doses, and what temperature range does it support?"
                ),
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            )

            print("\nRAG response:\n")
            print(response.output_text)
        finally:
            if keep_agent:
                print(
                    f"\nAgent kept: {agent.name} (version {agent.version})"
                )
                print(
                    f"Vector store kept: {vector_store.id}. Set KEEP_AGENT=false to restore cleanup behavior."
                )
            else:
                project_client.agents.delete_version(
                    agent_name=agent.name,
                    agent_version=agent.version,
                )
                print("\nAgent deleted")
                if created_vector_store:
                    openai_client.vector_stores.delete(vector_store.id)
                    print("Vector store deleted")


if __name__ == "__main__":
    main()