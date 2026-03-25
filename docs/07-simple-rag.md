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