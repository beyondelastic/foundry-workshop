# 09 Native Foundry Workflow

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
