# Microsoft Foundry Workshop

Welcome to a docs-first Microsoft Foundry workshop for beginners.

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
    <p>The examples stay in one language so participants can focus on Foundry concepts instead of SDK translation.</p>
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
6. Add a built-in tool to an agent and force a tool-backed answer.
7. Build a simple RAG flow with file search over a local document.
8. Explore tracing as a stretch lab.

## Before you start

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
