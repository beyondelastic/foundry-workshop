# 03 Build An Agent

## Goal

Create a prompt agent version and use it in a multi-turn conversation.

## Estimated time

15 to 20 minutes.

## Official references

- [Azure AI Agents quickstart](https://learn.microsoft.com/azure/ai-services/agents/quickstart?context=/azure/ai-foundry/context/context)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)

## Exercise

1. Create the agent:

```bash
python examples/02-agent-chat/create_agent.py
```

This step does not chat with the model yet. It creates a prompt-based agent version inside your Foundry project by combining three things: the project endpoint, the deployed model name, and the agent instructions. In this script, `PromptAgentDefinition(...)` tells Foundry which deployed model the agent should use and what system-style behavior it should follow.

The script reads the agent name from `AZURE_AI_AGENT_NAME` in your `.env` file. If you want the agent to appear under a different name in Foundry, change that value in `.env` before running the script.

2. Chat with the agent:

```bash
python examples/02-agent-chat/chat_with_agent.py
```

This step uses the agent you created in step 1. Instead of calling the model directly, the script creates a conversation and sends messages through the agent reference, so the reply is generated with the agent's instructions applied. Because the script keeps the same conversation object across turns, the second question can use the context from the first question.

## Example files

- [Open create_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/02-agent-chat/create_agent.py)
- [Open chat_with_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/02-agent-chat/chat_with_agent.py)

```python title="examples/02-agent-chat/create_agent.py"
import os

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import PromptAgentDefinition
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
    agent_name = get_env("AZURE_AI_AGENT_NAME", "AGENT_NAME")

    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )

    agent = project.agents.create_version(
        agent_name=agent_name,
        definition=PromptAgentDefinition(
            model=model_deployment_name,
            instructions=(
                "You are a life sciences workshop assistant. Answer healthcare and "
                "biomedical questions clearly and briefly, stay educational, and do "
                "not provide diagnosis or treatment advice."
            ),
        ),
    )

    print(
        f"Agent created (id: {agent.id}, name: {agent.name}, version: {agent.version})"
    )


if __name__ == "__main__":
    main()
```

```python title="examples/02-agent-chat/chat_with_agent.py"
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
    agent_name = get_env("AZURE_AI_AGENT_NAME", "AGENT_NAME")

    project = AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    )
    openai = project.get_openai_client()

    conversation = openai.conversations.create()

    first_response = openai.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
        input="What does ELISA stand for in a life sciences lab context?",
    )
    print("First response:")
    print(first_response.output_text)

    second_response = openai.responses.create(
        conversation=conversation.id,
        extra_body={"agent_reference": {"name": agent_name, "type": "agent_reference"}},
        input="And what is it commonly used to detect or measure?",
    )
    print("\nSecond response:")
    print(second_response.output_text)


if __name__ == "__main__":
    main()
```

## What this lab demonstrates

1. A prompt agent definition with a deployed model and instructions.
2. Agent version creation through the Foundry project client.
3. A conversation object for stateful chat.
4. Multi-turn responses routed through an agent reference.

## What is happening when you run it

The first script creates a prompt agent version inside your Foundry project. That is the point where you move from direct model calls to a reusable agent resource with instructions and a stable name.

The second script talks to that agent through a conversation. Because the conversation is reused across turns, the agent can use the first exchange as context for the follow-up question.

Taken together, these two scripts show the basic agent lifecycle used throughout the rest of the workshop: define an agent, create it in Foundry, and then route conversation turns through that agent instead of calling the model directly.

## Expected result

- The agent creation script prints an agent id, name, and version.
- The chat script answers the first life-science question and the follow-up.

## Verification

- You can see the agent in the Foundry project.
- The same conversation carries context into the second turn.

## Common confusion

This is the first lab where it is easy to confuse the model deployment name with the agent name. Keep those separate in `.env`.

If you want to rename the agent, update `AZURE_AI_AGENT_NAME` in `.env`, not the model deployment name.
