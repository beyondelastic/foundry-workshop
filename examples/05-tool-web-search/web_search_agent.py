import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WebSearchApproximateLocation,
    WebSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai import BadRequestError


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = name if not fallback else f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def get_keep_agent_setting() -> bool:
    value = os.getenv("KEEP_AGENT", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    keep_agent = get_keep_agent_setting()

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        tool = WebSearchTool(
            user_location=WebSearchApproximateLocation(
                country="GB",
                city="London",
                region="London",
            )
        )

        agent = project_client.agents.create_version(
            agent_name="WorkshopWebSearchAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a helpful assistant. Use web search when the user asks for recent or time-sensitive public information."
                ),
                tools=[tool],
            ),
            description="Workshop example for simple built-in tool usage.",
        )
        print(f"Agent created: {agent.name} (version {agent.version})")

        try:
            conversation = openai_client.conversations.create()
            try:
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    input=(
                        "Find one recent Microsoft Learn page about Foundry evaluation. Give the title and one-sentence purpose."
                    ),
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )
            except BadRequestError as exc:
                error_code = getattr(exc, "code", None)
                if error_code == "context_length_exceeded":
                    raise SystemExit(
                        "This tool example exceeded the selected model deployment's context window. Try the shorter default prompt in this sample, or switch AZURE_AI_MODEL_DEPLOYMENT_NAME to a larger-context model."
                    ) from exc
                raise

            used_web_search = any(
                getattr(item, "type", None) == "web_search_call"
                for item in response.output
            )

            print("\nTool-backed response:\n")
            print(response.output_text)
            print()
            print(f"Web search tool used: {used_web_search}")
        finally:
            if keep_agent:
                print(
                    f"\nAgent kept: {agent.name} (version {agent.version}). Set KEEP_AGENT=false to restore cleanup behavior."
                )
            else:
                project_client.agents.delete_version(
                    agent_name=agent.name,
                    agent_version=agent.version,
                )
                print("\nAgent deleted")


if __name__ == "__main__":
    main()