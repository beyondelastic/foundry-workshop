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

By default, this script now keeps the created agent so participants can inspect and reuse it later in Foundry. To restore the older cleanup behavior for a one-off demo run, set `KEEP_AGENT=false` in your `.env` file.

## Example file

- [Open web_search_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/05-tool-web-search/web_search_agent.py)

## What this lab demonstrates

1. Define a built-in tool in `PromptAgentDefinition`.
2. Create a new agent version with that tool.
3. Send a short prompt that should rely on web search.
4. Let the agent choose the built-in web search tool for a time-sensitive question.

## What is happening when you run it

The script creates a prompt agent version named `WorkshopWebSearchAgent`. That agent uses the same model deployment as the earlier labs, but it now includes a built-in `WebSearchTool` in its definition.

When the script sends the question through `responses.create(...)` with `agent_reference`, Foundry routes the request to that agent instead of calling the base model directly. The model sees the agent instructions, notices that the prompt asks for recent public information, and decides to call the web search tool.

The response payload includes both the final assistant message and structured items that describe what happened during execution. In this sample, the script checks `response.output` for any item with `type == "web_search_call"`. That is why the terminal can print `Web search tool used: True` even though the final text looks like a normal answer.

This is the main concept the page is trying to show: the agent still returns plain text to the user, but under the hood it can take an extra step, call a tool, and then use the tool result to produce a grounded answer.

## Expected result

The response should return a recent public result from web search instead of relying only on the model's internal knowledge.

## Verification

- The script creates an agent successfully.
- The agent returns a grounded answer to the web query.
- The script reports that the web search tool was used.
- The agent remains available by default for later use in the Foundry UI.

## Why the sample keeps the agent

Keeping the agent is now the default workshop behavior.

That makes it easier for participants to inspect the agent in the Foundry UI and continue experimenting after the script finishes.

The script is still safe to rerun multiple times. Each rerun creates a new version under the same agent name, so participants can keep iterating without manually deleting the earlier one first.

If you want a clean, disposable run instead, set `KEEP_AGENT=false` and the script will delete the created agent version at the end.

## Common issue

- `context_length_exceeded`: smaller model deployments can hit their context window once the agent instructions, tool definitions, and your prompt are combined. This sample now uses a shorter query by default; if you still hit the limit, switch `AZURE_AI_MODEL_DEPLOYMENT_NAME` to a larger-context model.

## Extension idea

After this lab works, try keeping the agent and changing either the prompt or the instructions to see when the agent chooses web search and when it answers directly from the model.