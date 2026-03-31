"""
FastAPI application for the self-healing ML system.

This API exposes the ML prediction pipeline as a REST endpoint.
"""

import logging
import sys
import os
import random as _random
import math as _math
from contextlib import asynccontextmanager
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field
from typing import Optional
import asyncio

# Import service layer
from self_healing_system.services.inference_service.prediction_service import (
    initialize_inference_system,
    run_prediction_pipeline
)

# Import LLM service for RCA
from self_healing_system.services.llm_service import generate_root_cause_analysis

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Pydantic model for input validation
class PredictionInput(BaseModel):
    """Input schema for prediction endpoint."""
    cpu: float = Field(..., description="CPU usage percentage (0-100)")
    memory: float = Field(..., description="Memory usage percentage (0-100)")
    latency: float = Field(..., description="Response latency in milliseconds")
    error_rate: float = Field(..., description="Error rate (0-1)")


class PredictionOutput(BaseModel):
    """Output schema for prediction endpoint."""
    prediction: int
    decision: str
    metrics: dict
    action: str | None
    root_cause_analysis: Optional[str] = None


class SimulateOutput(BaseModel):
    cpu: float
    memory: float
    latency: float
    error_rate: float
    network_in: float
    network_out: float
    disk: float
    prediction: int
    decision: str
    anomaly_rate: float
    drift_score: float
    action: str
    message: str
    nodes: list
    timestamp: str


# Simulation tick counter (persists across requests in memory)
_sim_state = {"tick": 0}


