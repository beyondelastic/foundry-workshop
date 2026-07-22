# 07 Simple RAG

## Goal

Build a small retrieval-augmented generation flow by grounding an agent on a local markdown file uploaded to a vector store.

## Estimated time

15 to 20 minutes.

## Official references

- [Azure SDK for Python file and agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure AI Search classic generative search (RAG) overview](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)

## Why file search is used here

This is the lightest useful RAG example in this workshop. It stays within the Foundry project, uploads one local file, creates a vector store, and lets the agent retrieve from that content.

## Exercise

Run:

```bash
python examples/06-simple-rag/file_search_rag.py
```

By default, this script keeps the created agent and reuses the same workshop vector store on later reruns, so you can inspect the setup and continue using the agent later in Foundry. Set `KEEP_AGENT=false` in your `.env` file if you want a disposable run.

## Example files

- [Open file_search_rag.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/06-simple-rag/file_search_rag.py)
- [Open product_info.md on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/06-simple-rag/product_info.md)

```python title="examples/06-simple-rag/file_search_rag.py"
import os
from pathlib import Path

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import FileSearchTool, PromptAgentDefinition
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
        uploaded_file = openai_client.vector_stores.files.upload_and_poll(
            vector_store_id=vector_store.id,
            file=file_handle,
        )
    print(f"File uploaded: {uploaded_file.id}")

    return vector_store, True


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )
    asset_file_path = Path(__file__).with_name("product_info.md")
    keep_agent = get_keep_agent_setting()
    vector_store_name = "WorkshopClinicalSupplyStore"

    with (
        DefaultAzureCredential() as credential,
        AIProjectClient(endpoint=project_endpoint, credential=credential) as project_client,
        project_client.get_openai_client() as openai_client,
    ):
        vector_store, created_vector_store = get_or_create_vector_store(
            openai_client,
            vector_store_name,
            asset_file_path,
        )

        agent = project_client.agents.create_version(
            agent_name="WorkshopFileSearchAgent",
            definition=PromptAgentDefinition(
                model=model_deployment_name,
                instructions=(
                    "You are a healthcare operations assistant that answers from the "
                    "uploaded clinical supply notes whenever the question can be "
                    "answered from that document."
                ),
                tools=[FileSearchTool(vector_store_ids=[vector_store.id])],
            ),
            description="Workshop example for simple file-search RAG.",
        )
        print(f"Agent created: {agent.name} (version {agent.version})")

        try:
            conversation = openai_client.conversations.create()
            response = openai_client.responses.create(
                conversation=conversation.id,
                input=(
                    "Which item is best for transporting refrigerated vaccine doses, and what temperature range does it support?"
                ),
                extra_body={"agent_reference": {"name": agent.name, "type": "agent_reference"}},
            )

            print("\nRAG response:\n")
            print(response.output_text)
        finally:
            if keep_agent:
                print(
                    f"\nAgent kept: {agent.name} (version {agent.version})"
                )
                print(
                    f"Vector store kept: {vector_store.id}. Set KEEP_AGENT=false to restore cleanup behavior."
                )
            else:
                project_client.agents.delete_version(
                    agent_name=agent.name,
                    agent_version=agent.version,
                )
                print("\nAgent deleted")
                if created_vector_store:
                    openai_client.vector_stores.delete(vector_store.id)
                    print("Vector store deleted")


if __name__ == "__main__":
    main()
```

```markdown title="examples/06-simple-rag/product_info.md"
# Contoso Clinical Supply Notes

## ColdChain Transit Case

- Price: $329
- Temperature range: 2 C to 8 C for up to 12 hours
- Best use: transporting refrigerated vaccine doses between care sites
- Notable feature: validated cold-chain hold with tamper-evident latch

## Specimen Transport Kit

- Price: $94
- Capacity: 12 sample containers
- Best use: routine blood and swab specimen pickup from outpatient clinics
- Notable feature: absorbent lining, UN3373 labeling area, and tamper-evident seal

## Mobile Consent Tablet

- Price: $449
- Battery life: 10 hours
- Best use: digital patient intake and research consent capture
- Notable feature: encrypted form storage with stylus support

## Sharps Safety Station

- Price: $58
- Capacity: 5 liters
- Best use: temporary vaccination and phlebotomy stations
- Notable feature: portable container with lockable lid and integrated tray
```

