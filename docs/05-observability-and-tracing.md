# 05 Observability And Tracing

## Goal

Add one simple OpenTelemetry trace to a model call and view it in the Foundry UI.

## Estimated time

10 to 15 minutes once your project is already working.

## Why this lab matters

In the earlier labs, you verified that the project, model, agent, and evaluation flow work correctly.

This lab adds observability to that flow. Evaluation helps you judge output quality, while tracing helps you inspect execution details such as timing, failures, and what happened during a request.

The example stays intentionally small: one Responses API call and one custom application span. That keeps the tracing setup easy to understand before you move on to more complex flows such as tool calls and RAG.

## Official references

- [Microsoft Foundry app tracing guidance](https://learn.microsoft.com/azure/foundry-classic/how-to/develop/trace-application)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)

## One-time setup in Foundry

Before running the example, open your Foundry project and go to `Operate` > `Admin`.

This lab requires an Azure Application Insights resource to be connected to the Foundry project. In the current portal layout, a reliable way to add that connection is:

1. Open `Operate` > `Admin`.
2. Select your Foundry project.
3. Open `Connected resources`.
4. Add or connect the Application Insights resource there.

The example script reads that connection through `project_client.telemetry.get_application_insights_connection_string()`.

You might also see trace-related UI under `Build` > `Agents` > select an agent > `Traces`. Treat that as a viewing and debugging surface, not the primary place to attach the Application Insights resource for this lab.

Microsoft's tracing articles still mostly describe the classic portal, so menu labels can differ from what you see in the new portal.

You do not need to add any new value to `.env` for this lab. The script reuses the existing project endpoint and model deployment name, and it reads the Application Insights connection string directly from the Foundry project telemetry configuration.

## Exercise

Run the tracing example:

```bash
python examples/04-observability/traced_model_call.py
```

## Example file

- [Open traced_model_call.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/04-observability/traced_model_call.py)

## What this lab demonstrates

1. Connect to the Foundry project with `AIProjectClient`.
2. Read the linked Application Insights connection string from the project telemetry helper.
3. Configure Azure Monitor OpenTelemetry export.
4. Instrument the OpenAI-compatible client with `OpenAIInstrumentor`.
5. Create one custom application span around a `responses.create(...)` call.
6. View the resulting trace in the Foundry UI.

## What is happening under the hood

- `configure_azure_monitor(...)` configures OpenTelemetry so spans are exported to the Application Insights resource linked to your Foundry resource.
- `OpenAIInstrumentor().instrument()` patches the OpenAI client so model calls automatically emit spans.
- `project_client.get_openai_client()` returns the same `openai.OpenAI` style client used in the earlier labs, so the tracing example stays consistent with the existing workshop flow.
- `trace.get_tracer(...)` gives you a tracer for your own application spans.
- `with tracer.start_as_current_span("workshop.simple_traced_call")` creates a parent span around the model request, which makes it easier to see your application step and the nested model call together in the trace timeline.
- `openai_client.responses.create(...)` still performs a normal Responses API call. The difference is that the call is now instrumented and exported through OpenTelemetry.

## What you should see in Foundry

After running the script, open the trace experience available in your portal. Depending on your current Foundry UI, that may appear in an agent's `Traces` view under `Build` > `Agents`, while the Application Insights connection itself is managed through `Operate` > `Admin` > project > `Connected resources`.

You should see a new trace that includes:

- a top-level custom span named `workshop.simple_traced_call`
- a nested span for the OpenAI model request
- duration and status information
- model metadata and token usage details

## Optional note

If you also want message content captured in traces, set this before running the script:

```bash
export OTEL_INSTRUMENTATION_GENAI_CAPTURE_MESSAGE_CONTENT=true
```

## Common issues

- `No Application Insights connection found.`: connect Application Insights from `Operate` > `Admin` > project > `Connected resources` first.
- Authentication errors: run `az login` again and verify access to the Foundry project.
- No trace appears immediately: wait a short time and refresh the trace view in the portal, or check the connected Application Insights resource directly in Azure Monitor.