# Microsoft Foundry Workshop

Welcome to a docs-first Microsoft Foundry workshop for beginners.

The examples use lightweight healthcare and life sciences scenarios so the workshop stays consistent across model calls, agent prompts, tool use, RAG, evaluation, and workflow labs.

Workshop source repository: [beyondelastic/foundry-workshop](https://github.com/beyondelastic/foundry-workshop)

This workshop is intentionally small, practical, and tied to official Microsoft documentation. Each section includes:

- a clear goal
- official reference links
- one or more runnable Python examples
- expected results
- a short verification checklist

<div class="hero-grid">
  <div class="hero-card">
    <h3>Official by default</h3>
    <p>Every core exercise is mapped to Microsoft Learn or the official Foundry samples repository.</p>
  </div>
  <div class="hero-card">
    <h3>Python only</h3>
    <p>The examples stay in one language so you can focus on Foundry concepts instead of SDK translation.</p>
  </div>
  <div class="hero-card">
    <h3>Built for beginners</h3>
    <p>Each exercise is small, verifiable, and sequenced so the workshop can be taught live or followed alone.</p>
  </div>
</div>

## Learning path

1. Confirm prerequisites and environment setup.
2. Create a Foundry resource, project, and model deployment.
3. Send your first model request from Python.
4. Create a prompt agent and chat with it across turns.
5. Evaluate that agent with a small dataset.
6. Add simple OpenTelemetry tracing and inspect the trace in Foundry.
7. Add a built-in tool to an agent and inspect a tool-backed answer.
8. Build a simple RAG flow with file search over a local document.
9. Coordinate two agents through a simple Python handoff.
10. Create and invoke a native Foundry workflow that coordinates multiple agents.

## Before you start

- Clone this repository, or fork it and clone your fork, so you can run the local example files during the workshop.
- Complete the steps in `SETUP.md`.
- Verify you can sign in with the Azure CLI.
- Confirm you know your Foundry project endpoint.

## Workshop outcomes

By the end of the core labs, you should be able to:

- connect Python code to a Foundry project
- use the OpenAI-compatible client exposed by the project
- create a prompt agent version
- hold a multi-turn conversation with that agent
- evaluate the agent with built-in evaluators
- use a built-in agent tool for a grounded response
- ground an agent answer against uploaded document content
- coordinate two agents through a simple Python orchestrator and explicit handoff
- prepare and invoke a native Foundry workflow from Python
