"""
Prediction module for making inferences with trained models.

This module provides functionality to load a model and make predictions
on new input data.
"""

import logging
from typing import Any, List, Union

import numpy as np

from inference.model_loader import load_model

logger = logging.getLogger(__name__)


def predict(model: Any, input_data: Union[List, np.ndarray]) -> np.ndarray:
    """
    Make predictions using a trained model.

    Args:
        model: A trained model with a predict method.
        input_data: Input data for prediction. Can be a list or numpy array.

    Returns:
        np.ndarray: Prediction results.

    Raises:
        ValueError: If input data cannot be converted to proper shape.
    """
    logger.info("Making predictions...")

    # Convert input to numpy array if needed
    if isinstance(input_data, list):
        input_data = np.array(input_data)

    # Get expected number of features from the model
    # RandomForestClassifier stores n_features_in_ attribute
    if hasattr(model, "n_features_in_"):
        expected_features = model.n_features_in_
    else:
        # Fallback: try to infer from model classes
        raise ValueError(
            "Model does not have n_features_in_ attribute. "
            "Please ensure the model was trained properly."
        )

    # Reshape input if it's 1D (single sample)
    if input_data.ndim == 1:
        # Check if it matches expected features
        if len(input_data) == expected_features:
            input_data = input_data.reshape(1, -1)
        else:
            raise ValueError(
                f"Input has {len(input_data)} features, "
                f"but model expects {expected_features} features."
            )
    elif input_data.ndim == 0:
        # Single scalar - reshape to 2D
        input_data = input_data.reshape(1, -1)

    logger.info(f"Input data shape: {input_data.shape}")

    # Make predictions
    predictions = model.predict(input_data)

    logger.info(f"Predictions made: {len(predictions)} samples")

    return predictions


def main() -> None:
    """
    Test block to demonstrate model loading and prediction.
    """
    print("=" * 60)
    print("INFERENCE TEST")
    print("=" * 60)

    try:
        # Load the trained model
        print("\nLoading model...")
        model = load_model()
        print("Model loaded successfully")

        # Get the number of features the model expects
        n_features = model.n_features_in_
        print(f"Model expects {n_features} features")

        # Create a dummy input with correct number of features
        # Using random values as a test sample
        print("\nCreating dummy input...")
        dummy_input = np.random.randn(n_features)
        print(f"Dummy input shape: {dummy_input.shape}")

        # Run prediction
        print("\nRunning prediction...")
        prediction = predict(model, dummy_input)
        print(f"Prediction result: {prediction}")
        print(f"Predicted class: {prediction[0]}")

        # Test with multiple samples
        print("\nTesting with multiple samples...")
        dummy_batch = np.random.randn(5, n_features)
        predictions = predict(model, dummy_batch)
        print(f"Batch predictions: {predictions}")

        print("\n" + "=" * 60)
        print("INFERENCE TEST COMPLETED")
        print("=" * 60)

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("Please train the model first by running: python training/train.py")
    except ValueError as e:
        print(f"\nError: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
