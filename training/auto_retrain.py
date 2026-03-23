"""
Automated Retraining Pipeline for ML Models.

This module provides automated model retraining based on performance metrics
and data drift detection.
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_score,
    recall_score,
    f1_score
)
from imblearn.over_sampling import SMOTE
import joblib

from training.data_loader import load_data
from training.drift_detector import detect_drift

logger = logging.getLogger(__name__)

# Configuration
RECALL_THRESHOLD = 0.8
DRIFT_THRESHOLD = 0.1
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def get_current_model_version() -> int:
    """
    Get the current model version number.

    Returns:
        int: Current version number (1 if no models exist).
    """
    models_dir = PROJECT_ROOT / "models"
    if not models_dir.exists():
        return 1

    model_files = list(models_dir.glob("model_v*.pkl"))
    if not model_files:
        return 1

    versions = []
    for f in model_files:
        try:
            v = int(f.stem.split("_v")[1])
            versions.append(v)
        except (IndexError, ValueError):
            continue

    return max(versions) if versions else 1


def evaluate_current_model(model_path: str) -> Dict[str, float]:
    """
    Evaluate the current model on recent data.

    Args:
        model_path: Path to the model file.

    Returns:
        Dictionary containing evaluation metrics.
    """
    logger.info(f"Evaluating current model: {model_path}")

    # Load model
    model = joblib.load(model_path)

    # Load and prepare data
    df = load_data()
    X = df.drop("Class", axis=1)
    y = df["Class"]

    # Split data
    _, X_test, _, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Evaluate
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0)
    }

    logger.info(f"Current model metrics: {metrics}")
    return metrics


def check_drift(reference_data: pd.DataFrame, current_data: pd.DataFrame) -> bool:
    """
    Check if data drift is detected.

    Args:
        reference_data: Reference (training) dataset.
        current_data: Current dataset to check.

    Returns:
        bool: True if drift is detected.
    """
    logger.info("Checking for data drift...")

    drift_results = detect_drift(
        reference_data,
        current_data,
        threshold=DRIFT_THRESHOLD
    )

    return drift_results["has_drift"]


def should_retrain(
    current_metrics: Dict[str, float],
    has_drift: bool
) -> tuple[bool, str]:
    """
    Determine if retraining should be triggered.

    Args:
        current_metrics: Current model metrics.
        has_drift: Whether data drift is detected.

    Returns:
        Tuple of (should_retrain, reason).
    """
    recall = current_metrics.get("recall", 0)

    if has_drift:
        return True, f"Data drift detected (drift_threshold={DRIFT_THRESHOLD})"

    if recall < RECALL_THRESHOLD:
        return True, f"Recall below threshold ({recall:.4f} < {RECALL_THRESHOLD})"

    return False, "No retraining needed"


def retrain_model(new_version: int) -> Dict[str, Any]:
    """
    Retrain the model with fresh data.

    Args:
        new_version: Version number for the new model.

    Returns:
        Dictionary containing new model metrics.
    """
    logger.info(f"Retraining model to version {new_version}...")

    # Load fresh data
    df = load_data()
    X = df.drop("Class", axis=1)
    y = df["Class"]

    logger.info(f"Training data shape: {X.shape}")
    logger.info(f"Class distribution:\n{y.value_counts()}")

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Apply SMOTE
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

    # Train model
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train_resampled, y_train_resampled)

    # Evaluate
    y_pred = model.predict(X_test)

    metrics = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, zero_division=0),
        "recall": recall_score(y_test, y_pred, zero_division=0),
        "f1": f1_score(y_test, y_pred, zero_division=0)
    }

    # Save new model
    model_path = PROJECT_ROOT / "models" / f"model_v{new_version}.pkl"
    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)

    logger.info(f"New model saved to {model_path}")
    logger.info(f"New model metrics: {metrics}")

    return metrics


def run_auto_retraining() -> Dict[str, Any]:
    """
    Run the automated retraining pipeline.

    Returns:
        Dictionary containing retraining results.
    """
    logger.info("Starting automated retraining check...")

    results = {
        "timestamp": datetime.utcnow().isoformat(),
        "retraining_triggered": False,
        "reason": "",
        "previous_metrics": {},
        "new_metrics": {},
        "new_version": 1
    }

    # Get current model version
    current_version = get_current_model_version()
    model_path = PROJECT_ROOT / "models" / f"model_v{current_version}.pkl"

    if not model_path.exists():
        logger.warning("No existing model found. Training initial model.")
        new_metrics = retrain_model(1)
        results["retraining_triggered"] = True
        results["reason"] = "Initial model training"
        results["new_metrics"] = new_metrics
        results["new_version"] = 1
        return results

    # Evaluate current model
    current_metrics = evaluate_current_model(str(model_path))
    results["previous_metrics"] = current_metrics

    # Load data for drift detection
    df = load_data()
    X = df.drop("Class", axis=1)
    y = df["Class"]

    # Check for drift (comparing recent data vs full dataset)
    # Using last 20% as "current" data
    X_current = X.iloc[-int(len(X) * 0.2):]
    X_reference = X.iloc[:-int(len(X) * 0.2)]

    has_drift = check_drift(X_reference, X_current)

    # Determine if retraining is needed
    should_retrain_flag, reason = should_retrain(current_metrics, has_drift)

    results["drift_detected"] = has_drift

    if should_retrain_flag:
        logger.info(f"Retraining triggered: {reason}")

        new_version = current_version + 1
        new_metrics = retrain_model(new_version)

        results["retraining_triggered"] = True
        results["reason"] = reason
        results["new_metrics"] = new_metrics
        results["new_version"] = new_version
    else:
        logger.info(f"No retraining needed: {reason}")

    # Save retraining log
    log_path = PROJECT_ROOT / "logs" / "retraining_log.jsonl"
    log_path.parent.mkdir(parents=True, exist_ok=True)

    with open(log_path, "a") as f:
        f.write(json.dumps(results) + "\n")

    return results


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )

    results = run_auto_retraining()

    print("\n" + "=" * 60)
    print("AUTO RETRAINING RESULTS")
    print("=" * 60)
    print(f"Retraining triggered: {results['retraining_triggered']}")
    print(f"Reason: {results['reason']}")
    if results["previous_metrics"]:
        print(f"Previous metrics: {results['previous_metrics']}")
    if results["new_metrics"]:
        print(f"New metrics: {results['new_metrics']}")
    print(f"New model version: v{results['new_version']}")
    print("=" * 60)
