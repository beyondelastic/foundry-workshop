# 06 Simple RAG

## Goal

Build a small retrieval-augmented generation flow by grounding an agent on a local markdown file uploaded to a vector store.

## Estimated time

15 to 20 minutes.

## Official references

- [Azure SDK for Python file and agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure AI Search classic generative search (RAG) overview](https://learn.microsoft.com/azure/search/retrieval-augmented-generation-overview)

## Why this lab uses file search

This is the lightest useful RAG example for the workshop. It stays within the Foundry project, uploads one local file, creates a vector store, and lets the agent retrieve from that content.

## Exercise

Run:

```bash
python examples/05-simple-rag/file_search_rag.py
```

## Example files

- [Open file_search_rag.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/05-simple-rag/file_search_rag.py)
- [Open product_info.md on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/05-simple-rag/product_info.md)

## What this lab demonstrates

1. Create a vector store.
2. Upload a local markdown file.
3. Attach `FileSearchTool` to a prompt agent.
4. Ask questions that require grounded retrieval from the uploaded content.

## Expected result

The agent should answer questions using the uploaded document rather than general model knowledge.

## Verification

- The vector store is created.
- The file upload completes successfully.
- The agent answers questions about the local document.
- Cleanup removes the agent version and vector store.

## RAG discussion point

This is still a real RAG pattern, even though it is small. Retrieval fetches relevant chunks from the vector store, and generation turns that retrieved content into a final answer.