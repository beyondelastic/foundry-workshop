# 09 Native Foundry Workflow

!!! warning "This lab is optional"
    The native Foundry workflow feature is in preview and [will retire on December 1, 2026](https://learn.microsoft.com/en-us/azure/foundry/agents/concepts/workflow). You can skip this lab.

    If you are building new workflows, use the Microsoft Agent Framework instead. See the [Microsoft Agent Framework Workshop](https://beyondelastic.github.io/maf-workshop/) to get started.

## Goal

Use a native Foundry workflow for a two-step mobile vaccination clinic scenario, then invoke that workflow from Python.

## Estimated time

20 to 30 minutes.

## Official references

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Microsoft Agent Framework workflows overview](https://learn.microsoft.com/agent-framework/workflows/)
- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)
- [microsoft-foundry/foundry-samples](https://github.com/microsoft-foundry/foundry-samples)

## How this lab works

This lab uses a native Foundry workflow YAML.

The pattern is:

1. Python prepares the agents that the workflow will invoke.
2. Foundry stores and manages the workflow resource.
3. Python invokes that workflow through the Foundry project endpoint.

This is the platform-managed workflow approach rather than the Python-managed orchestration approach.

## Scenario

One workflow step asks a research agent for current mobile vaccination clinic guidance.

A second workflow step asks a supply agent to recommend exactly one catalog item based on that research.

Foundry owns the workflow definition and executes the workflow actions.

## Exercise

1. Prepare the agents used by the workflow:

```bash
python examples/08-declarative-yaml/prepare_workflow_agents.py
```

2. In the Foundry portal, open the `Workflows` experience, create a workflow, and paste the contents of `examples/08-declarative-yaml/workflow.yaml` into the workflow editor.

!!! note "Save the workflow with the exact name"
    When you save the workflow, it must be named `Workshop-Clinical-Operations-Workflow` so the Python invocation script can find it. If you choose a different name, set `AZURE_AI_WORKFLOW_NAME` in `.env` to match.

3. Invoke the saved workflow from Python:

```bash
python examples/08-declarative-yaml/invoke_foundry_workflow.py
```

If you want the full event stream for troubleshooting, run:

```bash
WORKFLOW_VERBOSE=true python examples/08-declarative-yaml/invoke_foundry_workflow.py
```

Set `AZURE_AI_WORKFLOW_NAME` in `.env` only if you save the workflow under a different name than the provided default.

## Example files

- [Open agents.yaml on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/agents.yaml)
- [Open workflow.yaml on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/workflow.yaml)
- [Open prepare_workflow_agents.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/prepare_workflow_agents.py)
- [Open invoke_foundry_workflow.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/invoke_foundry_workflow.py)
- [Open gear_notes.md on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/gear_notes.md)

```yaml title="examples/08-declarative-yaml/agents.yaml"
version: 1
agents:
  - object: agent.version
    id: WorkshopFoundryWorkflowResearchAgent:1
    name: WorkshopFoundryWorkflowResearchAgent
    version: "1"
    description: Research agent for the native Foundry workflow lab.
    definition:
      kind: prompt
      # Replaced at runtime by prepare_workflow_agents.py using AZURE_AI_MODEL_DEPLOYMENT_NAME.
      model: __MODEL_DEPLOYMENT_NAME__
      instructions: >-
        You are a healthcare operations research assistant. Use web search to
        gather concise, recent public guidance for vaccine handling or mobile
        vaccination clinic operations. Return exactly three short bullets.
      tools:
        - type: web_search
          user_location:
            country: NL
            city: Amsterdam
            region: Noord-Holland

  - object: agent.version
    id: WorkshopFoundryWorkflowSupplyAgent:1
    name: WorkshopFoundryWorkflowSupplyAgent
    version: "1"
    description: Supply recommendation agent for the native Foundry workflow lab.
    definition:
      kind: prompt
      # Replaced at runtime by prepare_workflow_agents.py using AZURE_AI_MODEL_DEPLOYMENT_NAME.
      model: __MODEL_DEPLOYMENT_NAME__
      instructions: >-
        You are a clinical supply assistant. Use the uploaded clinic supply
        catalog to recommend exactly one item. Base your answer on the scenario
        and the research notes you receive.
      tools:
        - type: file_search
          vector_store_name: WorkshopFoundryWorkflowSupplyStore
          files:
            - gear_notes.md
```

```yaml title="examples/08-declarative-yaml/workflow.yaml"
kind: workflow
id: ""
name: Workshop-Clinical-Operations-Workflow
description: Recommends one clinical supply item for a mobile vaccination scenario using a native Foundry workflow.
trigger:
  kind: OnConversationStart
  id: trigger_clinical_operations
  actions:
    - kind: SetVariable
      id: set_clinic_scenario
      variable: Local.ClinicScenario
      value: A community health team is planning a one-day mobile vaccination clinic in Amsterdam and wants one supply recommendation from the catalog.

    - kind: InvokeAzureAgent
      id: run_research_agent
      agent:
        name: WorkshopFoundryWorkflowResearchAgent
      conversationId: =System.ConversationId
      input:
        messages: >-
          Scenario: {Local.ClinicScenario}

          Find recent public guidance for what matters most for this type of clinic. Return exactly three bullets.
      output:
        autoSend: false
        messages: Local.ResearchOutputText

    - kind: InvokeAzureAgent
      id: run_supply_agent
      agent:
        name: WorkshopFoundryWorkflowSupplyAgent
      conversationId: =System.ConversationId
      input:
        messages: >-
          Scenario: {Local.ClinicScenario}

          Research notes:
          {Local.ResearchOutputText}

          Using only the uploaded clinic supply catalog, recommend exactly one item. Explain the choice in three bullets and include the price.
      output:
        autoSend: false
        messages: Local.RecommendationOutputText

    - kind: SendActivity
      id: send_final_response
      activity: '{Local.RecommendationOutputText}'

    - kind: EndConversation
      id: end_clinical_operations_workflow
```

```python title="examples/08-declarative-yaml/prepare_workflow_agents.py"
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
```

```python title="examples/08-declarative-yaml/invoke_foundry_workflow.py"
import os
import json

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
RESPONSE_FAILED = "response.failed"
RESPONSE_COMPLETED = "response.completed"


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = name if not fallback else f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def is_verbose_enabled() -> bool:
    return os.getenv("WORKFLOW_VERBOSE", "false").lower() in {"1", "true", "yes", "on"}


def get_field(value, name: str, default=None):
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def get_message_text(item) -> str:
    text_parts: list[str] = []

    for part in get_field(item, "content", []) or []:
        if get_field(part, "type") == "output_text":
            text = get_field(part, "text", "")
            if text:
                text_parts.append(text)

    return "\n".join(text_parts).strip()


def format_agent_label(agent_name: str | None) -> str:
    if not agent_name:
        return "Agent"

    label = agent_name
    if label.startswith("WorkshopFoundryWorkflow"):
        label = label.removeprefix("WorkshopFoundryWorkflow")
    if label.endswith("Agent"):
        label = label.removesuffix("Agent")

    label = label.replace("_", " ").strip()
    if not label:
        return "Agent"

    return f"{label} Agent"


def extract_text_from_workflow_wrapper(text: str) -> str | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, list) or not payload:
        return None

    first_item = payload[0]
    if not isinstance(first_item, dict):
        return None

    direct_text = first_item.get("Text")
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text.strip()

    for content_item in first_item.get("Content", []):
        if not isinstance(content_item, dict):
            continue
        if content_item.get("Type") == "Text":
            value = content_item.get("Value")
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def extract_display_text(response, workflow_name: str) -> str:
    fallback_text = ""

    for item in reversed(getattr(response, "output", []) or []):
        if get_field(item, "type") != "message":
            continue

        text = get_message_text(item)
        if not text:
            continue

        agent_reference = get_field(item, "agent_reference")
        agent_name = get_field(agent_reference, "name")

        if agent_name == workflow_name:
            extracted = extract_text_from_workflow_wrapper(text)
            if extracted:
                return extracted
            fallback_text = text
            continue

        return text

    if fallback_text:
        return fallback_text

    output_text = (getattr(response, "output_text", None) or "").strip()
    return output_text


def extract_conversation_messages(response, workflow_name: str) -> list[tuple[str, str]]:
    messages: list[tuple[str, str]] = []
    seen_messages: set[tuple[str, str]] = set()

    for item in getattr(response, "output", []) or []:
        if get_field(item, "type") != "message":
            continue

        text = get_message_text(item)
        if not text:
            continue

        agent_reference = get_field(item, "agent_reference")
        agent_name = get_field(agent_reference, "name")

        if agent_name == workflow_name:
            continue

        message_key = (agent_name or "", text)
        if message_key in seen_messages:
            continue

        seen_messages.add(message_key)
        messages.append((format_agent_label(agent_name), text))

    return messages


def invoke_workflow_verbose(openai_client, conversation_id: str, workflow_name: str) -> None:
    stream = openai_client.responses.create(
        conversation=conversation_id,
        extra_body={
            "agent_reference": {
                "name": workflow_name,
                "type": "agent_reference",
            }
        },
        input="Start the mobile vaccination clinic planning workflow.",
        stream=True,
        metadata={"x-ms-debug-mode-enabled": "1"},
    )

    print(f"Created conversation (id: {conversation_id})")
    print(f"Running workflow: {workflow_name}\n")
    for event in stream:
        if event.type == RESPONSE_OUTPUT_TEXT_DELTA:
            print(event.delta, end="", flush=True)
        elif (
            event.type == RESPONSE_OUTPUT_ITEM_ADDED
            and event.item.type == "workflow_action"
        ):
            print(
                f"\n[{event.item.action_id}] status={event.item.status} previous={event.item.previous_action_id}"
            )
        elif (
            event.type == RESPONSE_OUTPUT_ITEM_DONE
            and event.item.type == "workflow_action"
        ):
            print(
                f"\n[{event.item.action_id}] status={event.item.status} previous={event.item.previous_action_id}"
            )
        elif event.type == RESPONSE_FAILED:
            error = getattr(event, "error", None)
            print(f"\nWorkflow failed: {error}")
        elif event.type == RESPONSE_COMPLETED:
            print("\n[response.completed]")
        else:
            item = getattr(event, "item", None)
            item_type = getattr(item, "type", None)
            print(f"\n[event:{event.type}] item_type={item_type}")

    print()


def invoke_workflow_quiet(openai_client, conversation_id: str, workflow_name: str) -> None:
    response = openai_client.responses.create(
        conversation=conversation_id,
        extra_body={
            "agent_reference": {
                "name": workflow_name,
                "type": "agent_reference",
            }
        },
        input="Start the mobile vaccination clinic planning workflow.",
    )

    messages = extract_conversation_messages(response, workflow_name)
    if messages:
        for index, (label, text) in enumerate(messages):
            if index > 0:
                print()
            print(f"{label}:")
            print(text)
        return

    output_text = extract_display_text(response, workflow_name)
    if output_text:
        print(output_text)
        return

    raise RuntimeError("Workflow completed without text output. Re-run with WORKFLOW_VERBOSE=true for detailed events.")


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    workflow_name = os.getenv(
        "AZURE_AI_WORKFLOW_NAME", "Workshop-Clinical-Operations-Workflow"
    )
    verbose = is_verbose_enabled()

    with AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:
        with project_client.get_openai_client() as openai_client:
            conversation = openai_client.conversations.create()

            try:
                if verbose:
                    invoke_workflow_verbose(openai_client, conversation.id, workflow_name)
                else:
                    invoke_workflow_quiet(openai_client, conversation.id, workflow_name)
            finally:
                openai_client.conversations.delete(conversation_id=conversation.id)
                if verbose:
                    print("Conversation deleted")


if __name__ == "__main__":
    main()
```

```markdown title="examples/08-declarative-yaml/gear_notes.md"
# Contoso Mobile Clinic Supply Notes

## ColdChain Transit Case

- Price: $329
- Best use: transporting refrigerated vaccine doses between care sites
- Notable feature: validated temperature hold between 2 C and 8 C for up to 12 hours

## Portable Screening Station

- Price: $189
- Best use: pop-up intake desks for community health events
- Notable feature: fold-out workspace with integrated privacy side panels

## Mobile Consent Tablet

- Price: $449
- Best use: digital patient intake and research consent capture
- Notable feature: 10-hour battery life with encrypted form storage

## Sharps Safety Station

- Price: $58
- Best use: temporary vaccination and phlebotomy stations
- Notable feature: portable container with lockable lid and integrated tray
```

## What each file is doing

`agents.yaml` defines the supporting agent versions in YAML.

This is the agent-side equivalent of the workflow definition. It keeps the agent name, description, prompt definition, and tool configuration in one declarative file instead of hardcoding those values directly in Python.

The workshop version is intentionally close to the shape you see in the Foundry UI export. The setup script accepts either a file containing an `agents:` list or a single exported `object: agent.version` record.

It also uses one small workshop-friendly extension for file search: `vector_store_name` plus `files`. That lets the setup script create or reuse the correct vector store in each environment instead of hardcoding a store ID that only works in one project.

`workflow.yaml` is now a real Foundry workflow definition.

It uses workflow actions like `SetVariable`, `InvokeAzureAgent`, `SendActivity`, and `EndConversation`. That means the YAML is meant for the Foundry workflow system itself, not for a local Python parser in this repository.

In this sample:

1. the workflow stores the clinic scenario in a workflow variable
2. it invokes the research agent
3. it invokes the supply agent with the research output
4. it sends the final answer back to the conversation

`prepare_workflow_agents.py` creates the agents that the workflow references.

The workflow YAML refers to agent names, so those agents must already exist in Foundry. This script creates or updates:

1. `WorkshopFoundryWorkflowResearchAgent`
2. `WorkshopFoundryWorkflowSupplyAgent`

The script now reads those definitions from `agents.yaml`, resolves any file-search vector stores, and then creates the corresponding Foundry prompt agent versions.

`invoke_foundry_workflow.py` is the Python client that runs the workflow.

It does not interpret workflow YAML. It simply opens a conversation, invokes the workflow by name through `agent_reference`, and prints a concise transcript of the agent messages in order.

If you set `WORKFLOW_VERBOSE=true`, it switches to a streamed troubleshooting view that prints workflow actions and lower-level response events.

`gear_notes.md` is the local grounding file.

This is the catalog used by the supply agent. It is not the workflow. It is the data source that the supply agent retrieves from when making its recommendation.

## What happens when you run it

The easiest way to understand this lab is to split it into three phases.

The execution flow is:

1. `prepare_workflow_agents.py` creates or updates the research and supply agents.
2. You save `workflow.yaml` in the Foundry workflow editor so Foundry has a real workflow resource.
3. `invoke_foundry_workflow.py` starts a conversation and invokes that workflow.

Once the workflow is running, Foundry performs the orchestration itself:

1. the workflow trigger starts on conversation start
2. a workflow variable is initialized with the clinic scenario
3. Foundry invokes the research agent
4. the research output is stored in a workflow variable
5. Foundry invokes the supply agent with that research output included in the next prompt
6. the final recommendation is sent back to the conversation

Foundry owns the step order and action execution.

## Why this is useful

This pattern shows what changes when you move from application-managed orchestration to platform-managed orchestration.

You can change different concerns in different files:

1. change the workflow structure in `workflow.yaml`
2. change the agent definitions in `prepare_workflow_agents.py`
3. change the local grounding data in `gear_notes.md`
4. change the invocation client in `invoke_foundry_workflow.py`

That separation makes it easier to see which logic belongs to Foundry and which logic belongs to your client code.

## What this lab demonstrates

1. Create Foundry agents that a workflow can invoke.
2. Define a native Foundry workflow in YAML.
3. Use workflow actions and workflow variables instead of a custom Python loop.
4. Invoke the workflow from Python and inspect streamed workflow events.
5. Keep the supporting agents and vector store available for later inspection and reuse.

## Expected result

The default script output shows a short transcript with the research agent message first and the supply agent message second.

If you run with `WORKFLOW_VERBOSE=true`, you will also see workflow actions and lower-level response events.

## Verification

- The workflow is saved successfully in Foundry.
- Both supporting agents exist in Foundry.
- The invocation script starts a conversation and runs the workflow.
- The final output reflects both web research and local grounding.
- The supporting agents and vector store remain available for later use.

## Additional resource note

This lab keeps the two supporting agents and the supply agent's vector store so the workflow can be invoked again without recreating its dependencies every time.

That vector store is reused on later runs, so reruns do not keep creating new indexes.

If you change `gear_notes.md` and want the index rebuilt, delete the existing workflow vector store in Foundry and run `prepare_workflow_agents.py` again.

## What you should see in Foundry

After you save `workflow.yaml`, you should see a real workflow in the Foundry `Workflows` tab.

You should also see the supporting agents created by `prepare_workflow_agents.py`, plus the vector store used by the supply agent.

## Why this matters

This lab shows the difference between invoking agents directly and building a platform-managed workflow that can coordinate those agents for you.

That is often the right middle ground when you want:

- a workflow visible in Foundry
- explicit workflow actions and variables
- a lightweight Python client that invokes the workflow instead of implementing it
