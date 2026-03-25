import os
import json

from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv


RESPONSE_OUTPUT_TEXT_DELTA = "response.output_text.delta"
RESPONSE_OUTPUT_ITEM_ADDED = "response.output_item.added"
RESPONSE_OUTPUT_ITEM_DONE = "response.output_item.done"
RESPONSE_FAILED = "response.failed"
RESPONSE_COMPLETED = "response.completed"


def get_env(name: str, fallback: str | None = None) -> str:
    value = os.getenv(name) or (os.getenv(fallback) if fallback else None)
    if not value:
        missing = name if not fallback else f"{name} or {fallback}"
        raise ValueError(f"Missing required environment variable: {missing}")
    return value


def is_verbose_enabled() -> bool:
    return os.getenv("WORKFLOW_VERBOSE", "false").lower() in {"1", "true", "yes", "on"}


def get_field(value, name: str, default=None):
    if isinstance(value, dict):
        return value.get(name, default)
    return getattr(value, name, default)


def get_message_text(item) -> str:
    text_parts: list[str] = []

    for part in get_field(item, "content", []) or []:
        if get_field(part, "type") == "output_text":
            text = get_field(part, "text", "")
            if text:
                text_parts.append(text)

    return "\n".join(text_parts).strip()


def format_agent_label(agent_name: str | None) -> str:
    if not agent_name:
        return "Agent"

    label = agent_name
    if label.startswith("WorkshopFoundryWorkflow"):
        label = label.removeprefix("WorkshopFoundryWorkflow")
    if label.endswith("Agent"):
        label = label.removesuffix("Agent")

    label = label.replace("_", " ").strip()
    if not label:
        return "Agent"

    return f"{label} Agent"


def extract_text_from_workflow_wrapper(text: str) -> str | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, list) or not payload:
        return None

    first_item = payload[0]
    if not isinstance(first_item, dict):
        return None

    direct_text = first_item.get("Text")
    if isinstance(direct_text, str) and direct_text.strip():
        return direct_text.strip()

    for content_item in first_item.get("Content", []):
        if not isinstance(content_item, dict):
            continue
        if content_item.get("Type") == "Text":
            value = content_item.get("Value")
            if isinstance(value, str) and value.strip():
                return value.strip()

    return None


def extract_display_text(response, workflow_name: str) -> str:
    fallback_text = ""

    for item in reversed(getattr(response, "output", []) or []):
        if get_field(item, "type") != "message":
            continue

        text = get_message_text(item)
        if not text:
            continue

        agent_reference = get_field(item, "agent_reference")
        agent_name = get_field(agent_reference, "name")

        if agent_name == workflow_name:
            extracted = extract_text_from_workflow_wrapper(text)
            if extracted:
                return extracted
            fallback_text = text
            continue

        return text

    if fallback_text:
        return fallback_text

    output_text = (getattr(response, "output_text", None) or "").strip()
    return output_text


def extract_conversation_messages(response, workflow_name: str) -> list[tuple[str, str]]:
    messages: list[tuple[str, str]] = []
    seen_messages: set[tuple[str, str]] = set()

    for item in getattr(response, "output", []) or []:
        if get_field(item, "type") != "message":
            continue

        text = get_message_text(item)
        if not text:
            continue

        agent_reference = get_field(item, "agent_reference")
        agent_name = get_field(agent_reference, "name")

        if agent_name == workflow_name:
            continue

        message_key = (agent_name or "", text)
        if message_key in seen_messages:
            continue

        seen_messages.add(message_key)
        messages.append((format_agent_label(agent_name), text))

    return messages


def invoke_workflow_verbose(openai_client, conversation_id: str, workflow_name: str) -> None:
    stream = openai_client.responses.create(
        conversation=conversation_id,
        extra_body={
            "agent_reference": {
                "name": workflow_name,
                "type": "agent_reference",
            }
        },
        input="Start the city break planning workflow.",
        stream=True,
        metadata={"x-ms-debug-mode-enabled": "1"},
    )

    print(f"Created conversation (id: {conversation_id})")
    print(f"Running workflow: {workflow_name}\n")
    for event in stream:
        if event.type == RESPONSE_OUTPUT_TEXT_DELTA:
            print(event.delta, end="", flush=True)
        elif (
            event.type == RESPONSE_OUTPUT_ITEM_ADDED
            and event.item.type == "workflow_action"
        ):
            print(
                f"\n[{event.item.action_id}] status={event.item.status} previous={event.item.previous_action_id}"
            )
        elif (
            event.type == RESPONSE_OUTPUT_ITEM_DONE
            and event.item.type == "workflow_action"
        ):
            print(
                f"\n[{event.item.action_id}] status={event.item.status} previous={event.item.previous_action_id}"
            )
        elif event.type == RESPONSE_FAILED:
            error = getattr(event, "error", None)
            print(f"\nWorkflow failed: {error}")
        elif event.type == RESPONSE_COMPLETED:
            print("\n[response.completed]")
        else:
            item = getattr(event, "item", None)
            item_type = getattr(item, "type", None)
            print(f"\n[event:{event.type}] item_type={item_type}")

    print()


def invoke_workflow_quiet(openai_client, conversation_id: str, workflow_name: str) -> None:
    response = openai_client.responses.create(
        conversation=conversation_id,
        extra_body={
            "agent_reference": {
                "name": workflow_name,
                "type": "agent_reference",
            }
        },
        input="Start the city break planning workflow.",
    )

    messages = extract_conversation_messages(response, workflow_name)
    if messages:
        for index, (label, text) in enumerate(messages):
            if index > 0:
                print()
            print(f"{label}:")
            print(text)
        return

    output_text = extract_display_text(response, workflow_name)
    if output_text:
        print(output_text)
        return

    raise RuntimeError("Workflow completed without text output. Re-run with WORKFLOW_VERBOSE=true for detailed events.")


def main() -> None:
    load_dotenv()

    project_endpoint = get_env("AZURE_AI_PROJECT_ENDPOINT", "PROJECT_ENDPOINT")
    workflow_name = os.getenv("AZURE_AI_WORKFLOW_NAME", "Workshop-City-Break-Workflow")
    verbose = is_verbose_enabled()

    with AIProjectClient(
        endpoint=project_endpoint,
        credential=DefaultAzureCredential(),
    ) as project_client:
        with project_client.get_openai_client() as openai_client:
            conversation = openai_client.conversations.create()

            try:
                if verbose:
                    invoke_workflow_verbose(openai_client, conversation.id, workflow_name)
                else:
                    invoke_workflow_quiet(openai_client, conversation.id, workflow_name)
            finally:
                openai_client.conversations.delete(conversation_id=conversation.id)
                if verbose:
                    print("Conversation deleted")


if __name__ == "__main__":
    main()