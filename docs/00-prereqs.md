# 00 Prerequisites

## Goal

Make sure you can start the hands-on labs without hidden setup gaps.

## Estimated time

10 to 15 minutes if the Azure resources already exist.

## Official references

- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Microsoft Foundry portal](https://ai.azure.com/)

## Checklist

- This repository is cloned locally, or you have forked it and cloned your fork, so the example files are available on your machine.
- Azure subscription is active.
- Azure CLI is installed and `az login` works.
- Python 3.10 or newer is installed.
- You have an existing Foundry project or permission to create one.
- You have a role such as `Azure AI User` on the project.

## Verify locally

```bash
python --version
az version
az account show
```

## Environment variables used in this workshop

Primary names:

- `AZURE_AI_PROJECT_ENDPOINT`
- `AZURE_AI_MODEL_DEPLOYMENT_NAME`
- `AZURE_AI_AGENT_NAME`

Fallback names accepted by the example code:

- `PROJECT_ENDPOINT`
- `MODEL_DEPLOYMENT_NAME`
- `AGENT_NAME`

## Success criteria

You are ready to continue when:

- Azure CLI can show your account
- you know your project endpoint
- you know the name of a deployed model
