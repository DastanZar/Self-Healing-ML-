"""
Training pipeline script for the machine learning system.

This script loads the infrastructure metrics dataset, trains a RandomForest model,
evaluates its performance, and saves the trained model.
"""

# Add project root to path for imports
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import logging
from pathlib import Path

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    auc,
    roc_curve
)
import matplotlib.pyplot as plt
from imblearn.over_sampling import SMOTE
import joblib

from training.data_loader import load_data

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def load_and_prepare_data() -> tuple[pd.DataFrame, pd.Series]:
    """
    Load the dataset and separate features from target.

    Returns:
        tuple: A tuple containing:
            - X (pd.DataFrame): Features (all columns except "Class")
            - y (pd.Series): Target variable ("Class" column)
    """
    logger.info("Loading dataset...")
    df = load_data()
    logger.info(f"Dataset loaded with shape: {df.shape}")

    # Separate features and target
    X = df.drop("Class", axis=1)
    y = df["Class"]

    logger.info(f"Features shape: {X.shape}")
    logger.info(f"Target distribution:\n{y.value_counts()}")

    return X, y


def train_model(X: pd.DataFrame, y: pd.Series) -> RandomForestClassifier:
    """
    Train a RandomForest classifier on the provided data.
    Uses class_weight='balanced' and SMOTE to handle class imbalance.

    Args:
        X: Features dataframe.
        y: Target series.

    Returns:
        RandomForestClassifier: The trained model.
    """
    logger.info("Splitting data into train and test sets...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y  # Maintain class distribution in splits
    )
    logger.info(f"Training set size: {len(X_train)}")
    logger.info(f"Test set size: {len(X_test)}")
    logger.info(f"Training class distribution before SMOTE:\n{y_train.value_counts()}")

    # Apply SMOTE only on training data to avoid data leakage
    logger.info("Applying SMOTE to handle class imbalance...")
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
    logger.info(f"Training class distribution after SMOTE:\n{pd.Series(y_train_resampled).value_counts()}")

    logger.info("Training RandomForest model with class_weight='balanced'...")
    model = RandomForestClassifier(
        n_estimators=100,
        class_weight='balanced',  # Handle class imbalance
        random_state=42,
        n_jobs=-1  # Use all available cores
    )
    model.fit(X_train_resampled, y_train_resampled)
    logger.info("Model training completed")

    # Store test data for evaluation
    model._X_test = X_test
    model._y_test = y_test

    return model


def evaluate_model(model: RandomForestClassifier) -> None:
    """
    Evaluate the trained model and print metrics.

    Args:
        model: The trained RandomForestClassifier.
    """
    # Create evaluation directory if it doesn't exist
    eval_dir = PROJECT_ROOT / "evaluation"
    if not eval_dir.exists():
        eval_dir.mkdir(parents=True, exist_ok=True)

    logger.info("Evaluating model...")

    X_test = model._X_test
    y_test = model._y_test

    y_pred = model.predict(X_test)
    y_proba = model.predict_proba(X_test)[:, 1]

    # Accuracy
    accuracy = accuracy_score(y_test, y_pred)
    logger.info(f"Accuracy: {accuracy:.4f}")
    print(f"\nAccuracy Score: {accuracy:.4f}")

    # Classification Report
    report = classification_report(y_test, y_pred)
    logger.info(f"Classification Report:\n{report}")
    print(f"\nClassification Report:\n{report}")

    # Confusion Matrix
    cm = confusion_matrix(y_test, y_pred)
    logger.info(f"Confusion Matrix:\n{cm}")
    print(f"\nConfusion Matrix:")
    print(f"  TN: {cm[0][0]:5d}  FP: {cm[0][1]:5d}")
    print(f"  FN: {cm[1][0]:5d}  TP: {cm[1][1]:5d}")

    # ROC-AUC Score
    roc_auc = roc_auc_score(y_test, y_proba)
    logger.info(f"ROC-AUC Score: {roc_auc:.4f}")
    print(f"\nROC-AUC Score: {roc_auc:.4f}")

    # Precision-Recall AUC
    precision_curve, recall_curve, _ = precision_recall_curve(y_test, y_proba)
    pr_auc = auc(recall_curve, precision_curve)
    logger.info(f"Precision-Recall AUC: {pr_auc:.4f}")
    print(f"Precision-Recall AUC: {pr_auc:.4f}")

    # Plot ROC Curve
    fpr, tpr, _ = roc_curve(y_test, y_proba)
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC Curve (AUC = {roc_auc:.4f})')
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Random Classifier')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('ROC Curve - Server Health Anomaly Detection')
    plt.legend(loc='lower right')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('evaluation/roc_curve.png', dpi=150)
    plt.close()
    logger.info("ROC curve saved to evaluation/roc_curve.png")
    print("ROC curve saved to evaluation/roc_curve.png")

    # Plot Precision-Recall Curve
    plt.figure(figsize=(8, 6))
    plt.plot(recall_curve, precision_curve, color='green', lw=2, label=f'PR Curve (AUC = {pr_auc:.4f})')
    plt.axhline(y=y_test.mean(), color='gray', linestyle='--', label=f'Baseline (Prevalence = {y_test.mean():.4f})')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('Recall')
    plt.ylabel('Precision')
    plt.title('Precision-Recall Curve - Server Health Anomaly Detection')
    plt.legend(loc='lower left')
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('evaluation/pr_curve.png', dpi=150)
    plt.close()
    logger.info("Precision-Recall curve saved to evaluation/pr_curve.png")
    print("Precision-Recall curve saved to evaluation/pr_curve.png")


