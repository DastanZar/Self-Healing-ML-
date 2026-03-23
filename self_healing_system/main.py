from self_healing_system.services.monitoring_service.monitor import compute_metrics
from self_healing_system.services.intelligence_service.fast_decision_engine import FastDecisionEngine
from self_healing_system.services.action_service.action_engine import ActionEngine


def main():
    metrics = compute_metrics("logs/predictions.jsonl")
    print(f"Metrics: {metrics}")

    decision = FastDecisionEngine().decide(metrics)
    print(f"Decision: {decision}")

    ActionEngine().execute(decision, metrics)


if __name__ == "__main__":
    main()
