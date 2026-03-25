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
    agent_name = get_env("AZURE_AI_AGENT_NAME", "AGENT_NAME")

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
            "Tracing is not connected for this Foundry project yet. In Foundry, open Operate > Admin > your project > Connected resources, connect or create an Application Insights resource, then run this script again."
        ) from exc

    configure_azure_monitor(connection_string=connection_string)
    OpenAIInstrumentor().instrument()

    openai_client = project_client.get_openai_client()
    tracer = trace.get_tracer("foundry_workshop.observability")
    conversation = openai_client.conversations.create()

    with tracer.start_as_current_span("workshop.traced_agent_conversation") as span:
        span.set_attribute("workshop.lab", "observability")
        span.set_attribute("foundry.model_deployment", model_deployment_name)
        span.set_attribute("foundry.agent_name", agent_name)
        span.set_attribute("foundry.conversation_id", conversation.id)

        first_response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {"name": agent_name, "type": "agent_reference"}
            },
            input="In one short sentence, explain why observability matters for AI applications.",
        )

        second_response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {"name": agent_name, "type": "agent_reference"}
            },
            input="Now give one practical reason why traces help when debugging that agent.",
        )

        app_trace_id = format(span.get_span_context().trace_id, "032x")

    # This example is a short-lived script, so force-flush telemetry before exit.
    tracer_provider = trace.get_tracer_provider()
    if hasattr(tracer_provider, "force_flush"):
        tracer_provider.force_flush()

    print(f"Application span trace id (App Insights): {app_trace_id}")
    print(f"Conversation id: {conversation.id}")
    print(f"First response id: {first_response.id}")
    print(f"Second response id: {second_response.id}")
    print()
    print("First response:")
    print(first_response.output_text)
    print()
    print("Second response:")
    print(second_response.output_text)
    print()
    print(
        "Open your agent's Traces view in Foundry and match the conversation id or response ids above. The App Insights trace id is useful when querying telemetry directly in Azure Monitor."
    )


if __name__ == "__main__":
    main()