## What this lab demonstrates

1. Create or reuse a vector store.
2. Upload a local markdown file.
3. Attach `FileSearchTool` to a prompt agent.
4. Ask questions that require grounded retrieval from the uploaded content.

## What is happening when you run it

The script first creates a vector store inside your Foundry-backed OpenAI project. You can think of that vector store as the retrieval index for this example. It is the place where the uploaded document will be stored and prepared for semantic lookup.

Next, the script uploads `product_info.md` into that vector store by calling `upload_and_poll(...)`. The important detail here is the `and_poll` part: the script waits until Foundry finishes processing and indexing the file before moving on. That avoids a common timing problem where the agent is created successfully, but retrieval fails because the document is not ready yet.

After the file is indexed, the script creates a prompt agent and gives it a `FileSearchTool` that points at the vector store ID. This is the key RAG step. The model is still the same deployed model you used in earlier labs, but now the agent has access to a retrieval tool that can search the uploaded document for relevant content before answering.

When the script sends the vaccine cold-chain question through `responses.create(...)` with `agent_reference`, Foundry routes the request to that file-search agent instead of directly to the base model. The agent reads the question, decides the answer should come from the uploaded notes, retrieves the relevant chunk or chunks from the vector store, and then uses that retrieved context to generate the final answer.

That is why this counts as retrieval-augmented generation rather than just prompt engineering. The answer is not only based on the model's general training data. It is augmented with retrieved content from `product_info.md`, which makes the answer grounded in the uploaded document.

In this sample, the retrieval source is intentionally small and local so the moving parts stay easy to follow. The same pattern scales outward: in a larger system, the vector store might contain many documents, but the flow is still the same sequence of indexing content, retrieving relevant chunks, and generating an answer from them.

## What a vector store means here

Even in this lightweight option, there is still an embedding-style retrieval step happening behind the scenes. You do not explicitly choose or call an embedding model in this sample, but the platform still has to transform the uploaded file into a searchable representation so semantic retrieval can work.

That is one reason this feels simpler than building a full Azure AI Search pipeline. With `vector_stores.create(...)` and `upload_and_poll(...)`, Foundry handles the document ingestion and retrieval plumbing for you. You do not manage a separate search service, define an index schema, configure chunking and vector fields yourself, or wire up a separate embedding deployment in the sample code.

Compared with Azure AI Search, this approach is easier to teach and faster to get running, but it is also less explicit and less configurable. Azure AI Search is the better fit when you want richer indexing control, hybrid retrieval, filters, ranking tuning, more advanced content pipelines, or a retrieval system shared across multiple applications. The vector store approach is best when you want the lightest path to grounded retrieval inside a Foundry-based agent workflow.

## Expected result

The agent should answer questions using the uploaded document rather than general model knowledge.

## Verification

- The vector store is created on the first run and reused on later runs.
- The file upload completes successfully.
- The agent answers questions about the local document.
- The agent and its vector store remain available by default for later use.

## Additional resource note

This lab keeps one extra resource beyond the agent introduced in the previous lab: the workshop vector store used for file search.

That vector store is created on the first run and reused on later runs, so reruns do not keep creating new indexes.

If you change `product_info.md` and want the grounded data rebuilt, delete the existing workshop vector store in Foundry and run the script again.

## Why this counts as RAG

This is still a real RAG pattern, even though it is small. Retrieval fetches relevant chunks from the vector store, and generation turns that retrieved content into a final answer.