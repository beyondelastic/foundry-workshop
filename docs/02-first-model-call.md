# 02 First Model Call

## Goal

Confirm your Foundry endpoint, authentication, and deployed model all work from Python.

## Estimated time

10 minutes.

## Official references

- Microsoft Foundry quickstart: chat with a model
- Python sample: `samples/python/quickstart/responses/quickstart-responses.py`

## Exercise

Run the example:

```bash
python examples/01-model-call/model_call.py
```

## Example file

- [Open model_call.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/01-model-call/model_call.py)

## What this script demonstrates

1. Create an `AIProjectClient` with `DefaultAzureCredential`.
2. Get the OpenAI-compatible client from the project.
3. Send a `responses.create(...)` request.
4. Print the generated answer.

## Expected result

You should see a response to the prompt about France.

## Verification

- The script runs without authentication errors.
- The script returns model output.
- The project endpoint in `.env` is valid.

## Common issues

- `DefaultAzureCredential failed to retrieve a token`: sign in again with `az login`.
- `404 Not Found`: check your project endpoint format.
- SDK mismatch errors: verify `azure-ai-projects>=2.0.0`.
