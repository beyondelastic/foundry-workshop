# Microsoft Foundry Workshop

This repository is a beginner-friendly Microsoft Foundry workshop built around official Microsoft Learn guidance and official samples.

The examples use lightweight healthcare and life sciences scenarios so the workshop stays consistent across model calls, agents, evaluation, RAG, and workflow labs.

GitHub repository: [beyondelastic/foundry-workshop](https://github.com/beyondelastic/foundry-workshop)

## What this workshop covers

1. Prepare your environment and verify Azure prerequisites.
2. Create Microsoft Foundry resources and deploy a model.
3. Make your first Python SDK model call.
4. Create a prompt agent and have a multi-turn conversation.
5. Evaluate that agent with a small dataset.
6. Add basic observability with OpenTelemetry and view traces in Foundry.
7. Use a built-in tool from a prompt agent.
8. Build a simple RAG flow with file search.
9. Coordinate two agents through a simple Python-managed handoff.
10. Create a native Foundry workflow and invoke it from Python.

## Design goals

- Keep the flow easy to follow.
- Favor official documentation over custom theory.
- Keep examples short and runnable.
- Use a lightweight docs-first web UI.

## Official sources used

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Microsoft Foundry get-started code quickstart](https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code)
- [Azure AI Agents quickstart](https://learn.microsoft.com/azure/ai-services/agents/quickstart?context=/azure/ai-foundry/context/context)
- [Microsoft Foundry cloud evaluation guidance](https://learn.microsoft.com/azure/foundry/how-to/develop/cloud-evaluation)
- [microsoft-foundry/foundry-samples](https://github.com/microsoft-foundry/foundry-samples)
- [Azure SDK for Python samples for azure-ai-projects](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples)

## Repository layout

```text
.
├── docs/
├── examples/
├── mkdocs.yml
├── requirements.txt
└── SETUP.md
```

## Quick start

1. Create a Python virtual environment.
2. Install dependencies.
3. Sign in to Azure.
4. Copy `.env.example` to `.env` and fill in your project values.
5. Start the docs UI with `mkdocs serve`.

Detailed steps are in `SETUP.md`.

If you run the native workflow lab, save the workflow in Foundry with the default name `Workshop-Clinical-Operations-Workflow` or set `AZURE_AI_WORKFLOW_NAME` in `.env` to match the name you chose.

## Run the workshop UI

```bash
mkdocs serve
```

Then open the local URL shown in the terminal, usually `http://127.0.0.1:8000`.

## Run the examples

```bash
python examples/01-model-call/model_call.py
python examples/02-agent-chat/create_agent.py
python examples/02-agent-chat/chat_with_agent.py
python examples/03-agent-eval/evaluate_agent.py
python examples/04-observability/traced_model_call.py
python examples/05-tool-web-search/web_search_agent.py
python examples/06-simple-rag/file_search_rag.py
python examples/07-multi-agent/two_agent_workflow.py
python examples/08-declarative-yaml/prepare_workflow_agents.py
python examples/08-declarative-yaml/invoke_foundry_workflow.py
```

## SDK note

This workshop targets `azure-ai-projects>=2.0.0`. If you run into SDK-shape mismatches, first confirm your installed version with `pip show azure-ai-projects`.
