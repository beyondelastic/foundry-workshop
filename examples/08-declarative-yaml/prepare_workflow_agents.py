import os
from pathlib import Path

import yaml

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


def get_or_create_vector_store(openai_client, store_name: str, file_path: Path):
    for vector_store in openai_client.vector_stores.list(limit=100, order="desc"):
        if vector_store.name == store_name:
            print(f"Vector store reused: {vector_store.id}")
            return vector_store

    vector_store = openai_client.vector_stores.create(name=store_name)
    print(f"Vector store created: {vector_store.id}")

    with file_path.open("rb") as file_handle:
        uploaded_file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=file_handle,
        )
    print(f"File uploaded: {uploaded_file.id}")

    return vector_store


def load_yaml(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as file_handle:
        data = yaml.safe_load(file_handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must load to an object: {file_path}")
    return data


def get_agent_specs(config: dict) -> list[dict]:
    if "agents" in config:
        agent_specs = config["agents"]
    elif config.get("object") == "agent.version" and "definition" in config:
        agent_specs = [config]
    else:
        raise ValueError(
            "Agent YAML must contain either an 'agents' list or a single Foundry-style agent.version object"
        )

    if not isinstance(agent_specs, list) or not agent_specs:
        raise ValueError("Agent YAML must contain at least one agent definition")

    return agent_specs


def build_tools(openai_client, base_dir: Path, tool_specs: list[dict]):
    tools = []
    supporting_vector_store_ids: list[str] = []

    for tool_spec in tool_specs:
        tool_type = tool_spec["type"]

        if tool_type == "web_search":
            location = tool_spec.get("user_location", {})
            tools.append(
                WebSearchTool(
                    user_location=WebSearchApproximateLocation(
                        country=location.get("country", "NL"),
                        city=location.get("city", "Amsterdam"),
                        region=location.get("region", "Noord-Holland"),
                    )
                )
            )
            continue

        if tool_type == "file_search":
            relative_files = tool_spec.get("files", [])
            if not relative_files:
                raise ValueError("file_search tool requires at least one file")

            vector_store_name = tool_spec.get("vector_store_name")
            if not vector_store_name:
                raise ValueError("file_search tool requires vector_store_name")

            if len(relative_files) != 1:
                raise ValueError("This workshop sample expects exactly one file per file_search tool")

            file_path = base_dir / relative_files[0]
            vector_store = get_or_create_vector_store(
                openai_client,
                vector_store_name,
                file_path,
            )
            tools.append(FileSearchTool(vector_store_ids=[vector_store.id]))
            supporting_vector_store_ids.append(vector_store.id)
            continue

        raise ValueError(f"Unsupported tool type: {tool_type}")

    return tools, supporting_vector_store_ids


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    base_dir = Path(__file__).resolve().parent
    agents_config = load_yaml(base_dir / "agents.yaml")

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        supporting_vector_store_ids: list[str] = []

        for agent_spec in get_agent_specs(agents_config):
            definition = agent_spec["definition"]
            tools, vector_store_ids = build_tools(
                openai_client,
                base_dir,
                definition.get("tools", []),
            )
            supporting_vector_store_ids.extend(vector_store_ids)

            model_name = definition.get("model", model_deployment_name)
            if model_name == "__MODEL_DEPLOYMENT_NAME__":
                model_name = model_deployment_name

            agent = project_client.agents.create_version(
                agent_name=agent_spec["name"],
                definition=PromptAgentDefinition(
                    model=model_name,
                    instructions=definition["instructions"],
                    tools=tools,
                ),
                description=agent_spec.get("description"),
            )

            print(f"Agent ready: {agent.name} (version {agent.version})")

        if supporting_vector_store_ids:
            print(
                f"Supporting vector stores: {', '.join(dict.fromkeys(supporting_vector_store_ids))}"
            )
        print(
            "Next step: create or update the workflow in Foundry using examples/08-declarative-yaml/workflow.yaml."
        )


if __name__ == "__main__":
    main()