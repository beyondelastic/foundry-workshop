import os
import time
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = f"{name}"
        if fallback:
            missing = f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    agent_name = get_env("AZURE_AI_AGENT_NAME", "AGENT_NAME")
    dataset_path = Path(__file__).with_name("test-queries.jsonl")

    credential = DefaultAzureCredential()
    project_client = AIProjectClient(endpoint=project_endpoint, credential=credential)
    openai_client = project_client.get_openai_client()

    dataset = project_client.datasets.upload_file(
        name="agent-test-queries",
        version="1",
        file_path=str(dataset_path),
    )
    print(f"Uploaded dataset: {dataset.id}")

    testing_criteria = [
        {
            "type": "azure_ai_evaluator",
            "name": "Task Adherence",
            "evaluator_name": "builtin.task_adherence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_items}}",
            },
            "initialization_parameters": {"deployment_name": model_deployment_name},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Coherence",
            "evaluator_name": "builtin.coherence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
            "initialization_parameters": {"deployment_name": model_deployment_name},
        },
        {
            "type": "azure_ai_evaluator",
            "name": "Violence",
            "evaluator_name": "builtin.violence",
            "data_mapping": {
                "query": "{{item.query}}",
                "response": "{{sample.output_text}}",
            },
        },
    ]

    data_source_config = {
        "type": "custom",
        "item_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string"},
            },
            "required": ["query"],
        },
        "include_sample_schema": True,
    }

    evaluation = openai_client.evals.create(
        name="Agent Quality Evaluation",
        data_source_config=data_source_config,
        testing_criteria=testing_criteria,
    )
    print(f"Created evaluation: {evaluation.id}")

    eval_run = openai_client.evals.runs.create(
        eval_id=evaluation.id,
        name="Agent Evaluation Run",
        data_source={
            "type": "azure_ai_target_completions",
            "source": {
                "type": "file_id",
                "id": dataset.id,
            },
            "input_messages": {
                "type": "template",
                "template": [
                    {
                        "type": "message",
                        "role": "user",
                        "content": {
                            "type": "input_text",
                            "text": "{{item.query}}",
                        },
                    }
                ],
            },
            "target": {
                "type": "azure_ai_agent",
                "name": agent_name,
            },
        },
    )
    print(f"Started evaluation run: {eval_run.id}")

    while True:
        run = openai_client.evals.runs.retrieve(
            run_id=eval_run.id,
            eval_id=evaluation.id,
        )
        if run.status in ["completed", "failed"]:
            break
        time.sleep(5)

    print(f"Final status: {run.status}")
    print(f"Report URL: {run.report_url}")


if __name__ == "__main__":
    main()