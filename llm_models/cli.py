#!/usr/bin/env python3
"""Quick script to list available LLM models from various providers"""

import argparse
import os
import sys
from importlib.metadata import version as _pkg_version

try:
    __version__ = _pkg_version("llm-models")
except Exception:
    __version__ = "unknown"

parser = argparse.ArgumentParser(
    description=f"List available LLM models from various providers (v{__version__})",
    formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument("-p", "--provider",
                    required=True,
                    choices=["OpenAI", "Anthropic", "xAI", "GoogleAI", "VertexAI", "Baseten", "OpenRouter"],
                    help="""The LLM provider backend.
- 'GoogleAI': Google AI Studio (API Key). Global/Auto-routed.
- 'VertexAI': Google Cloud Vertex AI (IAM Auth). Region-specific.
- 'Baseten': Baseten deployed models (BASETEN_API_KEY).""")
parser.add_argument("-V", "--version", action="version", version=f"%(prog)s {__version__}")
parser.add_argument("-r", "--region",
                    help="""Google Cloud region (e.g., 'us-central1').
*Required* if provider is VertexAI. Ignored for other providers.""")
parser.add_argument("-c", "--check", action="store_true",
                    help="""Probe each model with a minimal 1-token request to report
live availability instead of just listing the catalog.
Anthropic only; consumes a tiny amount of credits per model.""")

# Global args variable, set by main()
args = None


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


class _OutOfCredits(Exception):
    """Raised when the Anthropic account has insufficient credit balance."""


def _probe_anthropic_model(api_key, model_id):
    """Send a minimal 1-token request to check a model's live availability.

    Returns a (symbol, label) tuple for display. Raises _OutOfCredits if the
    account is out of credits, since every subsequent probe would fail too.
    """
    import json
    import urllib.error
    import urllib.request

    payload = json.dumps({
        "model": model_id,
        "max_tokens": 1,
        "messages": [{"role": "user", "content": "hi"}],
    }).encode()
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req) as response:
            response.read()
        return ("✓", "available")
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        try:
            err = json.loads(body).get("error", {})
            etype = err.get("type", "")
            emsg = err.get("message", "")
        except Exception:
            etype, emsg = "", body[:200]

        if "credit balance" in emsg.lower() or etype == "billing_error":
            raise _OutOfCredits(emsg or "credit balance too low")
        if e.code == 529 or etype == "overloaded_error":
            return ("✗", "unavailable (overloaded)")
        if e.code == 404 or etype == "not_found_error":
            return ("✗", "not found for this key")
        if e.code == 401:
            return ("✗", "unauthorized (check API key)")
        if e.code == 429:
            return ("⚠", "rate-limited")
        detail = emsg[:60] if emsg else etype or "unknown error"
        return ("⚠", f"error {e.code}: {detail}")
    except urllib.error.URLError as e:
        return ("⚠", f"network error: {e.reason}")


def list_anthropic_models():
    """List available Anthropic models"""
    import json
    import urllib.request

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)

    checking = getattr(args, "check", False)
    if checking:
        print("Checking live availability of Anthropic models...")
    else:
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
    except Exception as e:
        print(f"Error listing models: {e}")
        sys.exit(1)

    models = data.get("data", [])
    try:
        for model in models:
            model_id = model.get("id", "unknown")
            display_name = model.get("display_name", "")
            label = f"{model_id} ({display_name})" if display_name else model_id
            if checking:
                symbol, status = _probe_anthropic_model(api_key, model_id)
                print(f"{symbol} {label} - {status}")
            else:
                print(f"Model: {label}")
    except _OutOfCredits as e:
        print()
        print("=" * 80)
        print("Out of credits: your Anthropic account's credit balance is too low to")
        print("run availability checks. Listing still works (it doesn't cost credits);")
        print("re-run without --check, or top up at https://console.anthropic.com/settings/billing")
        if str(e):
            print(f"\nAPI message: {e}")
        sys.exit(1)


def list_baseten_models():
    """List Baseten hosted models"""
    import json
    import urllib.request

    api_key = os.getenv("BASETEN_API_KEY")
    if not api_key:
        print("Error: BASETEN_API_KEY not set")
        sys.exit(1)

    print("Listing available Baseten models...")
    print("=" * 80)

    try:
        req = urllib.request.Request(
            "https://inference.baseten.co/v1/models",
            headers={"Authorization": f"Bearer {api_key}"}
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        for model in data.get("data", []):
            model_id = model.get("id", "unknown")
            name = model.get("name", "")
            context = model.get("context_length")
            parts = [f"Model: {model_id}"]
            if name:
                parts.append(f"({name})")
            if context:
                parts.append(f"context: {context:,}")
            print(" ".join(parts))
    except Exception as e:
        print(f"Error listing models: {e}")
        sys.exit(1)


def list_openrouter_models():
    """List models available via OpenRouter"""
    import json
    import urllib.request

    # The models endpoint is public; a key is optional and only used if present.
    api_key = os.getenv("OPENROUTER_API_KEY")

    print("Listing available OpenRouter models...")
    print("=" * 80)

    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    try:
        req = urllib.request.Request(
            "https://openrouter.ai/api/v1/models",
            headers=headers
        )
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())

        for model in sorted(data.get("data", []), key=lambda m: m.get("id", "")):
            model_id = model.get("id", "unknown")
            name = model.get("name", "")
            context = model.get("context_length")
            price = (model.get("pricing") or {}).get("prompt")
            parts = [f"Model: {model_id}"]
            if name:
                parts.append(f"({name})")
            if context:
                parts.append(f"context: {context:,}")
            if price:
                parts.append(f"${price}/in-tok")
            print(" ".join(parts))
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


def main():
    """Entry point for the CLI."""
    global args
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
    elif args.provider == "Baseten":
        list_baseten_models()
    elif args.provider == "OpenRouter":
        list_openrouter_models()


if __name__ == "__main__":
    main()
