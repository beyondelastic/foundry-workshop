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

This step does not chat with the model yet. It creates a prompt-based agent version inside your Foundry project by combining three things: the project endpoint, the deployed model name, and the agent instructions. In this script, `PromptAgentDefinition(...)` tells Foundry which deployed model the agent should use and what system-style behavior it should follow.

The script reads the agent name from `AZURE_AI_AGENT_NAME` in your `.env` file. If you want the agent to appear under a different name in Foundry, change that value in `.env` before running the script.

### Step 2: chat with the agent

```bash
python examples/02-agent-chat/chat_with_agent.py
```

[Open chat_with_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/02-agent-chat/chat_with_agent.py)

This step uses the agent you created in step 1. Instead of calling the model directly, the script creates a conversation and sends messages through the agent reference, so the reply is generated with the agent's instructions applied. Because the script keeps the same conversation object across turns, the second question can use the context from the first question.

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

## Common confusion

This is the first lab where it is easy to confuse the model deployment name with the agent name. Keep those separate in `.env`.

If you want to rename the agent, update `AZURE_AI_AGENT_NAME` in `.env`, not the model deployment name.
