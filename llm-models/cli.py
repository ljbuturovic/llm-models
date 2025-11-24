#!/usr/bin/env python3
"""Quick script to list available LLM models from various providers"""

import argparse
import os
import sys

parser = argparse.ArgumentParser(
    description="List available LLM models from various providers",
    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-p", "--provider",
                    required=True,
                    choices=["OpenAI", "Anthropic", "xAI", "GoogleAI", "VertexAI"],
                    help="""The LLM provider backend.
- 'GoogleAI': Google AI Studio (API Key). Global/Auto-routed.
- 'VertexAI': Google Cloud Vertex AI (IAM Auth). Region-specific.""")
parser.add_argument("-r", "--region",
                    help="""Google Cloud region (e.g., 'us-central1').
*Required* if provider is VertexAI. Ignored for other providers.""")
args = parser.parse_args()

# Validate region requirement for VertexAI
if args.provider == "VertexAI":
    if not args.region:
        parser.error("--region is required when provider is VertexAI")

    # Validate region format (e.g., us-central1, europe-west4, asia-northeast1)
    import re
    if not re.match(r'^[a-z]+-[a-z]+\d+$', args.region):
        print(f"Error: Invalid region format '{args.region}'")
        print("Expected format: <continent>-<location><number> (e.g., 'us-central1', 'europe-west4')")
        print("\nCommon Vertex AI regions:")
        print("  us-central1, us-east4, us-west1")
        print("  europe-west1, europe-west4")
        print("  asia-northeast1, asia-southeast1")
        print("\nSee: https://cloud.google.com/vertex-ai/docs/general/locations")
        sys.exit(1)

def list_openai_models():
    """List available OpenAI models"""
    try:
        import openai
    except ImportError:
        print("Error: openai package not installed. Install with: pip install openai")
        sys.exit(1)

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: OPENAI_API_KEY not set")
        sys.exit(1)

    print("Listing available OpenAI models...")
    print("=" * 80)

    try:
        client = openai.OpenAI(api_key=api_key)
        models = client.models.list()

        # Filter for main models (not fine-tuned versions)
        main_models = [m for m in models.data if not m.id.startswith("ft:")]

        for model in sorted(main_models, key=lambda x: x.id):
            print(f"Model: {model.id}")
    except Exception as e:
        print(f"Error listing models: {e}")
        sys.exit(1)


def list_googleai_models():
    """List available Google AI Studio models"""
    try:
        from google import genai
    except ImportError:
        print("Error: google-genai package not installed. Install with: pip install google-genai")
        sys.exit(1)

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("Error: GOOGLE_API_KEY not set")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    print("Listing available Google AI Studio models (auto-routed region)...")
    print("=" * 80)

    try:
        models = client.models.list()
        for model in models:
            if hasattr(model, 'supported_generation_methods'):
                methods = model.supported_generation_methods
            else:
                methods = []

            print(f"Model: {model.name}")
            if methods:
                print(f"  Supported methods: {methods}")
    except Exception as e:
        print(f"Error listing models: {e}")
        _try_known_gemini_models(client)


def list_vertexai_models():
    """List available Vertex AI models"""
    try:
        from google import genai
    except ImportError:
        print("Error: google-genai package not installed. Install with: pip install google-genai")
        sys.exit(1)

    project = os.getenv("GOOGLE_CLOUD_PROJECT")
    if not project:
        print("Error: GOOGLE_CLOUD_PROJECT not set (required for Vertex AI)")
        sys.exit(1)

    client = genai.Client(
        vertexai=True,
        project=project,
        location=args.region
    )

    print(f"Listing available Vertex AI models (project: {project}, region: {args.region})...")
    print("=" * 80)

    try:
        models = client.models.list()
        for model in models:
            if hasattr(model, 'supported_generation_methods'):
                methods = model.supported_generation_methods
            else:
                methods = []

            print(f"Model: {model.name}")
            if methods:
                print(f"  Supported methods: {methods}")
    except Exception as e:
        print(f"Error listing models: {e}")
        _try_known_gemini_models(client)


def _try_known_gemini_models(client):
    """Fallback: try known Gemini model names"""
    print("\nTrying alternative approach...")

    test_models = [
        "gemini-3.0-pro",
        "gemini-2.5-pro",
        "gemini-2.0-flash-exp",
        "gemini-1.5-pro",
        "gemini-1.5-flash"
    ]

    for model_name in test_models:
        try:
            client.models.generate_content(
                model=model_name,
                contents="Say hello"
            )
            print(f"✓ {model_name} - WORKS")
        except Exception as e:
            error_msg = str(e)
            if "404" in error_msg or "not found" in error_msg.lower():
                print(f"✗ {model_name} - NOT FOUND")
            else:
                print(f"? {model_name} - Error: {error_msg[:100]}")


def list_anthropic_models():
    """List available Anthropic models"""
    import json
    import urllib.request

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    print("Listing available Anthropic models...")
    print("=" * 80)

    try:
        req = urllib.request.Request(
            "https://api.anthropic.com/v1/models",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01"
            }
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        for model in data.get("data", []):
            model_id = model.get("id", "unknown")
            display_name = model.get("display_name", "")
            if display_name:
                print(f"Model: {model_id} ({display_name})")
            else:
                print(f"Model: {model_id}")
    except Exception as e:
        print(f"Error listing models: {e}")
        sys.exit(1)


def list_xai_models():
    """List available xAI models"""
    try:
        import openai
    except ImportError:
        print("Error: openai package not installed (xAI uses OpenAI-compatible API). Install with: pip install openai")
        sys.exit(1)

    api_key = os.getenv("XAI_API_KEY")
    if not api_key:
        print("Error: XAI_API_KEY not set")
        sys.exit(1)

    print("Listing available xAI models (NOTE: xAI uses aliases, so grok-4 is an acceptable API name, resolving to grok-4-0709 as of Nov. 2025)...")
    print("=" * 80)

    try:
        client = openai.OpenAI(
            api_key=api_key,
            base_url="https://api.x.ai/v1"
        )
        models = client.models.list()

        for model in models.data:
            print(f"Model: {model.id}")
    except Exception as e:
        print(f"Error listing models: {e}")
        print("\nKnown xAI models:")
        print("Model: grok-beta")
        print("Model: grok-vision-beta")
        print("\nNote: Check https://docs.x.ai/docs for the latest model information.")


# Main execution
if args.provider == "OpenAI":
    list_openai_models()
elif args.provider == "GoogleAI":
    list_googleai_models()
elif args.provider == "VertexAI":
    list_vertexai_models()
elif args.provider == "Anthropic":
    list_anthropic_models()
elif args.provider == "xAI":
    list_xai_models()
