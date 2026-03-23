import json
import os
from collections import deque


def compute_metrics(log_file: str, window_size: int = 50) -> dict:
    if not os.path.exists(log_file):
        print(f"[Monitor] anomaly_rate=0.000 drift_score=0.000 latency=0.000 (file not found)")
        return {"anomaly_rate": 0.0, "drift_score": 0.0, "latency": 0.0}

    entries = deque(maxlen=window_size)
    with open(log_file, "r") as f:
        for line in f:
            if line.strip():
                entries.append(json.loads(line))

    if not entries:
        print(f"[Monitor] anomaly_rate=0.000 drift_score=0.000 latency=0.000 (empty file)")
        return {"anomaly_rate": 0.0, "drift_score": 0.0, "latency": 0.0}

    anomaly_rate = sum(1 for e in entries if e.get("prediction") == 1) / len(entries)

    latency_values = [e.get("input", {}).get("latency", 0) for e in entries]
    latency = sum(latency_values) / len(latency_values) if latency_values else 0.0

    half = len(entries) // 2
    if half < 1:
        drift_score = 0.0
    else:
        first_half = list(entries)[:half]
        second_half = list(entries)[half:]

        first_half_cpu = [e.get("input", {}).get("cpu", 0) for e in first_half]
        second_half_cpu = [e.get("input", {}).get("cpu", 0) for e in second_half]

        first_mean = sum(first_half_cpu) / len(first_half_cpu)
        second_mean = sum(second_half_cpu) / len(second_half_cpu)

        if first_mean != 0:
            drift_score = abs(second_mean - first_mean) / abs(first_mean)
        else:
            drift_score = 0.0

    print(f"[Monitor] anomaly_rate={anomaly_rate:.3f} drift_score={drift_score:.3f} latency={latency:.3f}")

    return {
        "anomaly_rate": anomaly_rate,
        "drift_score": drift_score,
        "latency": latency
    }
