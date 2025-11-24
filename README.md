# llm_models

![Python](https://img.shields.io/badge/python-3.7+-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

A simple command-line tool to list available LLM models from various providers (OpenAI, Google, Anthropic, xAI).

## Installation

```bash
$ pip install llm_models
```

## Usage

The tool requires API keys set as environment variables:
- `OPENAI_API_KEY` for OpenAI
- `GOOGLE_API_KEY` for Google Gemini API, or `GOOGLE_CLOUD_PROJECT` for Vertex AI API
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

List Google models using Gemini API:
```bash
$ llm-models --provider GoogleAI
Listing available Google AI Studio models (auto-routed region)...
================================================================================
Model: models/embedding-gecko-001
Model: models/gemini-2.5-pro-preview-03-25
Model: models/gemini-2.5-flash
Model: models/gemini-2.5-pro-preview-05-06
Model: models/gemini-2.5-pro-preview-06-05
```

List Google models using Vertex AI API (with regional endpoint):
```bash
$ llm-models --provider VertexAI --region us-central1
```

List Anthropic models:
```bash
$ llm-models --provider Anthropic
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
$ llm-models --provider xAI
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
