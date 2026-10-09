"""
lib/ai/models.py

Unified model registry accessor for Physics Lab.
Loads canonical active model endpoints from app/config/ai_models.json
with optional environment variable overrides.
"""
import os
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONFIG_PATH = PROJECT_ROOT / "app" / "config" / "ai_models.json"

_cached_registry = None

def load_model_registry() -> dict:
    """Loads and caches the centralized ai_models.json configuration."""
    global _cached_registry
    if _cached_registry is not None:
        return _cached_registry

    defaults = {
        "flash": "gemini-flash-latest",
        "pro": "gemini-pro-latest",
        "embedding": "gemini-embedding-001"
    }

    if CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    defaults.update(data)
        except Exception:
            pass

    _cached_registry = defaults
    return _cached_registry

def get_flash_model() -> str:
    """Returns active Flash model name (e.g., for formula drafting and quick sweeps)."""
    env_override = os.environ.get("GEMINI_FLASH_MODEL") or os.environ.get("MODEL_NAME")
    if env_override:
        return env_override.strip()
    return load_model_registry().get("flash", "gemini-flash-latest")

def get_flash_lite_model() -> str:
    """Returns active Flash-Lite model name for high-throughput, low-latency tasks."""
    env_override = os.environ.get("GEMINI_FLASH_LITE_MODEL")
    if env_override:
        return env_override.strip()
    return load_model_registry().get("flash_lite", "gemini-flash-lite-latest")

def get_flash_candidates() -> list:
    """Returns an ordered list of Flash model candidates for resilient zero-cost drafting."""
    primary = get_flash_model()
    reg = load_model_registry()
    fallbacks = reg.get("flash_fallbacks", [
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
        "gemini-flash-lite-latest",
        "gemini-3.5-flash-lite"
    ])
    candidates = [primary]
    for fb in fallbacks:
        if fb not in candidates:
            candidates.append(fb)
    return candidates


def get_pro_model() -> str:
    """Returns active Pro/reasoning model name (e.g., for multi-step derivations)."""
    env_override = os.environ.get("GEMINI_PRO_MODEL")
    if env_override:
        return env_override.strip()
    return load_model_registry().get("pro", "gemini-pro-latest")

def get_embedding_model() -> str:
    """Returns active text embedding model name for vector semantic search."""
    env_override = os.environ.get("GEMINI_EMBEDDING_MODEL")
    if env_override:
        return env_override.strip()
    return load_model_registry().get("embedding", "gemini-embedding-001")
