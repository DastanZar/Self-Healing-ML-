"""
Generate synthetic infrastructure metrics dataset for server health monitoring.

This script creates a dataset with 10,000 rows of synthetic server metrics,
with 85% normal (HEALTHY) and 15% anomalous (ANOMALY) samples.
"""

import numpy as np
import pandas as pd
from pathlib import Path


def generate_infra_data(n_samples: int = 10000, anomaly_fraction: float = 0.15, random_state: int = 42) -> pd.DataFrame:
    """
    Generate synthetic infrastructure metrics dataset.

    Args:
        n_samples: Total number of samples to generate.
        anomaly_fraction: Fraction of samples that should be anomalies.
        random_state: Random seed for reproducibility.

    Returns:
        DataFrame with columns: cpu, memory, latency, error_rate, Class
    """
    np.random.seed(random_state)
    
    n_anomalies = int(n_samples * anomaly_fraction)
    n_normal = n_samples - n_anomalies
    
    # Generate normal samples (Class 0)
    # CPU: 5-30% utilization (typical healthy server)
    cpu_normal = np.random.beta(a=2, b=8, size=n_normal) * 30 + 5
    # Memory: 20-60% utilization
    memory_normal = np.random.beta(a=3, b=4, size=n_normal) * 40 + 20
    # Latency: 10-100ms (low latency)
    latency_normal = np.random.exponential(scale=20, size=n_normal) + 10
    # Error rate: 0-0.5% (very low)
    error_rate_normal = np.random.beta(a=1, b=100, size=n_normal) * 0.005
    
    # Generate anomalous samples (Class 1)
    # CPU: 70-100% (high utilization)
    cpu_anomaly = np.random.beta(a=8, b=2, size=n_anomalies) * 30 + 70
    # Memory: 80-100% (high memory usage)
    memory_anomaly = np.random.beta(a=9, b=1, size=n_anomalies) * 20 + 80
    # Latency: 500-2000ms (high latency)
    latency_anomaly = np.random.exponential(scale=500, size=n_anomalies) + 500
    # Error rate: 5-30% (high error rate)
    error_rate_anomaly = np.random.beta(a=2, b=5, size=n_anomalies) * 0.25 + 0.05
    
    # Combine data
    cpu = np.concatenate([cpu_normal, cpu_anomaly])
    memory = np.concatenate([memory_normal, memory_anomaly])
    latency = np.concatenate([latency_normal, latency_anomaly])
    error_rate = np.concatenate([error_rate_normal, error_rate_anomaly])
    class_labels = np.concatenate([np.zeros(n_normal), np.ones(n_anomalies)])
    
    # Clip values to realistic ranges
    cpu = np.clip(cpu, 0, 100)
    memory = np.clip(memory, 0, 100)
    latency = np.clip(latency, 0, 10000)  # cap at 10 seconds
    error_rate = np.clip(error_rate, 0, 1)
    
    # Create DataFrame
    df = pd.DataFrame({
        'cpu': cpu,
        'memory': memory,
        'latency': latency,
        'error_rate': error_rate,
        'Class': class_labels.astype(int)
    })
    
    # Shuffle the dataset
    df = df.sample(frac=1, random_state=random_state).reset_index(drop=True)
    
    return df


def main():
    """Generate and save the infrastructure metrics dataset."""
    print("Generating synthetic infrastructure metrics dataset...")
    
    df = generate_infra_data()
    
    # Ensure data directory exists
    data_dir = Path(__file__).parent
    data_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = data_dir / "infra_metrics.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Dataset generated successfully!")
    print(f"Shape: {df.shape}")
    print(f"Saved to: {output_path}")
    
    # Print summary statistics
    print("\nDataset Summary:")
    print("=" * 50)
    print(f"Total samples: {len(df)}")
    print(f"Normal samples (Class 0): {(df['Class'] == 0).sum()} ({(df['Class'] == 0).mean():.1%})")
    print(f"Anomalous samples (Class 1): {(df['Class'] == 1).sum()} ({(df['Class'] == 1).mean():.1%})")
    
    print("\nFeature Statistics (Normal):")
    normal = df[df['Class'] == 0]
    print(f"  CPU: {normal['cpu'].mean():.1f}% ± {normal['cpu'].std():.1f}%")
    print(f"  Memory: {normal['memory'].mean():.1f}% ± {normal['memory'].std():.1f}%")
    print(f"  Latency: {normal['latency'].mean():.1f}ms ± {normal['latency'].std():.1f}ms")
    print(f"  Error Rate: {normal['error_rate'].mean():.4f} ± {normal['error_rate'].std():.4f}")
    
    print("\nFeature Statistics (Anomaly):")
    anomaly = df[df['Class'] == 1]
    print(f"  CPU: {anomaly['cpu'].mean():.1f}% ± {anomaly['cpu'].std():.1f}%")
    print(f"  Memory: {anomaly['memory'].mean():.1f}% ± {anomaly['memory'].std():.1f}%")
    print(f"  Latency: {anomaly['latency'].mean():.1f}ms ± {anomaly['latency'].std():.1f}ms")
    print(f"  Error Rate: {anomaly['error_rate'].mean():.4f} ± {anomaly['error_rate'].std():.4f}")
    
    print("=" * 50)


if __name__ == "__main__":
    main()