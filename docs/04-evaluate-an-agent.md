# 04 Evaluate An Agent

## Goal

Run a simple evaluation against your agent using a tiny JSONL dataset of healthcare and life-science prompts plus built-in evaluators.

## Estimated time

15 to 25 minutes.

## Official references

- [Microsoft Foundry cloud evaluation guidance](https://learn.microsoft.com/azure/foundry/how-to/develop/cloud-evaluation)
- [Azure SDK for Python evaluation samples](https://github.com/Azure/azure-sdk-for-python/tree/main/sdk/ai/azure-ai-projects/samples/evaluations)

## Exercise

Run the evaluation script:

```bash
python examples/03-agent-eval/evaluate_agent.py
```

This lab has two distinct phases. First, the script defines the evaluation itself: what kind of dataset shape is expected and which evaluators should be applied. Second, it starts an evaluation run that feeds your dataset rows to the target agent and records the scores.

## Example files

- [Open evaluate_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/03-agent-eval/evaluate_agent.py)
- [Open test-queries.jsonl on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/03-agent-eval/test-queries.jsonl)

## What this lab demonstrates

1. Upload a JSONL file as a dataset.
2. Define evaluation criteria.
3. Create an evaluation.
4. Start an evaluation run that targets your agent.
5. Poll for completion and print a report URL.

## What is happening under the hood

- `project_client.datasets.upload_file(...)` uploads the local JSONL file so Foundry can use it as evaluation input.
- `testing_criteria` defines which built-in evaluators should score the agent output. In this lab, the script uses task adherence, coherence, and violence.
- `data_source_config` tells Foundry what each dataset row looks like. Here, each row is expected to contain a single `query` field.
- `openai_client.evals.create(...)` creates the evaluation definition. Think of this as registering the evaluation recipe: the name, expected input shape, and scoring criteria. It does not execute the evaluation yet.
- `openai_client.evals.runs.create(...)` starts a concrete run of that evaluation. This is the step that actually sends each dataset item to your agent and collects the evaluator results.
- The `target` block inside the run points to your Foundry agent by name, so the evaluation is scoring agent responses rather than direct raw model calls.
- The polling loop checks the run status until Foundry marks it as `completed` or `failed`, then prints the report URL.

The key line `evaluation = openai_client.evals.create(...)` is important because the returned `evaluation.id` is used by the next step. Without creating the evaluation definition first, there would be no evaluation object for `openai_client.evals.runs.create(...)` to run.

## Dataset format

The workshop uses a minimal dataset where each line contains a `query` field.

In this version of the workshop, those queries are simple healthcare and life-science questions so the evaluation stays aligned with the rest of the examples.

## Why these evaluators are a good starting point

- Task adherence checks whether the agent actually followed the intent of the prompt. This is a good first metric because an answer can sound fluent while still missing the task.
- Coherence checks whether the response reads clearly and holds together as a complete answer. That makes it useful for spotting weak or confusing outputs even in small demos.
- A safety evaluator such as violence helps you confirm that the evaluation flow can also check policy-related behavior. Even simple workshop agents should be tested for both usefulness and safety.

Together, these evaluators give you a practical starting set: one checks whether the answer stayed on task, one checks whether it reads well, and one checks a basic safety dimension. That is enough to introduce evaluation as part of normal development rather than something you only do at the end.

## Expected result

The script prints:

- the uploaded dataset id
- the evaluation id
- the evaluation run id
- the final run status
- the Foundry report URL

## Verification

- You can open the report URL in the Foundry portal.
- The run includes per-criterion results.
