import re
from os import getenv
from pathlib import Path

import yaml
from azure.ai.projects.models import (
    FileSearchTool,
    PromptAgentDefinition,
    WebSearchApproximateLocation,
    WebSearchTool,
)


TOKEN_PATTERN = re.compile(r"{{\s*([^}]+?)\s*}}")


def load_yaml(file_path: Path) -> dict:
    with file_path.open("r", encoding="utf-8") as file_handle:
        data = yaml.safe_load(file_handle)
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must load to an object: {file_path}")
    return data


def render_prompt(template: str, context: dict) -> str:
    def replace_token(match: re.Match[str]) -> str:
        token = match.group(1).strip()
        if token == "workflow_input":
            return context["workflow_input"]

        if token.startswith("steps.") and token.endswith(".output"):
            _, step_id, _ = token.split(".")
            return context["steps"][step_id]["output"]

        raise ValueError(f"Unsupported template token: {token}")

    return TOKEN_PATTERN.sub(replace_token, template)


def get_keep_agent_setting() -> bool:
    value = getenv("KEEP_AGENT", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def get_or_create_vector_store(openai_client, store_name: str, file_paths: list[Path]):
    for vector_store in openai_client.vector_stores.list(limit=100, order="desc"):
        if vector_store.name == store_name:
            return vector_store, False

    vector_store = openai_client.vector_stores.create(name=store_name)

    for file_path in file_paths:
        with file_path.open("rb") as file_handle:
            openai_client.vector_stores.files.upload_and_poll(
                vector_store_id=vector_store.id,
                file=file_handle,
            )

    return vector_store, True


def provision_agents(
    project_client,
    openai_client,
    base_dir: Path,
    agents_config: dict,
    model_deployment_name: str,
) -> tuple[dict, list[str]]:
    created_agents = {}
    vector_store_ids: list[str] = []

    for agent_spec in agents_config["agents"]:
        tools = []

        for tool_spec in agent_spec.get("tools", []):
            tool_type = tool_spec["type"]

            if tool_type == "web_search":
                location = tool_spec.get("location", {})
                tools.append(
                    WebSearchTool(
                        user_location=WebSearchApproximateLocation(
                            country=location.get("country", "GB"),
                            city=location.get("city", "London"),
                            region=location.get("region", "London"),
                        )
                    )
                )
                continue

            if tool_type == "file_search":
                file_paths = [
                    base_dir / relative_path for relative_path in tool_spec.get("files", [])
                ]
                vector_store, created_vector_store = get_or_create_vector_store(
                    openai_client,
                    f"{agent_spec['foundry_name']}Store",
                    file_paths,
                )

                if created_vector_store:
                    vector_store_ids.append(vector_store.id)
                    print(f"Vector store created: {vector_store.id}")
                else:
                    print(f"Vector store reused: {vector_store.id}")

                tools.append(FileSearchTool(vector_store_ids=[vector_store.id]))
                continue

            raise ValueError(f"Unsupported tool type: {tool_type}")

        agent = project_client.agents.create_version(
            agent_name=agent_spec["foundry_name"],
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=agent_spec["instructions"],
                tools=tools,
            ),
            description=agent_spec.get("description"),
        )
        created_agents[agent_spec["id"]] = agent

    return created_agents, vector_store_ids


def cleanup_resources(project_client, openai_client, agents: dict, vector_store_ids: list[str]) -> None:
    if get_keep_agent_setting():
        kept_agents = ", ".join(
            f"{agent.name} (version {agent.version})" for agent in agents.values()
        )
        print(
            f"Resources kept: {kept_agents}."
        )
        if vector_store_ids:
            print(
                f"Vector stores kept: {', '.join(vector_store_ids)}. Set KEEP_AGENT=false to restore cleanup behavior."
            )
        else:
            print("Set KEEP_AGENT=false to restore cleanup behavior.")
        return

    for agent in agents.values():
        project_client.agents.delete_version(
            agent_name=agent.name,
            agent_version=agent.version,
        )

    for vector_store_id in vector_store_ids:
        openai_client.vector_stores.delete(vector_store_id)