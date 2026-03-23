"""
Demo script showing the integrated ML inference pipeline.

This script demonstrates how to use real model predictions
in the self-healing system.
"""

import logging
import sys
import os

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


def generate_realistic_input() -> dict:
    """
    Generate realistic system input data with correct features.

    Returns:
        Dictionary with cpu, memory, latency, error_rate.
    """
    import random

    # Generate realistic system metrics
    # Normal operation: low CPU, moderate memory, low latency, low error rate
    # Anomaly: high CPU, high memory, high latency, high error rate

    # Randomly choose normal or anomalous
    is_anomaly = random.random() < 0.05  # 5% chance of anomaly

    if is_anomaly:
        cpu = random.uniform(70, 100)
        memory = random.uniform(70, 95)
        latency = random.uniform(200, 500)
        error_rate = random.uniform(0.05, 0.2)
    else:
        cpu = random.uniform(10, 60)
        memory = random.uniform(20, 60)
        latency = random.uniform(50, 150)
        error_rate = random.uniform(0.001, 0.02)

    return {
        "cpu": round(cpu, 2),
        "memory": round(memory, 2),
        "latency": round(latency, 2),
        "error_rate": round(error_rate, 4)
    }


def demo_single_prediction():
    """
    Demonstrate a single prediction with real model inference.
    """
    print("=" * 60)
    print("DEMO: Single Prediction with Real ML Model")
    print("=" * 60)

    # Initialize the inference system (loads model at startup)
    from self_healing_system.services.inference_service.prediction_service import (
        initialize_inference_system,
        run_prediction_pipeline
    )

    # Initialize - loads model once
    initialize_inference_system()

    # Generate realistic input
    input_data = generate_realistic_input()
    print(f"\nInput data: {input_data}")

    # Run the complete pipeline
    result = run_prediction_pipeline(input_data)

    print(f"\nResult: {result}")
    print("=" * 60)


def demo_batch_predictions(n: int = 5):
    """
    Demonstrate multiple predictions.
    """
    print("=" * 60)
    print(f"DEMO: Batch Predictions ({n} samples)")
    print("=" * 60)

    from self_healing_system.services.inference_service.prediction_service import (
        initialize_inference_system,
        run_prediction_pipeline
    )

    # Initialize
    initialize_inference_system()

    for i in range(n):
        print(f"\n--- Sample {i + 1} ---")
        input_data = generate_realistic_input()
        print(f"Input: {input_data}")

        # Just get prediction and log (not full pipeline for batch)
        from self_healing_system.services.inference_service.inference_engine import run_inference
        from self_healing_system.core.logger import log_prediction

        prediction = run_inference(input_data)
        log_prediction(input_data, prediction)
        print(f"Prediction: {prediction}")

    # After batch, show computed metrics
    print("\n--- Final Metrics after batch ---")
    from self_healing_system.services.monitoring_service.monitor import compute_metrics
    metrics = compute_metrics("logs/predictions.jsonl")
    print(f"Metrics: {metrics}")

    print("=" * 60)


def main():
    """
    Main demo function.
    """
    print("\nSelf-Healing ML System - Real Inference Demo")
    print("=" * 60)

    try:
        # Run single prediction demo
        demo_single_prediction()

        # Run batch predictions demo
        demo_batch_predictions(3)

        print("\nDemo completed successfully!")

    except FileNotFoundError as e:
        print(f"\nError: {e}")
        print("\nPlease train the model first by running:")
        print("  python training/train.py")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
