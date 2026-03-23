from self_healing_system.services.intelligence_service.fast_decision_engine import FastDecisionEngine


def should_trigger_deep_analysis(decision: str) -> bool:
    return decision == "INVESTIGATE"


def run_decision_loop():
    engine = FastDecisionEngine()

    metrics = {
        "anomaly_rate": 0.35,
        "drift_score": 0.1,
        "latency": 120
    }

    print(f"[Controller] Incoming metrics: {metrics}")

    decision = engine.decide(metrics)

    print(f"[Controller] Decision: {decision}")

    if should_trigger_deep_analysis(decision):
        print("[Controller] Triggering deep analysis (HLLM)...")
    else:
        print("[Controller] No deep analysis required.")


if __name__ == "__main__":
    run_decision_loop()

if __name__ == "__main__":
    run_decision_loop()
