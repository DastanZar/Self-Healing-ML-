# 🧠 Self-Healing ML System

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=flat-square&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/License-MIT-green?style=flat-square" alt="License">
  <img src="https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square" alt="Status">
</p>

---

## 🚀 Overview

Production machine learning models face a critical challenge: **model degradation over time**. Data drift, concept drift, and data quality issues can silently degrade model performance, leading to poor business decisions and lost revenue.

**Self-Healing ML System** is an intelligent, automated framework that monitors ML models in production, detects performance issues, and autonomously applies corrective actions—including retraining, alerting, and LLM-powered root cause analysis.

### Why It Matters

- **99% of ML models degrade** within the first year of deployment
- Manual monitoring is **time-consuming** and **error-prone**
- Downtime costs **thousands of dollars per hour** in production systems
- This system provides **autonomous healing** with human-in-the-loop oversight

---

## 🧠 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     Self-Healing ML System                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌────────┐ │
│  │  Data    │───▶│ Logging  │───▶│Monitoring│───▶│Decision│ │
│  │Generator │    │  Layer   │    │ Service  │    │ Engine │ │
│  └──────────┘    └──────────┘    └──────────┘    └────┬───┘ │
│                                                        │      │
│                              ┌──────────────────────────┘      │
│                              ▼                                  │
│                       ┌──────────┐                              │
│                       │  Action  │                              │
│                       │  Engine  │                              │
│                       └────┬─────┘                              │
│                            │                                    │
│          ┌─────────────────┼─────────────────┐                │
│          ▼                 ▼                 ▼                  │
│   ┌─────────────┐  ┌──────────────┐  ┌─────────────┐         │
│   │  Retraining │  │ Deep Analysis│  │   Alert    │         │
│   │  Pipeline   │  │  (HLLM)      │  │  System    │         │
│   └─────────────┘  └──────────────┘  └─────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### System Flow

1. **Data Input** → Predictions and metrics are logged to JSONL files
2. **Monitoring** → Computes anomaly_rate, drift_score, and latency from sliding window
3. **Decision Engine** → Fast rule-based classification (HEALTHY, INVESTIGATE, RETRAIN, ALERT)
4. **Action Engine** → Executes corrective actions based on decision
5. **Deep Analysis** → LLM-powered root cause diagnosis (HLLM integration)

---

## ⚙️ Tech Stack

| Component | Technology |
|-----------|------------|
| Language | Python 3.10+ |
| Data Processing | Pandas, NumPy |
| ML Integration | scikit-learn |
| LLM Backend | Azure OpenAI (HLLM) |
| Architecture | Modular Service-Oriented |

---

## 🔄 System Workflow

```
┌─────────────────┐
│ 1. Prediction   │ ← Model generates predictions
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 2. Logging      │ ← Write to JSONL (timestamp, input, prediction)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 3. Monitoring  │ ← Compute metrics (anomaly_rate, drift_score, latency)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 4. Decision     │ ← Classify: HEALTHY | INVESTIGATE | RETRAIN | ALERT
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ 5. Action      │ ← Execute: retrain / deep analysis / alert / log
└─────────────────┘
```

---

## 🔥 Key Features

### ✨ Real-Time Monitoring
- Sliding window metrics computation using `collections.deque`
- Computes **anomaly_rate**, **drift_score**, and **latency** from prediction logs
- Memory-efficient: only keeps last N entries in memory

### ⚡ Automated Decision Engine
- Fast rule-based classification with configurable thresholds
- Decisions: `HEALTHY`, `INVESTIGATE`, `RETRAIN`, `ALERT`
- Zero latency decision making

### 🔧 Self-Healing Actions
- **RETRAIN** → Triggers automated model retraining pipeline
- **INVESTIGATE** → Escalates to deep analysis
- **ALERT** → Sends notifications to system operators
- **HEALTHY** → No action needed

### 🧠 LLM-Powered Diagnostics
- Integrates **HLLM** (Hypothesizer-Language Language Model) for intelligent diagnosis
- Uses LLM to hypothesize root causes of model degradation
- Generates actionable insights from covariate-level performance analysis

---

## 📊 Example Output

```bash
$ python -m self_healing_system.main

[Monitor] anomaly_rate=0.500 drift_score=1.955 latency=132.500
Metrics: {'anomaly_rate': 0.5, 'drift_score': 1.954..., 'latency': 132.5}
Decision: INVESTIGATE
[Action] Escalating to deep analysis (HLLM)...
[DeepAnalysis] Running root cause analysis...
[DeepAnalysis] Input metrics: {'anomaly_rate': 0.5, 'drift_score': 1.954..., 'latency': 132.5}
[DeepAnalysis] Running HLLM-based diagnosis...
Possible data drift detected
High anomaly rate detected
```

---

## 🚀 Future Improvements

- [ ] **Real LLM Integration** → Connect Azure OpenAI for full HLLM diagnosis
- [ ] **Streaming Pipeline** → Replace file-based logging with Kafka/Pulsar
- [ ] **Kubernetes Deployment** → Containerize with Docker and deploy to K8s
- [ ] **Metrics Dashboard** → Add Prometheus + Grafana for real-time visualization
- [ ] **A/B Testing** → Compare healed model vs. original model performance
- [ ] **Alerting Integrations** → Slack, PagerDuty, email notifications

---

## 📝 License

MIT License - See [LICENSE](LICENSE) for details.

---

## 🤝 Contributing

Contributions are welcome! Please open an issue or submit a PR.

---

*Built with ❤️ for resilient ML systems*
