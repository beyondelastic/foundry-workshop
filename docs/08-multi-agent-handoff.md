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

One agent researches recent public guidance for a mobile vaccination clinic.

Another agent uses the local clinical supply notes from the RAG lab to recommend one item that fits those conditions.

## Exercise

Run:

```bash
python examples/07-multi-agent/two_agent_workflow.py
```

By default, this script keeps both agents and reuses the same supporting vector store on later reruns so you can inspect them and continue experimenting in Foundry after the Python run finishes. Set `KEEP_AGENT=false` in your `.env` file if you want a disposable run.

## Example files

- [Open two_agent_workflow.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/07-multi-agent/two_agent_workflow.py)
- [Open product_info.md on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/06-simple-rag/product_info.md)

This lab reuses the `product_info.md` clinical supply catalog shown in [07 Simple RAG](07-simple-rag.md).

```python title="examples/07-multi-agent/two_agent_workflow.py"
import os
from pathlib import Path

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


def get_keep_agent_setting() -> bool:
    value = os.getenv("KEEP_AGENT", "true").strip().lower()
    return value not in {"0", "false", "no", "off"}


def get_or_create_vector_store(openai_client, store_name: str, file_path: Path):
    for vector_store in openai_client.vector_stores.list(limit=100, order="desc"):
        if vector_store.name == store_name:
            print(f"Vector store reused: {vector_store.id}")
            return vector_store, False

    vector_store = openai_client.vector_stores.create(name=store_name)
    print(f"Vector store created: {vector_store.id}")

    with file_path.open("rb") as file_handle:
        openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=file_handle,
        )

    return vector_store, True


def run_agent(openai_client, agent_name: str, prompt: str) -> str:
    conversation = openai_client.conversations.create()
    response = openai_client.responses.create(
        conversation=conversation.id,
        input=prompt,
        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
    )
    return response.output_text


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    keep_agent = get_keep_agent_setting()
    product_file_path = (
        Path(__file__).resolve().parents[1] / "06-simple-rag" / "product_info.md"
    )
    vector_store_name = "WorkshopMultiAgentStore"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        vector_store, created_vector_store = get_or_create_vector_store(
            openai_client,
            vector_store_name,
            product_file_path,
        )

        research_agent = project_client.agents.create_version(
            agent_name="WorkshopResearchAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a healthcare operations research assistant. Use web search "
                    "to gather short, current public guidance for vaccine handling or "
                    "mobile vaccination clinic operations. Return only three concise bullets."
                ),
                tools=[
                    WebSearchTool(
                        user_location=WebSearchApproximateLocation(
                            country="GB",
                            city="London",
                            region="London",
                        )
                    )
                ],
            ),
            description="Research agent for workshop multi-agent handoff lab.",
        )

        product_agent = project_client.agents.create_version(
            agent_name="WorkshopSupplyAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a clinical supply recommendation assistant. Use the "
                    "uploaded supply notes to recommend one item. Base the "
                    "recommendation on the user scenario and the research notes you receive."
                ),
                tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
            ),
            description="Supply agent for workshop multi-agent handoff lab.",
        )

        try:
            scenario = (
                "A community health team is planning a one-day mobile vaccination clinic in the UK and wants one supply recommendation from the catalog."
            )

            research_notes = run_agent(
                openai_client,
                research_agent.name,
                (
                    f"Scenario: {scenario}\n"
                    "Find recent public guidance for what matters most for this type of clinic. Return exactly three bullets."
                ),
            )

            print("Research agent output:\n")
            print(research_notes)

            final_recommendation = run_agent(
                openai_client,
                product_agent.name,
                (
                    f"Scenario: {scenario}\n\n"
                    f"Research notes:\n{research_notes}\n\n"
                    "Using the uploaded clinical supply notes, recommend exactly one item. Explain why it fits in 3 to 4 bullets."
                ),
            )

            print("\nSupply agent output:\n")
            print(final_recommendation)
        finally:
            if keep_agent:
                print(
                    f"\nAgents kept: {research_agent.name} (version {research_agent.version}), {product_agent.name} (version {product_agent.version})"
                )
                print(
                    f"Vector store kept: {vector_store.id}. Set KEEP_AGENT=false to restore cleanup behavior."
                )
            else:
                project_client.agents.delete_version(
                    agent_name=research_agent.name,
                    agent_version=research_agent.version,
                )
                project_client.agents.delete_version(
                    agent_name=product_agent.name,
                    agent_version=product_agent.version,
                )
                if created_vector_store:
                    openai_client.vector_stores.delete(vector_store.id)


if __name__ == "__main__":
    main()
```

## What this lab demonstrates

1. Create a research agent with `WebSearchTool`.
2. Create a product agent with `FileSearchTool`.
3. Run the first agent and capture its output.
4. Pass that output into the second agent as structured context.
5. Produce a final recommendation grounded in the clinical supply file.

## How the handoff works

The script creates two separate prompt agents.

The first agent is the research agent. It has `WebSearchTool`, so it can gather recent public guidance for the clinic scenario. The helper function `run_agent(...)` invokes that agent by creating a conversation and sending a prompt through `responses.create(...)` with `agent_reference`.

The returned text from that first run is stored in `research_notes`. That text is the handoff payload.

The script then invokes the second agent, the supply agent. This time the Python code includes the earlier `research_notes` directly in the second prompt under a `Research notes:` section. The second agent also has access to `FileSearchTool`, so it can combine the handed-off notes with retrieved catalog content from the uploaded clinical supply file.

In other words, the handoff is not agent A directly calling agent B. The handoff is:

1. agent A produces text
2. Python captures that text
3. Python injects that text into agent B's prompt

That is why this lab is a good introduction to multi-agent composition. It shows the coordination pattern clearly before you move to more structured workflow approaches.

## Expected result

The first agent returns short research notes.

The second agent uses those notes plus the uploaded clinical supply file to recommend one item and explain why it fits the scenario.

## Verification

- Both agents are created successfully.
- The research output is printed first.
- The final answer references the catalog information.
- Both agents and the vector store remain available by default for later use.

## Additional resource note

This lab keeps two agents instead of one, plus the supporting clinical supply vector store used by the second agent.

That vector store is reused on later runs, so reruns do not keep creating new indexes.

If you update `product_info.md` and want the grounded data refreshed, delete the existing workshop vector store in Foundry and rerun the script.

## When to use workflows instead

Use Agent Framework workflows when:

- the process has explicit steps and routing
- multiple agents must coordinate in a controlled order
- you need branching or retries
- you want durable state or human approval points

In this workshop, the handoff pattern is the right first step. It teaches multi-agent composition without forcing you to learn a new orchestration framework immediately.

## How this differs from the next lab

This lab uses Python to coordinate the handoff between two agents. You can read the orchestration directly in the script, which makes the flow easy to follow.

In the next lab, Foundry owns the orchestration through a native workflow resource. That gives you a useful contrast between application-managed orchestration and platform-managed orchestration.