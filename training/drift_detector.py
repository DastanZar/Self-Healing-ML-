"""
Data Drift Detection Module for ML Models.

This module detects data drift by comparing training data with new incoming data
using statistical tests.
"""

import logging
from typing import Dict, List, Any

import pandas as pd
import numpy as np
from scipy.stats import ks_2samp

logger = logging.getLogger(__name__)


def detect_drift(
    reference_data: pd.DataFrame,
    current_data: pd.DataFrame,
    threshold: float = 0.1,
    features: List[str] | None = None
) -> Dict[str, Any]:
    """
    Detect data drift using Kolmogorov-Smirnov test.

    Args:
        reference_data: Training dataset (baseline).
        current_data: New incoming dataset to check for drift.
        threshold: KS statistic threshold for drift detection. Default: 0.1.
        features: List of features to check. If None, all numerical features are used.

    Returns:
        Dictionary containing drift detection results.
    """
    logger.info("Starting drift detection...")

    if features is None:
        # Use all numerical features
        features = reference_data.select_dtypes(include=[np.number]).columns.tolist()

    drift_results = {
        "total_features": len(features),
        "drifted_features": [],
        "features": {}
    }

    for feature in features:
        if feature not in reference_data.columns:
            logger.warning(f"Feature '{feature}' not found in reference data")
            continue

        if feature not in current_data.columns:
            logger.warning(f"Feature '{feature}' not found in current data")
            continue

        ref_values = reference_data[feature].dropna()
        cur_values = current_data[feature].dropna()

        if len(ref_values) < 2 or len(cur_values) < 2:
            logger.warning(f"Insufficient data for feature '{feature}'")
            continue

        # Kolmogorov-Smirnov test
        ks_statistic, p_value = ks_2samp(ref_values, cur_values)

        feature_result = {
            "ks_statistic": float(ks_statistic),
            "p_value": float(p_value),
            "drift_detected": ks_statistic > threshold,
            "reference_mean": float(ref_values.mean()),
            "current_mean": float(cur_values.mean()),
            "reference_std": float(ref_values.std()),
            "current_std": float(cur_values.std())
        }

        drift_results["features"][feature] = feature_result

        if feature_result["drift_detected"]:
            drift_results["drifted_features"].append(feature)
            logger.warning(
                f"DRIFT DETECTED in feature '{feature}': "
                f"KS statistic = {ks_statistic:.4f} (threshold = {threshold})"
            )

    # Summary
    drift_results["drift_percentage"] = len(drift_results["drifted_features"]) / len(features)
    drift_results["has_drift"] = len(drift_results["drifted_features"]) > 0

    logger.info(
        f"Drift detection complete: {len(drift_results['drifted_features'])}/{len(features)} "
        f"features show drift ({drift_results['drift_percentage']*100:.1f}%)"
    )

    return drift_results


def print_drift_report(drift_results: Dict[str, Any]) -> None:
    """
    Print a formatted drift detection report.

    Args:
        drift_results: Dictionary containing drift detection results.
    """
    print("\n" + "=" * 60)
    print("DATA DRIFT REPORT")
    print("=" * 60)

    print(f"\nTotal features analyzed: {drift_results['total_features']}")
    print(f"Features with drift: {len(drift_results['drifted_features'])}")
    print(f"Drift percentage: {drift_results['drift_percentage']*100:.1f}%")
    print(f"Drift detected: {drift_results['has_drift']}")

    if drift_results["drifted_features"]:
        print("\n--- Drifted Features ---")
        for feature in drift_results["drifted_features"]:
            feat_data = drift_results["features"][feature]
            print(f"  {feature}:")
            print(f"    KS Statistic: {feat_data['ks_statistic']:.4f}")
            print(f"    P-Value: {feat_data['p_value']:.4f}")
            print(f"    Ref Mean: {feat_data['reference_mean']:.4f}")
            print(f"    Current Mean: {feat_data['current_mean']:.4f}")

    print("=" * 60)


def get_drift_summary(drift_results: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get a summary of drift results.

    Args:
        drift_results: Dictionary containing drift detection results.

    Returns:
        Dictionary with summary information.
    """
    return {
        "has_drift": drift_results["has_drift"],
        "drift_percentage": drift_results["drift_percentage"],
        "drifted_features": drift_results["drifted_features"],
        "num_drifted": len(drift_results["drifted_features"])
    }
