"""
Data loader module for loading and inspecting the infrastructure metrics dataset.

This module provides functionality to load the infrastructure metrics dataset
from a CSV file and display its properties.
"""

import pandas as pd
from pathlib import Path


def load_data(filepath: str = "data/infra_metrics.csv") -> pd.DataFrame:
    """
    Load the infrastructure metrics dataset from a CSV file.

    Args:
        filepath: Path to the CSV file. Defaults to "data/infra_metrics.csv".

    Returns:
        pd.DataFrame: The loaded dataset.

    Raises:
        FileNotFoundError: If the specified file does not exist.
    """
    path = Path(filepath)

    if not path.exists():
        raise FileNotFoundError(
            f"Data file not found: {filepath}. "
            "Please ensure the file exists and the path is correct."
        )

    df = pd.read_csv(filepath)
    return df


def print_dataset_summary(df: pd.DataFrame) -> None:
    """
    Print a summary of the dataset including shape, columns, and class distribution.

    Args:
        df: The pandas DataFrame to summarize.
    """
    print("=" * 60)
    print("DATASET SUMMARY")
    print("=" * 60)

    # Dataset shape
    print(f"\nShape: {df.shape[0]} rows x {df.shape[1]} columns")

    # Column names
    print("\nColumn Names:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")

    # Class distribution
    print("\nClass Distribution:")
    class_counts = df["Class"].value_counts()
    for class_label, count in class_counts.items():
        percentage = (count / len(df)) * 100
        print(f"  Class {class_label}: {count} ({percentage:.2f}%)")

    print("=" * 60)


def main() -> None:
    """Main function to load and display the dataset summary."""
    try:
        df = load_data()
        print_dataset_summary(df)
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
