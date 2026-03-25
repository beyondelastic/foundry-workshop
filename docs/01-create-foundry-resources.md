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

If `az cognitiveservices account create` reports `unrecognized arguments: --allow-project-management`, your Azure CLI is too old for this flow. Run `az upgrade` and retry.

- Create the resource group that will contain the Foundry resources.

```bash
az group create --name my-foundry-rg --location swedencentral
```

- Create the Azure AI Services resource that backs the Foundry account and enables project management.

```bash

az cognitiveservices account create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --kind AIServices \
  --sku s0 \
  --location swedencentral \
  --allow-project-management
```

- Assign a stable custom subdomain for the Azure AI resource endpoint.

```bash

az cognitiveservices account update \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --custom-domain my-foundry-resource
```

- Create the Foundry project inside the Azure AI resource.

```bash

az cognitiveservices account project create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --project-name my-foundry-project \
  --location swedencentral
```

If you create everything in the Foundry portal and only plan to copy the project endpoint from the portal, you can usually skip the custom-domain step. It is included here because it matches the official CLI setup pattern and gives the Azure AI resource a stable endpoint that is also useful in SDK and API flows.

## Deploy a model

The official quickstart example uses `gpt-4.1-mini`. You can also choose another supported model available in your region.

- Deploy a starter model that the workshop scripts can call.

```bash
az cognitiveservices account deployment create \
  --name my-foundry-resource \
  --resource-group my-foundry-rg \
  --deployment-name gpt-4.1-mini \
  --model-name gpt-4.1-mini \
  --model-version "2025-04-14" \
  --model-format OpenAI \
  --sku-capacity 30 \
  --sku-name Standard
```

`--sku-capacity 30` sets a larger starter throughput allocation for the workshop so participants have more headroom for repeated runs and multi-step agent examples.

If your available quota is small, you can lower this value. If you expect several participants to share one deployment or to rerun the later labs quickly, increase it further as your region quota allows.

## Capture connection details

In the Foundry portal, copy:

You can find the project endpoint by clicking `Home` in Foundry, then opening your project where the endpoint is shown for SDK and API usage.

- your project endpoint
- your deployed model name

Put those values into `.env`.

## Verification

- The project appears in the Foundry portal.
- The model deployment shows a healthy provisioning state.
- Your `.env` file has the correct endpoint and model deployment name.
