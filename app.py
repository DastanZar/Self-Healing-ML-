"""
FastAPI application for the self-healing ML system.

This API exposes the ML prediction pipeline as a REST endpoint.
"""

import logging
import sys
import os
from contextlib import asynccontextmanager

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

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


if __name__ == "__main__":
    import uvicorn

    # Run the application
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
