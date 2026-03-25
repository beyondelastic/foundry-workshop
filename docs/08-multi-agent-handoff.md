# 08 Two-Agent Orchestration

## Goal

Show how two Foundry agents can work together on one task through a simple Python orchestrator, with each agent owning a different responsibility and tool.

## Estimated time

20 to 25 minutes.

## Official references

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)
- [Microsoft Agent Framework overview](https://learn.microsoft.com/agent-framework/overview/agent-framework-overview)

## Recommended approach

Use a simple Python orchestrator with two Foundry prompt agents.

Why this approach:

1. It stays consistent with the rest of the workshop.
2. You can see the handoff clearly.
3. It avoids introducing Agent Framework workflows too early.
4. It demonstrates a valid multi-agent pattern even when you do not need a full workflow engine.

Use Agent Framework workflows later when you need explicit branching, retries, checkpoints, or more structured multi-agent routing.

## What this pattern really is

This lab uses an application-managed handoff.

That means the handoff is performed by your Python code, not by a built-in Foundry inter-agent routing feature. The first agent produces text output, the application captures that output, and the application passes it into the next agent as part of the next prompt.

So this is a valid multi-agent option, but it is intentionally the lightweight option. It is best for small, linear flows where you want to make the orchestration logic easy to read and easy to explain.

## Scenario

One agent researches recent public guidance for a rainy spring hiking trip.

Another agent uses the local product notes from the RAG lab to recommend one product that fits those conditions.

## Exercise

Run:

```bash
python examples/07-multi-agent/two_agent_workflow.py
```

By default, this script now keeps both agents and reuses the same supporting vector store on later reruns so participants can inspect them and continue experimenting in Foundry after the Python run finishes. To restore the older cleanup behavior for a one-off demo run, set `KEEP_AGENT=false` in your `.env` file.

## Example files

- [Open two_agent_workflow.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/07-multi-agent/two_agent_workflow.py)
- [Open product_info.md on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/06-simple-rag/product_info.md)

## What this lab demonstrates

1. Create a research agent with `WebSearchTool`.
2. Create a product agent with `FileSearchTool`.
3. Run the first agent and capture its output.
4. Pass that output into the second agent as structured context.
5. Produce a final recommendation grounded in the product file.

## How the handoff works

The script creates two separate prompt agents.

The first agent is the research agent. It has `WebSearchTool`, so it can gather recent public guidance for the trip scenario. The helper function `run_agent(...)` invokes that agent by creating a conversation and sending a prompt through `responses.create(...)` with `agent_reference`.

The returned text from that first run is stored in `research_notes`. That text is the handoff payload.

The script then invokes the second agent, the product agent. This time the Python code includes the earlier `research_notes` directly in the second prompt under a `Research notes:` section. The second agent also has access to `FileSearchTool`, so it can combine the handed-off notes with retrieved catalog content from the uploaded product file.

In other words, the handoff is not agent A directly calling agent B. The handoff is:

1. agent A produces text
2. Python captures that text
3. Python injects that text into agent B's prompt

That is why this lab is a good introduction to multi-agent composition. It shows the coordination pattern clearly before you move to more structured workflow approaches.

## Expected result

The first agent returns short research notes.

The second agent uses those notes plus the uploaded product file to recommend one product and explain why it fits the scenario.

## Verification

- Both agents are created successfully.
- The research output is printed first.
- The final answer references the catalog information.
- Both agents and the vector store remain available by default for later use.

## Why the sample now keeps the resources

Keeping the agents is the better default for workshop participants because the Foundry UI is part of the learning flow. Participants can inspect both agents after the run, compare their instructions and tools, and continue using them without rerunning the full script immediately.

The same applies to the vector store used by the product agent. If the agent stayed but the vector store were deleted, the saved agent would no longer be useful for the grounded recommendation step.

The script is still safe to rerun multiple times. The product vector store is created once and then reused on later runs, while agent creation still uses versioning so participants can iterate without first deleting earlier agent versions.

If you update `product_info.md` and want the grounded data refreshed, delete the existing workshop vector store in Foundry and rerun the script.

If you want the older disposable behavior for a clean demo run, set `KEEP_AGENT=false` and the script will delete both agent versions and the vector store at the end.

## When to use workflows instead

Use Agent Framework workflows when:

- the process has explicit steps and routing
- multiple agents must coordinate in a controlled order
- you need branching or retries
- you want durable state or human approval points

In this workshop, the handoff pattern is the right first step. It teaches multi-agent composition without forcing you to learn a new orchestration framework immediately.

## Why you do not see a Foundry workflow

That is expected in this workshop.

The multi-agent and YAML labs use Python to orchestrate prompt agents, but they do not create native Foundry workflow resources. The YAML lab is declarative in your source files, not in the Foundry portal's workflow system, so you will see agents, files, and indexes in the UI but no workflow entry.