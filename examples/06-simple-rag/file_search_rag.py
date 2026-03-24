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


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    asset_file_path = Path(__file__).with_name("product_info.md")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        vector_store = openai_client.vector_stores.create(name="WorkshopProductInfoStore")
        print(f"Vector store created: {vector_store.id}")

        with asset_file_path.open("rb") as file_handle:
            uploaded_file = openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file_handle,
            )
        print(f"File uploaded: {uploaded_file.id}")

        agent = project_client.agents.create_version(
            agent_name="WorkshopFileSearchAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a helpful assistant that answers from the uploaded product notes whenever the question can be answered from that document."
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
                    "Which product is best for cold-weather camping, and what is its temperature rating?"
                ),
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            )

            print("\nRAG response:\n")
            print(response.output_text)
        finally:
            project_client.agents.delete_version(agent_name=agent.name, agent_version=agent.version)
            print("\nAgent deleted")
            openai_client.vector_stores.delete(vector_store.id)
            print("Vector store deleted")


if __name__ == "__main__":
    main()