# Global app state
app_state = {
    "model_loaded": False
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Load the model
    logger.info("Application startup - initializing inference system...")

    try:
        initialize_inference_system()
        app_state["model_loaded"] = True
        logger.info("Model loaded successfully")
    except FileNotFoundError as e:
        logger.error(f"Model initialization failed: {e}")
        app_state["model_loaded"] = False
    except Exception as e:
        logger.error(f"Model initialization failed: {e}")
        app_state["model_loaded"] = False

    yield

    # Shutdown
    logger.info("Application shutdown")


# Create FastAPI app
app = FastAPI(
    title="Self-Healing ML API",
    description="API for ML-powered self-healing system with real-time predictions",
    version="1.0.0",
    lifespan=lifespan
)
# --- ADD THIS CORS BLOCK RIGHT HERE ---
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        dict: Status of the API.
    """
    logger.info("Health check requested")
    return {"status": "running"}


@app.post("/predict", response_model=PredictionOutput)
async def predict(input_data: PredictionInput):
    """
    Run prediction pipeline with the given input data.

    Args:
        input_data: Input features containing cpu, memory, latency, error_rate.

    Returns:
        PredictionOutput: Prediction result, decision, metrics, and action.

    Raises:
        HTTPException: If model is not loaded or prediction fails.
    """
    logger.info(f"Request received with input: {input_data.model_dump()}")
    print(f"Request received: {input_data}")

    # Check if model is loaded
    if not app_state["model_loaded"]:
        logger.error("Model not loaded - cannot process request")
        raise HTTPException(
            status_code=503,
            detail="Model not loaded. Please ensure the model is trained."
        )

    try:
        # Run the prediction pipeline
        result = run_prediction_pipeline(input_data.model_dump())

        logger.info(f"Response returned: prediction={result['prediction']}, decision={result['decision']}")
        print(f"Response: prediction={result['prediction']}, decision={result['decision']}")

        # Generate root cause analysis only if prediction indicates anomaly (1)
        root_cause_analysis = None
        if result.get("prediction") == 1:
            logger.info("Generating root cause analysis...")
            root_cause_analysis = generate_root_cause_analysis(input_data.model_dump())
            print(f"Root cause analysis generated")

        return PredictionOutput(
            prediction=result["prediction"],
            decision=result["decision"],
            metrics=result["metrics"],
            action=result.get("action"),
            root_cause_analysis=root_cause_analysis
        )

    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        print(f"Error during prediction: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}"
        )


@app.get("/simulate")
async def simulate():
    """
    Simple simulation endpoint for frontend health check.
    Returns minimal metrics to prevent frontend crashes.
    """
    _sim_state["tick"] += 1
    tick = _sim_state["tick"]

    # Generate metrics with anomaly injection
    is_anomaly = tick > 0 and tick % 20 == 0
    is_spike   = tick > 0 and tick % 7  == 0

    if is_anomaly:
        cpu  = _random.uniform(75, 95)
        mem  = _random.uniform(70, 90)
        lat  = _random.uniform(250, 480)
        err  = _random.uniform(0.08, 0.18)
    elif is_spike:
        cpu  = _random.uniform(55, 75)
        mem  = _random.uniform(50, 70)
        lat  = _random.uniform(160, 260)
        err  = _random.uniform(0.02, 0.06)
    else:
        cpu  = _random.uniform(12, 55)
        mem  = _random.uniform(20, 58)
        lat  = _random.uniform(30, 140)
        err  = _random.uniform(0.001, 0.018)

    net_in  = round(_random.uniform(40, 180), 1)
    net_out = round(_random.uniform(15, 80), 1)
    disk    = round(min(35 + (tick * 0.05) % 30 + _random.uniform(-2, 2), 90), 1)

    inp = {
        "cpu": round(cpu, 2),
        "memory": round(mem, 2),
        "latency": round(lat, 2),
        "error_rate": round(err, 4),
    }

    # Run real ML pipeline
    try:
        result = run_prediction_pipeline(inp)
        prediction   = result["prediction"]
        decision     = result["decision"]
        metrics_out  = result.get("metrics", {})
        action       = str(result.get("action", "None"))
        anomaly_rate = metrics_out.get("anomaly_rate", 0.0)
        drift_score  = metrics_out.get("drift_score", 0.0)
    except Exception:
        decision     = "ALERT" if (cpu > 75 or lat > 220) else "HEALTHY"
        prediction   = 1 if decision == "ALERT" else 0
        anomaly_rate = 0.0
        drift_score  = 0.0
        action       = "Fallback mode"

    # Node health
    nodes = [True, True, True, True]
    if decision == "ALERT":
        nodes[_random.randint(0, 3)] = False
    elif decision in ("INVESTIGATE", "RETRAIN"):
        nodes[2] = False
        nodes[3] = False

    # Message
    msgs = {
        "HEALTHY":    "HEALTHY — System operating normally",
        "ALERT":      f"ALERT — Anomaly detected (confidence: {_random.randint(70,95)}%)",
        "INVESTIGATE":"INVESTIGATE — Escalated to deep analysis",
        "RETRAIN":    "RETRAIN — Model drift detected, retraining triggered",
    }

    # Return simple format to prevent frontend crashes
    return {
        "status": "online",
        "cpu": round(cpu, 1),
        "memory": round(mem, 1),
        "latency": round(lat, 0),
        "error_rate": round(err, 4),
        "networkIn": net_in,
        "networkOut": net_out,
        "diskUsage": disk,
    }


@app.post("/simulate/reset")
async def reset_simulation():
    _sim_state["tick"] = 0
    return {"status": "reset"}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time metric streaming.
    Pushes simulated metrics to the client every 2 seconds.
    """
    await websocket.accept()
    logger.info("WebSocket client connected")
    
    try:
        while True:
            # Reuse simulate logic
            _sim_state["tick"] += 1
            tick = _sim_state["tick"]

            # Generate metrics with anomaly injection
            is_anomaly = tick > 0 and tick % 20 == 0
            is_spike   = tick > 0 and tick % 7  == 0

            if is_anomaly:
                cpu  = _random.uniform(75, 95)
                mem  = _random.uniform(70, 90)
                lat  = _random.uniform(250, 480)
                err  = _random.uniform(0.08, 0.18)
            elif is_spike:
                cpu  = _random.uniform(55, 75)
                mem  = _random.uniform(50, 70)
                lat  = _random.uniform(160, 260)
                err  = _random.uniform(0.02, 0.06)
            else:
                cpu  = _random.uniform(12, 55)
                mem  = _random.uniform(20, 58)
                lat  = _random.uniform(30, 140)
                err  = _random.uniform(0.001, 0.018)

            net_in  = round(_random.uniform(40, 180), 1)
            net_out = round(_random.uniform(15, 80), 1)
            disk    = round(min(35 + (tick * 0.05) % 30 + _random.uniform(-2, 2), 90), 1)

            inp = {
                "cpu": round(cpu, 2),
                "memory": round(mem, 2),
                "latency": round(lat, 2),
                "error_rate": round(err, 4),
            }

            # Run real ML pipeline
            try:
                result = run_prediction_pipeline(inp)
                prediction   = result["prediction"]
                decision     = result["decision"]
                metrics_out  = result.get("metrics", {})
                action       = str(result.get("action", "None"))
                anomaly_rate = metrics_out.get("anomaly_rate", 0.0)
                drift_score  = metrics_out.get("drift_score", 0.0)
            except Exception:
                decision     = "ALERT" if (cpu > 75 or lat > 220) else "HEALTHY"
                prediction   = 1 if decision == "ALERT" else 0
                anomaly_rate = 0.0
                drift_score  = 0.0
                action       = "Fallback mode"

            # Node health
            nodes = [True, True, True, True]
            if decision == "ALERT":
                nodes[_random.randint(0, 3)] = False
            elif decision in ("INVESTIGATE", "RETRAIN"):
                nodes[2] = False
                nodes[3] = False

            # Message
            msgs = {
                "HEALTHY":    "HEALTHY — System operating normally",
                "ALERT":      f"ALERT — Anomaly detected (confidence: {_random.randint(70,95)}%)",
                "INVESTIGATE":"INVESTIGATE — Escalated to deep analysis",
                "RETRAIN":    "RETRAIN — Model drift detected, retraining triggered",
            }

            data = {
                "cpu": round(cpu, 1),
                "memory": round(mem, 1),
                "latency": round(lat, 0),
                "error_rate": round(err, 4),
                "network_in": net_in,
                "network_out": net_out,
                "disk": disk,
                "prediction": prediction,
                "decision": decision,
                "anomaly_rate": round(anomaly_rate, 4),
                "drift_score": round(drift_score, 4),
                "action": action,
                "message": msgs.get(decision, "UNKNOWN"),
                "nodes": nodes,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            }

            await websocket.send_json(data)
            await asyncio.sleep(2)
            
    except WebSocketDisconnect:
        logger.info("WebSocket client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")


@app.get("/metrics")
async def prometheus_metrics():
    """
    Prometheus metrics endpoint for monitoring scrapers.
    Returns metrics in Prometheus text format.
    """
    from fastapi.responses import PlainTextResponse
    
    tick = _sim_state.get("tick", 0)
    
    # Pull latest from predictions.jsonl
    try:
        from self_healing_system.services.monitoring_service.monitor import compute_metrics
        m = compute_metrics("logs/predictions.jsonl")
        anomaly_rate = m.get("anomaly_rate", 0)
        drift_score  = m.get("drift_score", 0)
        latency      = m.get("latency", 0)
    except:
        anomaly_rate = drift_score = latency = 0

    lines = [
        "# HELP aegisml_simulation_tick Total simulation ticks",
        "# TYPE aegisml_simulation_tick counter",
        f"aegisml_simulation_tick {tick}",
        "# HELP aegisml_anomaly_rate Current anomaly rate (0-1)",
        "# TYPE aegisml_anomaly_rate gauge",
        f"aegisml_anomaly_rate {anomaly_rate:.4f}",
        "# HELP aegisml_drift_score Current model drift score",
        "# TYPE aegisml_drift_score gauge",
        f"aegisml_drift_score {drift_score:.4f}",
        "# HELP aegisml_latency_ms Average latency milliseconds",
        "# TYPE aegisml_latency_ms gauge",
        f"aegisml_latency_ms {latency:.2f}",
    ]
    return PlainTextResponse("\n".join(lines), media_type="text/plain")


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
