# 09 Declarative YAML Workflow

## Goal

Define two agents and a simple workflow in YAML, then execute that declarative definition through Python code that uses only Foundry SDK APIs.

## Estimated time

20 to 30 minutes.

## Official references

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Microsoft Foundry get-started code quickstart](https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code)
- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)
- [microsoft-foundry/foundry-samples](https://github.com/microsoft-foundry/foundry-samples)

## What this lab is and is not

This lab uses YAML as a declarative configuration format.

It does **not** rely on Microsoft Agent Framework.

It also does **not** assume that the Foundry SDK natively executes YAML workflow files.

Instead, the pattern is:

1. YAML defines the agents and workflow steps.
2. Python loads that YAML.
3. Python provisions and invokes Foundry agents through `AIProjectClient` and the OpenAI-compatible client.

This is a clean Foundry-only way to keep workflow intent declarative without introducing another orchestration framework.

## Scenario

One agent researches what matters for a rainy spring city break.

Another agent uses a local gear catalog to recommend exactly one item.

The workflow is declared in YAML and executed step by step by a small Python runtime.

## Exercise

Run:

```bash
python examples/08-declarative-yaml/run_workflow_from_yaml.py
```

## Example files

- [Open agents.yaml on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/agents.yaml)
- [Open workflow.yaml on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/workflow.yaml)
- [Open run_workflow_from_yaml.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/run_workflow_from_yaml.py)
- [Open yaml_runtime.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/yaml_runtime.py)
- [Open gear_notes.md on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/08-declarative-yaml/gear_notes.md)

## What this lab demonstrates

1. Declare agent roles and tools in YAML.
2. Declare workflow steps and prompt handoffs in YAML.
3. Load that configuration in Python.
4. Create Foundry prompt agents from the YAML definitions.
5. Execute each workflow step in order.
6. Clean up the temporary agents and vector stores.

## Expected result

The first step prints research notes.

The second step prints a final gear recommendation grounded in the local catalog.

## Verification

- YAML loads successfully.
- Both agents are created.
- The workflow runner prints each step output.
- The final output reflects both web research and local grounding.
- Cleanup completes successfully.

## Why this matters

This lab shows how declarative configuration can fit into a Foundry-first architecture even when the orchestration runtime is still plain Python.

That is often the right middle ground when you want:

- YAML for readability and review
- Foundry APIs for execution
- no dependency on Agent Framework
