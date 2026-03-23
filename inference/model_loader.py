"""
Model loader module for loading trained machine learning models.

This module provides functionality to load a pre-trained model
from a pickle file using joblib.
"""

import logging
from pathlib import Path
from typing import Any

import joblib

logger = logging.getLogger(__name__)

# Get project root (parent of inference directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "model_v1.pkl"


def load_model(filepath: str | None = None) -> Any:
    """
    Load a trained model from a pickle file.

    Args:
        filepath: Path to the model file. Defaults to PROJECT_ROOT/models/model_v1.pkl.

    Returns:
        Any: The loaded model object.

    Raises:
        FileNotFoundError: If the model file does not exist.
    """
    # Use default path if not specified
    if filepath is None:
        filepath = DEFAULT_MODEL_PATH
    else:
        # Resolve to absolute path relative to project root
        filepath = PROJECT_ROOT / filepath

    filepath = Path(filepath)

    if not filepath.exists():
        raise FileNotFoundError(
            f"Model file not found: {filepath}. "
            "Please ensure the model has been trained and the path is correct."
        )

    logger.info(f"Loading model from {filepath}...")
    model = joblib.load(filepath)
    logger.info("Model loaded successfully")

    return model
