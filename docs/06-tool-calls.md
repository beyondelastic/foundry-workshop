# 06 Tool Calls

## Goal

Add one easy built-in tool to an agent and observe the agent choose that tool during response generation.

## Estimated time

10 to 15 minutes.

## Official references

- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [microsoft-foundry/foundry-samples](https://github.com/microsoft-foundry/foundry-samples)

## Why this lab matters

The earlier labs show plain model calls and prompt agents. This lab shows the next step: an agent can call a tool instead of answering only from its base model knowledge.

## Tool used in this example

This lab uses the built-in `WebSearchTool`, which is simpler than a full MCP approval flow and still demonstrates real tool usage through the agent.

## Exercise

Run:

```bash
python examples/05-tool-web-search/web_search_agent.py
```

By default, this script keeps the created agent so you can inspect and reuse it later in Foundry. Set `KEEP_AGENT=false` in your `.env` file if you want a disposable run.

## Example file

- [Open web_search_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/05-tool-web-search/web_search_agent.py)

```python title="examples/05-tool-web-search/web_search_agent.py"
import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    PromptAgentDefinition,
    WebSearchApproximateLocation,
    WebSearchTool,
)
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai import BadRequestError


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = name if not fallback else f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def get_keep_agent_setting() -> bool:
    value = os.getenv("KEEP_AGENT", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    keep_agent = get_keep_agent_setting()

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        tool = WebSearchTool(
            user_location=WebSearchApproximateLocation(
                country="GB",
                city="London",
                region="London",
            )
        )

        agent = project_client.agents.create_version(
            agent_name="WorkshopWebSearchAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a healthcare and life sciences research assistant. Use web "
                    "search when the user asks for recent or time-sensitive public "
                    "information."
                ),
                tools=[tool],
            ),
            description="Workshop example for simple built-in tool usage.",
        )
        print(f"Agent created: {agent.name} (version {agent.version})")

        try:
            conversation = openai_client.conversations.create()
            try:
                response = openai_client.responses.create(
                    conversation=conversation.id,
                    input=(
                        "Find one recent FDA page about clinical trial diversity or trial enrollment guidance. Give the title and one-sentence purpose."
                    ),
                    extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
                )
            except BadRequestError as exc:
                error_code = getattr(exc, "code", None)
                if error_code == "context_length_exceeded":
                    raise SystemExit(
                        "This tool example exceeded the selected model deployment's context window. Try the shorter default prompt in this sample, or switch AZURE_AI_MODEL_DEPLOYMENT_NAME to a larger-context model."
                    ) from exc
                raise

            used_web_search = any(
                getattr(item, "type", None) == "web_search_call"
                for item in response.output
            )

            print("\nTool-backed response:\n")
            print(response.output_text)
            print()
            print(f"Web search tool used: {used_web_search}")
        finally:
            if keep_agent:
                print(
                    f"\nAgent kept: {agent.name} (version {agent.version}). Set KEEP_AGENT=false to restore cleanup behavior."
                )
            else:
                project_client.agents.delete_version(
                    agent_name=agent.name,
                    agent_version=agent.version,
                )
                print("\nAgent deleted")


if __name__ == "__main__":
    main()
```

## What this lab demonstrates

1. Define a built-in tool in `PromptAgentDefinition`.
2. Create a new agent version with that tool.
3. Send a short prompt that should rely on web search.
4. Let the agent choose the built-in web search tool for a time-sensitive question.

## What is happening when you run it

The script creates a prompt agent version named `WorkshopWebSearchAgent`. That agent uses the same model deployment as the earlier labs, but it now includes a built-in `WebSearchTool` in its definition.

When the script sends the question through `responses.create(...)` with `agent_reference`, Foundry routes the request to that agent instead of calling the base model directly. The model sees the agent instructions, notices that the prompt asks for recent public information, and decides to call the web search tool.

The response payload includes both the final assistant message and structured items that describe what happened during execution. In this sample, the script checks `response.output` for any item with `type == "web_search_call"`. That is why the terminal can print `Web search tool used: True` even though the final text looks like a normal answer.

This is the main point of the lab: the agent still returns plain text to you, but under the hood it can call a tool and use that result to produce a grounded answer.

## Expected result

The response should return a recent public healthcare or life-sciences result from web search instead of relying only on the model's internal knowledge.

## Verification

- The script creates an agent successfully.
- The agent returns a grounded answer to the web query.
- The script reports that the web search tool was used.
- The agent remains available by default for later use in the Foundry UI.

## Why the sample keeps the agent

Keeping the agent is the default workshop behavior.

That makes it easier to inspect the agent in the Foundry UI and continue experimenting after the script finishes.

The script is still safe to rerun multiple times. Each rerun creates a new version under the same agent name, so participants can keep iterating without manually deleting the earlier one first.

If you want a clean, disposable run instead, set `KEEP_AGENT=false` and the script will delete the created agent version at the end.

## Common issue

- `context_length_exceeded`: smaller model deployments can hit their context window once the agent instructions, tool definitions, and your prompt are combined. This sample now uses a shorter query by default; if you still hit the limit, switch `AZURE_AI_MODEL_DEPLOYMENT_NAME` to a larger-context model.

## Extension idea

After this lab works, try keeping the agent and changing either the prompt or the instructions to see when the agent chooses web search and when it answers directly from the model.