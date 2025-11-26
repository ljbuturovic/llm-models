# llm-models

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A simple command-line tool to list available LLM models from various providers (OpenAI, Google, Anthropic, xAI).

## Installation

### Linux

```bash
$ pipx install llm-models
```

### macOS

```bash
% brew tap ljbuturovic/tap
% brew install llm-models
```

### Windows
```bash
pip install llm-models
```

## Usage
```bash
$ llm-models -h
usage: llm-models [-h] -p {OpenAI,Anthropic,xAI,GoogleAI,VertexAI} [-r REGION]

List available LLM models from various providers

options:
  -h, --help            show this help message and exit
  -p {OpenAI,Anthropic,xAI,GoogleAI,VertexAI}, --provider {OpenAI,Anthropic,xAI,GoogleAI,VertexAI}
                        The LLM provider backend.
                        - 'GoogleAI': Google AI Studio (API Key). Global/Auto-routed.
                        - 'VertexAI': Google Cloud Vertex AI (IAM Auth). Region-specific.
  -r REGION, --region REGION
                        Google Cloud region (e.g., 'us-central1').
                        *Required* if provider is VertexAI. Ignored for other providers.
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
Model: dall-e-2
Model: dall-e-3
Model: davinci-002
Model: gpt-3.5-turbo
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
Model: models/gemini-2.5-pro-preview-05-06
Model: models/gemini-2.5-pro-preview-06-05
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
Model: publishers/google/models/pt-test
Model: publishers/google/models/imageclassification-vit
...

```

List Anthropic models:
```bash
$ llm-models -p Anthropic
Listing available Anthropic models...
================================================================================
Model: claude-haiku-4-5-20251001 (Claude Haiku 4.5)
Model: claude-sonnet-4-5-20250929 (Claude Sonnet 4.5)
Model: claude-opus-4-1-20250805 (Claude Opus 4.1)
Model: claude-opus-4-20250514 (Claude Opus 4)
Model: claude-sonnet-4-20250514 (Claude Sonnet 4)
Model: claude-3-7-sonnet-20250219 (Claude Sonnet 3.7)
Model: claude-3-5-haiku-20241022 (Claude Haiku 3.5)
Model: claude-3-haiku-20240307 (Claude Haiku 3)
Model: claude-3-opus-20240229 (Claude Opus 3)
```

List xAI models:
```bash
$ llm-models -p xAI
Listing available xAI models (NOTE: xAI uses aliases, so grok-4 is an acceptable API name, resolving to grok-4-0709 as of Nov. 2025)...
================================================================================
Model: grok-2-1212
Model: grok-2-vision-1212
Model: grok-3
Model: grok-3-mini
Model: grok-4-0709
Model: grok-4-1-fast-non-reasoning
Model: grok-4-1-fast-reasoning
Model: grok-4-fast-non-reasoning
Model: grok-4-fast-reasoning
Model: grok-code-fast-1
Model: grok-2-image-1212

```

## Requirements

- Python 3.7+
- tested on Ubuntu 24.04
