# Setup

This workshop assumes you have an Azure subscription and permission to use Microsoft Foundry.

## 1. Azure prerequisites

Before you begin, verify:

- Your Azure subscription is active.
- You can sign in with `az login`.
- You have a role such as `Azure AI User` on the Foundry project.
- You already have, or can create, a Foundry resource and project.

Official references:

- Microsoft Foundry resource quickstart
- Microsoft Foundry SDK overview for Python

## 2. Local prerequisites

- Python 3.10 or later
- Azure CLI 2.67.0 or later
- A deployed model in your Foundry project

## 3. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

## 4. Authenticate

```bash
az login
az account show
```

## 5. Configure environment variables

Copy the template and fill in your values:

```bash
cp .env.example .env
```

Required values:

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- `AZURE_AI_AGENT_NAME`

Recommended optional value:

- `KEEP_AGENT=true`

The workshop examples also accept these fallback names because Microsoft docs use them in some quickstarts:

- `PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`
- `AGENT_NAME`

`KEEP_AGENT` controls whether the workshop examples that create agents and related vector stores keep them after the script finishes. The default workshop behavior is `true` so participants can inspect and reuse the created resources in Foundry. Set `KEEP_AGENT=false` when you want disposable demo runs instead.

## 6. Start the workshop UI

```bash
mkdocs serve
```

## 7. Suggested workshop order

1. Read `docs/00-prereqs.md`
2. Complete `docs/01-create-foundry-resources.md`
3. Run `examples/01-model-call/model_call.py`
4. Run `examples/02-agent-chat/create_agent.py`
5. Run `examples/02-agent-chat/chat_with_agent.py`
6. Run `examples/03-agent-eval/evaluate_agent.py`
7. Run `examples/04-observability/traced_model_call.py`
8. Run `examples/05-tool-web-search/web_search_agent.py`
9. Run `examples/06-simple-rag/file_search_rag.py`
10. Run `examples/07-multi-agent/two_agent_workflow.py`
11. Run `examples/08-declarative-yaml/prepare_workflow_agents.py`
12. Create the workflow in Foundry from `examples/08-declarative-yaml/workflow.yaml`
13. Run `examples/08-declarative-yaml/invoke_foundry_workflow.py`

## 8. Notes for the new labs

The tool-call lab uses the built-in `WebSearchTool` so participants can see real tool usage without first configuring a separate MCP server.

The simple RAG lab uses `FileSearchTool` with one local markdown file uploaded into a vector store. This keeps the retrieval pattern self-contained and easy to run in a workshop.

## Troubleshooting

If `DefaultAzureCredential` cannot get a token:

1. Run `az login` again.
2. Verify your role assignment on the Foundry project.
3. Confirm your project endpoint matches the format from the Foundry portal.

If example code fails with SDK errors:

1. Check `pip show azure-ai-projects`.
2. Ensure you are using the new Foundry docs and not Foundry classic samples.
