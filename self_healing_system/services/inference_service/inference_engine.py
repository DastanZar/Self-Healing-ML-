"""
Inference engine for the self-healing ML system.

This module provides real ML inference by loading a trained model
and making predictions on infrastructure metrics.
"""

import logging
import sys
import os
from pathlib import Path
from typing import Any, Dict, Optional

import numpy as np

logger = logging.getLogger(__name__)

# Get project root (workspace root)
PROJECT_ROOT = Path(os.getcwd())
DEFAULT_MODEL_PATH = PROJECT_ROOT / "models" / "model_v1.pkl"

# Global model instance (loaded once at startup)
_model: Any = None
_is_initialized: bool = False


def initialize_inference_system(model_path: str | None = None) -> Any:
    """
    Initialize the inference system by loading the model ONCE at startup.
    This must be called before any predictions are made.

    Args:
        model_path: Path to the trained model file. Defaults to PROJECT_ROOT/models/model_v1.pkl.

    Returns:
        The loaded model object.

    Raises:
        RuntimeError: If model is already initialized.
        FileNotFoundError: If the model file does not exist.
    """
    global _model, _is_initialized

    if _is_initialized:
        logger.info("Model already initialized, reusing existing instance")
        return _model

    # Use default path if not specified
    if model_path is None:
        model_path = DEFAULT_MODEL_PATH
    else:
        # Resolve to absolute path relative to project root
        model_path = PROJECT_ROOT / model_path

    try:
        # Import here to avoid circular imports
        from inference.model_loader import load_model

        logger.info(f"Loading inference model from {model_path}...")
        _model = load_model(str(model_path))
        _is_initialized = True
        logger.info(f"Model loaded successfully. Features: {getattr(_model, 'n_features_in_', 'unknown')}")

        return _model
    except FileNotFoundError as e:
        logger.error(f"Model file not found: {e}")
        _is_initialized = False
        raise
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _is_initialized = False
        raise


def load_inference_model(model_path: str | None = None) -> Any:
    """
    Alias for initialize_inference_system for backward compatibility.
    Loads the model ONCE at system startup.

    Args:
        model_path: Path to the trained model file. Defaults to PROJECT_ROOT/models/model_v1.pkl.

    Returns:
        The loaded model object.
    """
    return initialize_inference_system(model_path)


def get_model() -> Optional[Any]:
    """
    Get the currently loaded model.

    Returns:
        The loaded model or None if not loaded.
    """
    return _model


def is_model_initialized() -> bool:
    """
    Check if the model has been initialized.

    Returns:
        True if model is loaded and ready, False otherwise.
    """
    return _is_initialized and _model is not None


def create_input_features(input_data: Dict[str, float]) -> np.ndarray:
    """
    Create input features with correct shape for the model.

    The infrastructure metrics model expects 4 features:
    cpu, memory, latency, error_rate.

    Args:
        input_data: Dictionary with system metrics (cpu, memory, latency, error_rate).

    Returns:
        numpy array with shape (1, 4) ready for prediction.

    Raises:
        RuntimeError: If model is not initialized. Call initialize_inference_system() first.
    """
    global _model, _is_initialized

    if not _is_initialized or _model is None:
        raise RuntimeError(
            "Model not initialized. Call initialize_inference_system() before making predictions."
        )

    # Extract features from input
    cpu = input_data.get("cpu", 0.0)
    memory = input_data.get("memory", 0.0)
    latency = input_data.get("latency", 0.0)
    error_rate = input_data.get("error_rate", 0.0)

    # Create feature array in the same order as training data
    features = np.array([[cpu, memory, latency, error_rate]], dtype=np.float64)
    
    return features


def run_inference(input_data: Dict[str, float]) -> int:
    """
    Run model inference on input data.
    Uses the pre-loaded model from initialize_inference_system().

    Args:
        input_data: Dictionary with system metrics.

    Returns:
        Prediction result (0 or 1 for fraud detection).

    Raises:
        RuntimeError: If model is not initialized. Call initialize_inference_system() first.
    """
    global _model, _is_initialized

    # Safety check: ensure model is initialized
    if not _is_initialized or _model is None:
        raise RuntimeError(
            "Model not initialized. Call initialize_inference_system() before making predictions."
        )

    logger.info("Running model inference...")
    print(f"Running model inference...")

    # Create input features with correct shape
    input_features = create_input_features(input_data)
    logger.info(f"Input shape: {input_features.shape}")

    # Make prediction using the already loaded model
    from inference.predict import predict
    prediction = predict(_model, input_features)
    prediction_result = int(prediction[0])

    logger.info(f"Prediction result: {prediction_result}")
    print(f"Prediction result: {prediction_result}")

    return prediction_result
