# 05 Observability And Tracing

## Goal

Add one simple OpenTelemetry trace to a real agent conversation and view it in the Foundry UI.

## Estimated time

10 to 15 minutes once your project is already working.

## Why this lab matters

In the earlier labs, you verified that the project, model, agent, and evaluation flow work correctly.

This lab adds observability to that flow. Evaluation helps you judge output quality, while tracing helps you inspect execution details such as timing, failures, and what happened during a request.

The example stays intentionally small: one short conversation with your existing agent and one custom application span around it. That keeps the tracing setup easy to understand before you move on to more complex flows such as tool calls and RAG.

## Official references

- [Microsoft Foundry app tracing guidance](https://learn.microsoft.com/azure/foundry-classic/how-to/develop/trace-application)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)

## One-time setup in Foundry

This lab requires an Azure Application Insights resource to be connected to the Foundry project. 

If you do not already have one, create the Application Insights resource with Azure CLI, you can use:

```bash
az monitor app-insights component create \
	--app my-foundry-appinsights \
	--location swedencentral \
	--kind web \
	--application-type web \
	--resource-group my-foundry-rg
```

The `az monitor app-insights component` commands are provided by the Azure CLI `application-insights` extension. Azure CLI usually installs that extension automatically the first time you run the command.

After that command succeeds, return to `Operate` > `Admin` > your project > `Connected resources` and connect the new Application Insights resource.

The example script reads that connection through `project_client.telemetry.get_application_insights_connection_string()`.

You do not need to add any new value to `.env` for this lab. The script reuses the existing project endpoint and model deployment name, and it reads the Application Insights connection string directly from the Foundry project telemetry configuration.

## Exercise

Run the tracing example:

```bash
python examples/04-observability/traced_model_call.py
```

## Example file

- [Open traced_model_call.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/04-observability/traced_model_call.py)

```python title="examples/04-observability/traced_model_call.py"
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
            input=(
                "In one short sentence, explain why observability matters for an AI "
                "assistant that summarizes clinical-trial documents."
            ),
        )

        second_response = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent_reference": {"name": agent_name, "type": "agent_reference"}
            },
            input=(
                "Now give one practical reason why traces help when debugging that "
                "clinical-trial assistant."
            ),
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
```

## What this lab demonstrates

1. Connect to the Foundry project with `AIProjectClient`.
2. Read the linked Application Insights connection string from the project telemetry helper.
3. Configure Azure Monitor OpenTelemetry export.
4. Instrument the OpenAI-compatible client with `OpenAIInstrumentor`.
5. Start a conversation that uses the existing agent named in `AZURE_AI_AGENT_NAME`.
6. Create one custom application span around that agent conversation.
7. Print the conversation id and response ids so you can match them in the Foundry UI.

## What is happening under the hood

- `configure_azure_monitor(...)` configures OpenTelemetry so spans are exported to the Application Insights resource linked to your Foundry resource.
- `OpenAIInstrumentor().instrument()` patches the OpenAI client so model calls automatically emit spans.
- `project_client.get_openai_client()` returns the same `openai.OpenAI` style client used in the earlier labs, so the tracing example stays consistent with the existing workshop flow.
- `trace.get_tracer(...)` gives you a tracer for your own application spans.
- `openai_client.conversations.create()` creates a conversation that can be routed through your Foundry agent.
- `with tracer.start_as_current_span("workshop.traced_agent_conversation")` creates a parent application span around the conversation. That span is most useful when you inspect the full trace in Application Insights, while Foundry focuses on the agent response trace rows.
- `openai_client.responses.create(..., extra_body={"agent_reference": ...})` sends each turn through the existing agent named in your `.env`, instead of calling the model directly.
- The script prints the `conversation.id` and the response ids returned by each turn. Those identifiers line up with what you see in the agent `Traces` view.
- The custom application span still has its own OpenTelemetry trace id, but that id is most useful in Application Insights. In Foundry, the printed response ids are usually the easiest way to locate the request.

## What you should see in Foundry

After running the script, open `Build` > `Agents`, select the agent named in `AZURE_AI_AGENT_NAME`, and open its `Traces` view.

The printed ids are useful in different places:

- `Conversation ID` groups the full exchange across multiple turns.
- `Response ID` identifies one specific traced response row in the Foundry `Traces` view.
- The OpenTelemetry application span trace id is mainly useful in Application Insights, not as the primary lookup key in the Foundry trace table.

In the Foundry `Traces` view, you should see:

- duration and status information
- model metadata and token usage details
- a conversation that matches the printed conversation id
- response rows that match the printed response ids

If you open the connected Application Insights resource, you can inspect the broader OpenTelemetry trace there, including the custom application span named `workshop.traced_agent_conversation` and the nested spans beneath it.

## Optional note

If you also want message content captured in traces, add this to your `.env` file before running the script:

```dotenv
OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

## Common issues

- `No Application Insights connection found.`: connect Application Insights from `Operate` > `Admin` > project > `Connected resources` first.
- Authentication errors: run `az login` again and verify access to the Foundry project.
- Agent not found: verify `AZURE_AI_AGENT_NAME` points to an agent version that already exists in your Foundry project.
- No trace appears immediately: wait a short time and refresh the trace view in the portal, or check the connected Application Insights resource directly in Azure Monitor.