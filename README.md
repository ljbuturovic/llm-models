# llm-models

![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A simple command-line tool to list available LLM models from various providers (OpenAI, Google, Anthropic, xAI, Baseten).

## Installation

### Linux/macOS

```bash
$ pipx install llm-models
```

### Windows (untested)
```bash
pip install llm-models
```

## Usage
```bash
$ llm-models -h
usage: llm-models [-h] -p {OpenAI,Anthropic,xAI,GoogleAI,VertexAI,Baseten}
                  [-r REGION] [-c]

List available LLM models from various providers

options:
  -h, --help            show this help message and exit
  -p {OpenAI,Anthropic,xAI,GoogleAI,VertexAI,Baseten}, --provider {OpenAI,Anthropic,xAI,GoogleAI,VertexAI,Baseten}
                        The LLM provider backend.
                        - 'GoogleAI': Google AI Studio (API Key). Global/Auto-routed.
                        - 'VertexAI': Google Cloud Vertex AI (IAM Auth). Region-specific.
  -r REGION, --region REGION
                        Google Cloud region (e.g., 'us-central1').
                        *Required* if provider is VertexAI. Ignored for other providers.
  -c, --check           Probe each model with a minimal 1-token request to report
                        live availability instead of just listing the catalog.
                        Anthropic only; consumes a tiny amount of credits per model.
```


The tool requires API keys set as environment variables:
- `OPENAI_API_KEY` for OpenAI
- `GOOGLE_API_KEY` for GoogleAI API, or `GOOGLE_CLOUD_PROJECT` for VertexAI API
- `ANTHROPIC_API_KEY` for Anthropic
- `XAI_API_KEY` for xAI

### Examples

List OpenAI models:
```bash
$ llm-models --provider OpenAI
Listing available OpenAI models...
================================================================================
Model: babbage-002
Model: chatgpt-4o-latest
Model: codex-mini-latest
...
```

List Google models using GoogleAI API:
```bash
$ llm-models -p GoogleAI
Listing available Google AI Studio models (auto-routed region)...
================================================================================
Model: models/embedding-gecko-001
Model: models/gemini-2.5-pro-preview-03-25
Model: models/gemini-2.5-flash
...
```

List Google models using Vertex AI API (with regional endpoint):
```bash
$ llm-models -p VertexAI -r us-central1
Listing available Vertex AI models (project: ZZZ, region: us-central1)...
================================================================================
Model: publishers/google/models/imageclassification-efficientnet
Model: publishers/google/models/occupancy-analytics
Model: publishers/google/models/multimodalembedding
...

```

List Anthropic models:
```bash
$ llm-models -p Anthropic
Listing available Anthropic models...
================================================================================
Model: claude-haiku-4-5-20251001 (Claude Haiku 4.5)
Model: claude-sonnet-4-5-20250929 (Claude Sonnet 4.5)
...
```

#### Listing vs. checking (`--check`)

A plain listing reads Anthropic's **model catalog** (`/v1/models`): the set of
model IDs your API key is *entitled to address*. It is free and instant, but it
is **not** a health check — a model can appear in the catalog while not actually
being served to your key (still rolling out, gated by tier, or mid-incident).

`--check` answers the other question — *can I get a completion from it right
now?* — by sending each model a minimal 1-token request and reporting the live
result:

```bash
$ llm-models -p Anthropic --check
Checking live availability of Anthropic models...
================================================================================
✗ claude-fable-5 (Claude Fable 5) - not found for this key
✓ claude-opus-4-8 (Claude Opus 4.8) - available
✓ claude-sonnet-4-6 (Claude Sonnet 4.6) - available
✓ claude-haiku-4-5-20251001 (Claude Haiku 4.5) - available
...
```

Status meanings:

| Symbol | Meaning |
| ------ | ------- |
| `✓ available` | Served right now (HTTP 200). |
| `✗ unavailable (overloaded)` | Real model, temporarily over capacity (HTTP 529) — retry later. |
| `✗ not found for this key` | In the catalog but not serveable to your key (HTTP 404): not yet rolled out, or gated by tier/region. |
| `✗ unauthorized` | API key rejected (HTTP 401). |
| `⚠ rate-limited` | Throttled (HTTP 429) — couldn't determine availability. |

The two views fail for different reasons and have different fixes: a `404` is a
configuration/entitlement problem (retrying won't help), while a `529` is
transient (retrying will). The catalog tells you *whether it's worth trying*;
`--check` tells you *whether trying works right now*.

> **Note:** `--check` spends a tiny amount of credits per model. If your account
> is out of credits, it prints a friendly message and exits instead of dumping a
> stack trace — plain listing still works, since it costs nothing.

List xAI models:
```bash
$ llm-models -p xAI
Listing available xAI models (NOTE: xAI uses aliases, so grok-4 is an acceptable API name, resolving to grok-4-0709 as of Nov. 2025)...
================================================================================
Model: grok-2-1212
Model: grok-2-vision-1212
Model: grok-3
...
```

List Baseten models:
```bash
$ llm-models -p Baseten
Listing available Baseten models...
================================================================================
Model: openai/gpt-oss-120b (OpenAI GPT 120B) context: 128,072
Model: deepseek-ai/DeepSeek-V3.1 (DeepSeek V3.1) context: 163,840
Model: zai-org/GLM-4.7 (GLM 4.7) context: 200,000
Model: moonshotai/Kimi-K2.5 (Kimi K2.5) context: 262,000
Model: MiniMaxAI/MiniMax-M2.5 (Minimax M2.5) context: 204,000
Model: zai-org/GLM-5 (GLM 5) context: 202,800
Model: nvidia/Nemotron-120B-A12B (Nemotron Super) context: 202,800
Model: moonshotai/Kimi-K2.6 (Kimi K2.6) context: 262,000

```

## Requirements

- Python 3.10+
- tested on Ubuntu 24.04 and macOS 26.1
