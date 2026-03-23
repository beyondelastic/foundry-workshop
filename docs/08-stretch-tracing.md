# 08 Stretch Lab: Tracing

## Goal

Explore observability after the core labs are working.

## Why this is a stretch lab

Tracing is valuable, but it adds more setup and interpretation than the core workshop needs. That makes it a good optional follow-on section.

## Official references

- [Microsoft Foundry app tracing guidance](https://learn.microsoft.com/azure/foundry-classic/how-to/develop/trace-application)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)

## Suggested exercise

1. Read the official tracing setup guide.
2. Enable tracing for one of the workshop scripts.
3. Run a short conversation.
4. Inspect the resulting telemetry and trace data.

## What to look for

- latency by step
- model and evaluator usage
- failures or retries
- conversation flow across requests

## Recommended outcome

Participants leave the workshop knowing that building the happy path is only the start, and that Foundry includes tooling to inspect quality and behavior after the first prototype works.