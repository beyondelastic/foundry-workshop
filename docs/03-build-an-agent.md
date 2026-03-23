# 03 Build An Agent

## Goal

Create a prompt agent version and use it in a multi-turn conversation.

## Estimated time

15 to 20 minutes.

## Official references

- Microsoft Foundry quickstart: create an agent
- Microsoft Foundry quickstart: chat with an agent
- Python samples: `samples/python/quickstart/create-agent/quickstart-create-agent.py` and `samples/python/quickstart/chat-with-agent/quickstart-chat-with-agent.py`

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
