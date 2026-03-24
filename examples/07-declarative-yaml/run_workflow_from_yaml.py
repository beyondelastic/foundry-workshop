import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from yaml_runtime import cleanup_resources, load_yaml, provision_agents, render_prompt


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = name if not fallback else f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


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

    base_dir = Path(__file__).resolve().parent
    agents_config = load_yaml(base_dir / "agents.yaml")
    workflow_config = load_yaml(base_dir / "workflow.yaml")["workflow"]

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        agents, vector_store_ids = provision_agents(
            project_client,
            openai_client,
            base_dir,
            agents_config,
            model_deployment_name,
        )

        try:
            context = {
                "workflow_input": workflow_config["input"],
                "steps": {},
            }

            print(f"Workflow: {workflow_config['name']}")
            print(f"Scenario: {workflow_config['input']}\n")

            for step in workflow_config["steps"]:
                prompt = render_prompt(step["prompt"], context)
                output = run_agent(openai_client, agents[step["agent"]].name, prompt)
                context["steps"][step["id"]] = {"output": output}

                print(f"Step {step['id']} output:\n")
                print(output)
                print("\n" + "=" * 60 + "\n")

            final_step_id = workflow_config["steps"][-1]["id"]
            print("Final answer:\n")
            print(context["steps"][final_step_id]["output"])
        finally:
            cleanup_resources(project_client, openai_client, agents, vector_store_ids)


if __name__ == "__main__":
    main()