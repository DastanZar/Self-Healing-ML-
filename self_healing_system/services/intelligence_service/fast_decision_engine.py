class FastDecisionEngine:
    def decide(self, metrics: dict) -> str:
        anomaly_rate = metrics.get("anomaly_rate", 0)
        drift_score = metrics.get("drift_score", 0)
        latency = metrics.get("latency", 0)

        if anomaly_rate > 0.3:
            decision = "INVESTIGATE"
        elif drift_score > 0.2:
            decision = "RETRAIN"
        elif latency > 200:
            decision = "ALERT"
        else:
            decision = "HEALTHY"

        return decision