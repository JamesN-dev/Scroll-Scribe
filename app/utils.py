# scrollscribe/utils.py
# Adds model resolution, validation, and metadata loading from litellm JSON

import json
import os
from difflib import get_close_matches
from pathlib import Path

from rich.console import Console

console = Console()

# Path to model metadata file (update if you move it)
MODEL_REGISTRY_PATH = Path("data/litellm-model_prices_and_context_window.json")


def load_model_registry():
    if not MODEL_REGISTRY_PATH.exists():
        console.print(f"[bold red][ERROR] Model registry not found:[/bold red] {MODEL_REGISTRY_PATH}")
        return {}
    with open(MODEL_REGISTRY_PATH, encoding="utf-8") as f:
        return json.load(f)


def resolve_model_config(model_id: str):
    """Load model config from JSON registry and validate existence."""
    registry = load_model_registry()

    if model_id in registry:
        return registry[model_id]

    # Fallback: show close matches
    matches = get_close_matches(model_id, registry.keys(), n=5, cutoff=0.3)
    console.print(f"[bold red][ERROR] Model '{model_id}' not found in registry.[/bold red]")
    if matches:
        console.print("[cyan][INFO] Did you mean:[/cyan]")
        for m in matches:
            console.print(f"  • {m}")
    raise SystemExit(1)


def get_api_key(env_var: str) -> str:
    api_key = os.getenv(env_var)
    if api_key:
        return api_key

    console.print(f"[yellow][WARN] API key env var '{env_var}' not found.[/yellow]")
    try:
        api_key = input(f"➤ Enter value for {env_var}: ").strip()
        if not api_key:
            raise ValueError("Empty API key")
        os.environ[env_var] = api_key
        return api_key
    except (KeyboardInterrupt, EOFError):
        console.print("\n[bold red][ABORT] User cancelled input.[/bold red]")
        raise SystemExit(1) from KeyboardInterrupt


def display_model_info(model_id: str, metadata: dict):
    ctx_in = metadata.get("max_input_tokens", "?")
    ctx_out = metadata.get("max_output_tokens", "?")
    price_in = metadata.get("input_cost_per_million", "?")
    price_out = metadata.get("output_cost_per_million", "?")

    console.print(f"[green][MODEL INFO][/green] {model_id}")
    console.print(f"  • Max input tokens: {ctx_in}")
    console.print(f"  • Max output tokens: {ctx_out}")
    console.print(f"  • Cost: ${price_in}/M input | ${price_out}/M output")