def tune_threshold(model: RandomForestClassifier) -> float:
    """
    Tune classification threshold to optimize fraud detection.
    Uses model.predict_proba() to test multiple thresholds.

    Args:
        model: The trained RandomForestClassifier.

    Returns:
        float: The best threshold value.
    """
    X_test = model._X_test
    y_test = model._y_test

    # Get prediction probabilities
    y_proba = model.predict_proba(X_test)[:, 1]

    logger.info("Tuning classification threshold...")
    print("\n" + "=" * 60)
    print("THRESHOLD TUNING")
    print("=" * 60)

    best_threshold = 0.5
    best_recall = 0
    best_metrics = {}

    # Test thresholds from 0.1 to 0.9
    thresholds = np.arange(0.1, 0.9, 0.05)

    print(f"\n{'Threshold':<12} {'Precision':<12} {'Recall':<12} {'F1-Score':<12}")
    print("-" * 48)

    for threshold in thresholds:
        y_pred = (y_proba >= threshold).astype(int)

        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)

        print(f"{threshold:<12.2f} {precision:<12.4f} {recall:<12.4f} {f1:<12.4f}")

        # Find best threshold: maximize recall while keeping precision >= 0.3
        if recall > best_recall and precision >= 0.3:
            best_recall = recall
            best_threshold = threshold
            best_metrics = {
                'precision': precision,
                'recall': recall,
                'f1': f1
            }

    print("-" * 48)
    print(f"\nBest Threshold: {best_threshold:.2f}")
    print(f"Metrics at Best Threshold:")
    print(f"  - Precision: {best_metrics.get('precision', 0):.4f}")
    print(f"  - Recall: {best_metrics.get('recall', 0):.4f}")
    print(f"  - F1-Score: {best_metrics.get('f1', 0):.4f}")
    print("=" * 60)

    logger.info(f"Best threshold: {best_threshold:.2f}")
    logger.info(f"Metrics at best threshold: {best_metrics}")

    return best_threshold


# Get project root (parent of training directory)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def save_model(model: RandomForestClassifier, filepath: str | None = None) -> None:
    """
    Save the trained model to a file using joblib.

    Args:
        model: The trained model to save.
        filepath: Path where to save the model. Defaults to PROJECT_ROOT/models/model_v1.pkl.
    """
    # Use default path if not specified
    if filepath is None:
        filepath = PROJECT_ROOT / "models" / "model_v1.pkl"
    else:
        # Resolve to absolute path relative to project root
        filepath = PROJECT_ROOT / filepath

    # Create models directory if it doesn't exist
    models_dir = filepath.parent
    if not models_dir.exists():
        logger.info(f"Creating models directory at {models_dir}...")
        models_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Models directory created")

    logger.info(f"Saving model to {filepath}...")
    joblib.dump(model, filepath)
    logger.info(f"Model saved successfully to {filepath}")


def main() -> None:
    """
    Main function to run the entire training pipeline.
    """
    print("=" * 60)
    print("TRAINING PIPELINE")
    print("=" * 60)

    try:
        # Step 1: Load and prepare data
        X, y = load_and_prepare_data()

        # Step 2: Train the model
        model = train_model(X, y)

        # Step 3: Evaluate the model
        evaluate_model(model)

        # Step 4: Tune classification threshold
        best_threshold = tune_threshold(model)

        # Step 5: Save the model
        save_model(model)

        print("\n" + "=" * 60)
        print("TRAINING PIPELINE COMPLETED SUCCESSFULLY")
        print(f"Best threshold for anomaly detection: {best_threshold:.2f}")
        print("=" * 60)

    except FileNotFoundError as e:
        logger.error(f"Data file not found: {e}")
        print(f"Error: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")
        print(f"Error: {e}")
        raise


if __name__ == "__main__":
    main()
