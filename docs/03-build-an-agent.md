# 03 Build An Agent

## Goal

Create a prompt agent version and use it in a multi-turn conversation.

## Estimated time

15 to 20 minutes.

## Official references

- [Azure AI Agents quickstart](https://learn.microsoft.com/azure/ai-services/agents/quickstart?context=/azure/ai-foundry/context/context)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)
- [Azure SDK for Python agent samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/agents)

## Exercise flow

### Step 1: create the agent

```bash
python examples/02-agent-chat/create_agent.py
```

[Open create_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/02-agent-chat/create_agent.py)

### Step 2: chat with the agent

```bash
python examples/02-agent-chat/chat_with_agent.py
```

[Open chat_with_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/02-agent-chat/chat_with_agent.py)

## What this lab demonstrates

1. A prompt agent definition with a deployed model and instructions.
2. Agent version creation through the Foundry project client.
3. A conversation object for stateful chat.
4. Multi-turn responses routed through an agent reference.

## Expected result

- The agent creation script prints an agent id, name, and version.
- The chat script answers the first question and the follow-up.

## Verification

- You can see the agent in the Foundry project.
- The same conversation carries context into the second turn.

## Instructor note

This is the first lab where participants usually confuse the model deployment name with the agent name. Keep those separate in `.env`.
