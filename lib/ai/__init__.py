"""
Centralized AI Model Registry for Physics Lab.
Provides unified access to active Gemini model endpoints across CLI and maintenance tools.
"""
from lib.ai.models import get_flash_model, get_pro_model, get_embedding_model, load_model_registry

__all__ = ["get_flash_model", "get_pro_model", "get_embedding_model", "load_model_registry"]
