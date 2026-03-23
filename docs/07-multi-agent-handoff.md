# 07 Multi-Agent Handoff

## Goal

Show how two Foundry agents can work together on one task, with each agent owning a different responsibility and tool.

## Estimated time

20 to 25 minutes.

## Official references

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)
- [Microsoft Agent Framework overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)

## Recommendation

For this workshop, use a simple Python orchestrator with two Foundry prompt agents.

Why this approach:

1. It stays consistent with the rest of the workshop.
2. Participants can see the handoff clearly.
3. It avoids introducing Agent Framework workflows too early.

Use Agent Framework workflows later when you need explicit branching, retries, checkpoints, or more structured multi-agent routing.

## Scenario

One agent researches recent public guidance for a rainy spring hiking trip.

Another agent uses the local product notes from the RAG lab to recommend one product that fits those conditions.

## Exercise

Run:

```bash
python examples/06-multi-agent/two_agent_workflow.py
```

## Example files

- [Open two_agent_workflow.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/06-multi-agent/two_agent_workflow.py)
- [Open product_info.md on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/05-simple-rag/product_info.md)

## What this lab demonstrates

1. Create a research agent with `WebSearchTool`.
2. Create a product agent with `FileSearchTool`.
3. Run the first agent and capture its output.
4. Pass that output into the second agent as structured context.
5. Produce a final recommendation grounded in the product file.

## Expected result

The first agent returns short research notes.

The second agent uses those notes plus the uploaded product file to recommend one product and explain why it fits the scenario.

## Verification

- Both agents are created successfully.
- The research output is printed first.
- The final answer references the catalog information.
- Cleanup removes both agents and the vector store.

## When to use workflows instead

Use Agent Framework workflows when:

- the process has explicit steps and routing
- multiple agents must coordinate in a controlled order
- you need branching or retries
- you want durable state or human approval points

For this workshop, the handoff pattern is the right first step. It teaches multi-agent composition without forcing participants to learn a new orchestration framework immediately.