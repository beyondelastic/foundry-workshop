# 04 Evaluate An Agent

## Goal

Run a simple evaluation against your agent using a tiny JSONL dataset and built-in evaluators.

## Estimated time

15 to 25 minutes.

## Official references

- Microsoft Foundry guidance: evaluate your AI agents
- Python SDK evaluation samples from the Azure SDK repository

## Exercise

Run the evaluation script:

```bash
python examples/03-agent-eval/evaluate_agent.py
```

## Example files

- [Open evaluate_agent.py on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/03-agent-eval/evaluate_agent.py)
- [Open test-queries.jsonl on GitHub](https://github.com/beyondelastic/foundry-workshop/blob/main/examples/03-agent-eval/test-queries.jsonl)

## What this lab demonstrates

1. Upload a JSONL file as a dataset.
2. Define evaluation criteria.
3. Create an evaluation.
4. Start an evaluation run that targets your agent.
5. Poll for completion and print a report URL.

## Dataset format

The workshop uses a minimal dataset where each line contains a `query` field.

## Suggested discussion points

- Why task adherence and coherence are useful starter evaluators.
- Why safety evaluators matter even in simple demos.
- Why evaluation belongs in the development loop and not only at the end.

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
