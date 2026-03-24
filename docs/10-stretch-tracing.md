# 10 Stretch Lab: Advanced Tracing

## Goal

Extend the basic observability lab with richer tracing once the core workshop flow is working.

## Why this is a stretch lab

The simple observability lab shows one traced model call and one custom span. This stretch lab is for you if you want to trace more realistic, multi-step flows after the basics are already in place.

## Official references

- [Microsoft Foundry app tracing guidance](https://learn.microsoft.com/azure/foundry-classic/how-to/develop/trace-application)
- [Microsoft Foundry SDKs and Endpoints](https://learn.microsoft.com/azure/foundry/how-to/develop/sdk-overview?tabs=sync&pivots=programming-language-python)

## Suggested exercise

1. Read the official tracing setup guide.
2. Enable tracing for one of the later workshop scripts such as tool calls, RAG, or multi-agent handoff.
3. Add one or two custom spans around meaningful application steps.
4. Inspect the resulting telemetry and trace data.

## What to look for

- latency by step
- model and evaluator usage
- failures or retries
- conversation flow across requests

## Expected outcome

After this lab, you should be comfortable treating tracing as part of the normal development loop, not just an optional extra after the happy path works.