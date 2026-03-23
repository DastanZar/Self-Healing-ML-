"""
Prediction service that integrates ML inference with logging and monitoring.

This service provides the complete pipeline:
input → prediction → log → monitor → decide → act
"""

import logging
from typing import Any, Dict, Optional

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from self_healing_system.core.logger import log_prediction
from self_healing_system.services.monitoring_service.monitor import compute_metrics
from self_healing_system.services.intelligence_service.fast_decision_engine import FastDecisionEngine
from self_healing_system.services.action_service.action_engine import ActionEngine

logger = logging.getLogger(__name__)


def run_prediction_pipeline(input_data: Dict[str, float]) -> Dict[str, Any]:
    """
    Run the complete prediction pipeline.
    Uses the model that was loaded during initialize_inference_system().

    Flow: input → prediction → log → monitor → decide → act

    Args:
        input_data: Dictionary with system metrics (cpu, memory, latency, error_rate).

    Returns:
        Dictionary containing prediction, metrics, decision, and action results.

    Raises:
        RuntimeError: If model is not initialized. Call initialize_inference_system() first.
    """
    from self_healing_system.services.inference_service.inference_engine import (
        run_inference,
        is_model_initialized
    )

    # Safety check: ensure model was initialized
    if not is_model_initialized():
        raise RuntimeError(
            "Model not initialized. Call initialize_inference_system() before making predictions."
        )

    logger.info("=" * 50)
    logger.info("Starting prediction pipeline")
    logger.info("=" * 50)

    # Step 1: Run model inference (uses already loaded model)
    prediction = run_inference(input_data)

    # Step 2: Log the prediction
    logger.info("Logging prediction...")
    log_prediction(input_data, prediction)
    print(f"Logged prediction: {prediction}")

    # Step 3: Compute metrics (monitoring)
    logger.info("Computing metrics...")
    metrics = compute_metrics("logs/predictions.jsonl")

    # Step 4: Make decision
    logger.info("Making decision...")
    decision = FastDecisionEngine().decide(metrics)
    print(f"Decision: {decision}")

    # Step 5: Execute action
    logger.info("Executing action...")
    action_result = ActionEngine().execute(decision, metrics)

    logger.info("=" * 50)
    logger.info("Prediction pipeline completed")
    logger.info("=" * 50)

    return {
        "prediction": prediction,
        "metrics": metrics,
        "decision": decision,
        "action": action_result
    }


def initialize_inference_system() -> None:
    """
    Initialize the inference system by loading the model at startup.
    
    Raises:
        RuntimeError: If model initialization fails.
    """
    from self_healing_system.services.inference_service.inference_engine import load_inference_model

    logger.info("Initializing inference system...")

    try:
        load_inference_model()
        logger.info("Model loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Model initialization failed: {e}")
        raise RuntimeError(f"Model initialization failed: {e}") from e
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        raise RuntimeError(f"Model initialization failed: {e}") from e
