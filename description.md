# Training Description

The training has two connected parts:

## 1. How Large Language Models (LLMs) Work

Explains what happens inside a model, so it is clear what tools like Claude Code and GitHub Copilot actually do. It covers neural networks and how they learn, the transformer architecture (tokens, attention, context window, KV cache), and training and inference (temperature, instruct tuning, reasoning). It then looks at the limits of AI, such as hallucinations and prompt injection, and ends with the path from model to agent: tool calling, the agent loop, RAG and evals.

**Exercises:** a custom neural network for digit recognition (MNIST) and a simple coding agent built on the Claude API.

## 2. AI Coding Agents in Practice

For developers who want to become power users of Claude Code: get changes from the agent they can trust, know what it costs, and control what the agent is allowed to do. Topics:

- working with context and its cost
- building blocks: MCP, subagents, hooks, skills, plugins
- security: permissions, sandbox, prompt injection
- workflow: verification, debugging, worktrees, CI, and when not to use an agent

**Exercises:** done on a small invoicing app with real tickets (bugs and a feature). Includes a ready-to-copy configuration and a cheat sheet.

**Prerequisites:** programming basics, git and the command line.

## Required Setup

Please prepare before the training:

- **Python 3.12+** with packages `numpy`, `matplotlib`, `pillow`, `pyqt5`, `anthropic`, `truststore` and `pytest` (or `uv sync` in each exercise folder)
- **mnist dataset** from https://www.kaggle.com/datasets/hojjatk/mnist-dataset
- **Claude Code** installed and signed in with a company account (`claude --version` works)
- **Claude API access** for the mini-agent exercise: an API key - company gateway
- **jq**, which the hooks exercise uses (optional)
