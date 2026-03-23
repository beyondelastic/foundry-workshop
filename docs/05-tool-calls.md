# 05 Tool Calls

## Goal

Add one easy built-in tool to an agent and force the model to use it during response generation.

## Estimated time

10 to 15 minutes.

## Official references

- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [microsoft-foundry/foundry-samples](https://github.com/microsoft-foundry/foundry-samples)

## Why this lab exists

The earlier labs show plain model calls and prompt agents. This lab shows the next step: an agent can call a tool instead of answering only from its base model knowledge.

## Tool used in this example

This lab uses the built-in `WebSearchTool`, which is simpler than a full MCP approval flow and still demonstrates real tool usage through the agent.

## Exercise

Run:

```bash
python examples/04-tool-web-search/web_search_agent.py
```

## Example file

- [Open web_search_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/04-tool-web-search/web_search_agent.py)

## What this lab demonstrates

1. Define a built-in tool in `PromptAgentDefinition`.
2. Create a new agent version with that tool.
3. Send a prompt that should rely on web search.
4. Force tool usage with `tool_choice="required"`.

## Expected result

The response should summarize recent public web information instead of relying only on the model's internal knowledge.

## Verification

- The script creates an agent successfully.
- The agent returns a grounded answer to the web query.
- The example cleans up the agent version afterward.

## Extension idea

After this lab works, compare the same question with and without `tool_choice="required"` to see how tool use changes the answer path.