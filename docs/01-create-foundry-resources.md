# 01 Create Foundry Resources

## Goal

Create the Azure resource group, Foundry resource, Foundry project, and a starter model deployment.

## Estimated time

15 to 25 minutes.

## Official references

- [Microsoft Foundry portal](https://ai.azure.com/)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure AI Agents quickstart](https://learn.microsoft.com/azure/ai-services/agents/quickstart?context=/azure/ai-foundry/context/context)

## What you will do

1. Create or choose a resource group.
2. Create a Foundry resource with project management enabled.
3. Create a Foundry project.
4. Deploy a small starter model.
5. Copy the project endpoint from the Foundry portal.

## Azure CLI flow

The official quickstart uses a flow similar to this:

```bash
az group create --name my-foundry-rg --location eastus

az cognitiveservices account create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --kind AIServices \
  --sku s0 \
  --location eastus \
  --allow-project-management

az cognitiveservices account update \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --custom-domain my-foundry-resource

az cognitiveservices account project create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --project-name my-foundry-project \
  --location eastus
```

## Deploy a model

The official quickstart example uses `gpt-4.1-mini`. You can also choose another supported model available in your region.

```bash
az cognitiveservices account deployment create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --deployment-name gpt-4.1-mini \
  --model-name gpt-4.1-mini \
  --model-version "2025-04-14" \
  --model-format OpenAI \
  --sku-capacity 10 \
  --sku-name Standard
```

## Capture connection details

In the Foundry portal, copy:

- your project endpoint
- your deployed model name

Put those values into `.env`.

## Verification

- The project appears in the Foundry portal.
- The model deployment shows a healthy provisioning state.
- Your `.env` file has the correct endpoint and model deployment name.
