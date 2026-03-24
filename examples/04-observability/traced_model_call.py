import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.monitor.opentelemetry import configure_azure_monitor
from dotenv import load_dotenv
from opentelemetry import trace
from opentelemetry.instrumentation.openai_v2 import OpenAIInstrumentor


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = f"{name}"
        if fallback:
            missing = f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def main() -> None:
    load_dotenv(Path(".env"))

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )

    project_client = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    try:
        connection_string = (
            project_client.telemetry.get_application_insights_connection_string()
        )
    except ResourceNotFoundError as exc:
        raise SystemExit(
            "Tracing is not connected for this Foundry resource yet. In Foundry, open your project, go to Tracing, and connect or create an Application Insights resource, then run this script again."
        ) from exc

    configure_azure_monitor(connection_string=connection_string)
    OpenAIInstrumentor().instrument()

    openai_client = project_client.get_openai_client()
    tracer = trace.get_tracer("foundry_workshop.observability")

    with tracer.start_as_current_span("workshop.simple_traced_call") as span:
        span.set_attribute("workshop.lab", "observability")
        span.set_attribute("foundry.model_deployment", model_deployment_name)

        response = openai_client.responses.create(
            model=model_deployment_name,
            input="In one short sentence, explain why observability matters for AI applications.",
        )

    print("Model response:")
    print(response.output_text)
    print()
    print("Open your Foundry project and inspect Tracing to see the new trace.")


if __name__ == "__main__":
    main()