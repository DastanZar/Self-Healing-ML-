"""
Model Monitoring Module for ML Predictions.

This module tracks model performance metrics over time including
prediction counts, fraud detection rate, precision, and recall.
"""

import logging
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import deque

import numpy as np

logger = logging.getLogger(__name__)

# Configuration
PROJECT_ROOT = Path(__file__).resolve().parent.parent
METRICS_FILE = PROJECT_ROOT / "logs" / "model_metrics.jsonl"
CSV_METRICS_FILE = PROJECT_ROOT / "logs" / "model_metrics.csv"
WINDOW_SIZE = 100  # Rolling window for metrics


class ModelMonitor:
    """Monitor for tracking ML model performance metrics."""

    def __init__(self, window_size: int = WINDOW_SIZE):
        """
        Initialize the model monitor.

        Args:
            window_size: Number of predictions to keep in rolling window.
        """
        self.window_size = window_size
        self.predictions = deque(maxlen=window_size)
        self.total_predictions = 0
        self.total_fraud_detected = 0

        logger.info(f"ModelMonitor initialized with window_size={window_size}")

    def record_prediction(
        self,
        prediction: int,
        actual_label: Optional[int] = None
    ) -> None:
        """
        Record a single prediction.

        Args:
            prediction: Model prediction (0 or 1).
            actual_label: Actual label if available (for evaluation).
        """
        self.total_predictions += 1

        if prediction == 1:
            self.total_fraud_detected += 1

        # Store prediction with metadata
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "prediction": prediction,
            "actual": actual_label
        }
        self.predictions.append(record)

        logger.debug(f"Recorded prediction: {prediction}")

    def get_prediction_counts(self) -> Dict[str, int]:
        """
        Get prediction counts.

        Returns:
            Dictionary with total and fraud counts.
        """
        return {
            "total_predictions": self.total_predictions,
            "total_fraud_detected": self.total_fraud_detected,
            "window_predictions": len(self.predictions),
            "window_fraud_detected": sum(1 for p in self.predictions if p["prediction"] == 1)
        }

    def get_fraud_detection_rate(self) -> float:
        """
        Calculate fraud detection rate.

        Returns:
            Float between 0 and 1.
        """
        if self.total_predictions == 0:
            return 0.0
        return self.total_fraud_detected / self.total_predictions

    def get_precision(self) -> float:
        """
        Calculate precision (requires actual labels).

        Returns:
            Precision score or 0.0 if no labels available.
        """
        predictions_with_labels = [
            p for p in self.predictions
            if p["actual"] is not None
        ]

        if not predictions_with_labels:
            return 0.0

        true_positives = sum(
            1 for p in predictions_with_labels
            if p["prediction"] == 1 and p["actual"] == 1
        )
        predicted_positives = sum(
            1 for p in predictions_with_labels
            if p["prediction"] == 1
        )

        if predicted_positives == 0:
            return 0.0

        return true_positives / predicted_positives

    def get_recall(self) -> float:
        """
        Calculate recall (requires actual labels).

        Returns:
            Recall score or 0.0 if no labels available.
        """
        predictions_with_labels = [
            p for p in self.predictions
            if p["actual"] is not None
        ]

        if not predictions_with_labels:
            return 0.0

        true_positives = sum(
            1 for p in predictions_with_labels
            if p["prediction"] == 1 and p["actual"] == 1
        )
        actual_positives = sum(
            1 for p in predictions_with_labels
            if p["actual"] == 1
        )

        if actual_positives == 0:
            return 0.0

        return true_positives / actual_positives

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all current metrics.

        Returns:
            Dictionary containing all tracked metrics.
        """
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "prediction_counts": self.get_prediction_counts(),
            "fraud_detection_rate": self.get_fraud_detection_rate(),
            "precision": self.get_precision(),
            "recall": self.get_recall()
        }

        return metrics

    def log_metrics(self) -> None:
        """Log current metrics."""
        metrics = self.get_metrics()

        logger.info("=" * 50)
        logger.info("MODEL METRICS")
        logger.info("=" * 50)
        logger.info(f"Total Predictions: {metrics['prediction_counts']['total_predictions']}")
        logger.info(f"Fraud Detected: {metrics['prediction_counts']['total_fraud_detected']}")
        logger.info(f"Fraud Detection Rate: {metrics['fraud_detection_rate']:.4f}")
        logger.info(f"Precision: {metrics['precision']:.4f}")
        logger.info(f"Recall: {metrics['recall']:.4f}")
        logger.info("=" * 50)

    def save_metrics(self) -> None:
        """Save metrics to JSON and CSV files."""
        metrics = self.get_metrics()

        # Save to JSONL
        METRICS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(METRICS_FILE, "a") as f:
            f.write(json.dumps(metrics) + "\n")

        # Save to CSV
        csv_exists = CSV_METRICS_FILE.exists()

        with open(CSV_METRICS_FILE, "a", newline="") as f:
            fieldnames = [
                "timestamp",
                "total_predictions",
                "total_fraud_detected",
                "fraud_detection_rate",
                "precision",
                "recall"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if not csv_exists:
                writer.writeheader()

            writer.writerow({
                "timestamp": metrics["timestamp"],
                "total_predictions": metrics["prediction_counts"]["total_predictions"],
                "total_fraud_detected": metrics["prediction_counts"]["total_fraud_detected"],
                "fraud_detection_rate": metrics["fraud_detection_rate"],
                "precision": metrics["precision"],
                "recall": metrics["recall"]
            })

        logger.info(f"Metrics saved to {METRICS_FILE} and {CSV_METRICS_FILE}")

    def run(self) -> Dict[str, Any]:
        """
        Run monitoring cycle: log and save metrics.

        Returns:
            Dictionary containing current metrics.
        """
        self.log_metrics()
        self.save_metrics()

        return self.get_metrics()


# Global monitor instance
_monitor: Optional[ModelMonitor] = None


def get_monitor() -> ModelMonitor:
    """
    Get or create the global monitor instance.

    Returns:
        ModelMonitor instance.
    """
    global _monitor
    if _monitor is None:
        _monitor = ModelMonitor()
    return _monitor


def record_prediction(
    prediction: int,
    actual_label: Optional[int] = None
) -> None:
    """
    Record a prediction using the global monitor.

    Args:
        prediction: Model prediction (0 or 1).
        actual_label: Actual label if available.
    """
    get_monitor().record_prediction(prediction, actual_label)


def get_metrics() -> Dict[str, Any]:
    """
    Get current metrics from the global monitor.

    Returns:
        Dictionary containing all tracked metrics.
    """
    return get_monitor().get_metrics()


def log_metrics() -> None:
    """Log current metrics."""
    get_monitor().log_metrics()


def save_metrics() -> None:
    """Save metrics to files."""
    get_monitor().save_metrics()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Demo: simulate predictions
    monitor = ModelMonitor()

    # Simulate some predictions
    import random
    for i in range(50):
        pred = random.choices([0, 1], weights=[95, 5])[0]
        actual = random.choices([0, 1], weights=[95, 5])[0]
        monitor.record_prediction(pred, actual)

    # Run monitoring
    monitor.run()
