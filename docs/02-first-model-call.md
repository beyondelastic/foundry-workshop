# 02 First Model Call

## Goal

Confirm your Foundry endpoint, authentication, and deployed model all work from Python.

## Estimated time

10 minutes.

## Official references

- [Microsoft Foundry get-started code quickstart](https://learn.microsoft.com/azure/foundry/quickstarts/get-started-code)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure SDK for Python responses samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/responses)

## Exercise

Run the example:

```bash
python examples/01-model-call/model_call.py
```

This example is using the Responses API. The script first connects to your Foundry project with `AIProjectClient`, then asks that project client for an OpenAI-compatible client, and finally sends a `responses.create(...)` call to your deployed model.

## Example file

- [Open model_call.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/01-model-call/model_call.py)

```python title="examples/01-model-call/model_call.py"
import os

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = f"{name}"
        if fallback:
            missing = f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    model_deployment_name = get_env(
        "AZURE_AI_MODEL_DEPLOYMENT_NAME", "MODEL_DEPLOYMENT_NAME"
    )

    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )
    openai = project.get_openai_client()

    response = openai.responses.create(
        model=model_deployment_name,
        input=(
            "List three common use cases for PCR in life sciences in one sentence each."
        ),
    )

    print("Model response:")
    print(response.output_text)


if __name__ == "__main__":
    main()
```

## What this lab demonstrates

1. Create an `AIProjectClient` with `DefaultAzureCredential`.
2. Get the OpenAI-compatible client from the project.
3. Send a `responses.create(...)` request.
4. Print the generated answer.

## What is happening under the hood

- `AZURE_AI_PROJECT_ENDPOINT` points to your Foundry project endpoint, not directly to a raw model endpoint.
- `AIProjectClient` handles the Foundry-side connection and authentication using `DefaultAzureCredential`.
- `project.get_openai_client()` returns an OpenAI-compatible client that can call model features exposed through your Foundry project.
- `responses.create(...)` sends your input prompt to the deployed model named in `AZURE_AI_MODEL_DEPLOYMENT_NAME`.
- `response.output_text` prints the final text returned by the model.

This is a useful first lab because it proves the full path is working: local Python environment, Azure authentication, Foundry project endpoint, deployed model, and the OpenAI-compatible Responses API surface.

## Expected result

You should see a short response describing common PCR use cases in life sciences.

## Verification

- The script runs without authentication errors.
- The script returns model output.
- The project endpoint in `.env` is valid.

## Common issues

- `DefaultAzureCredential failed to retrieve a token`: sign in again with `az login`.
- `404 Not Found`: check your project endpoint format.
- SDK mismatch errors: verify `azure-ai-projects>=2.0.0`.
