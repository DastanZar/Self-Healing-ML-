import subprocess
import logging

from self_healing_system.services.intelligence_service.deep_analysis import DeepAnalysisEngine
from self_healing_system.pipelines.training_pipeline import retrain_model

logger = logging.getLogger(__name__)


class ActionEngine:
    def execute(self, decision: str, metrics: dict):
        """
        Execute the appropriate action based on the decision.
        
        Args:
            decision: The decision from the FastDecisionEngine (HEALTHY, ALERT, RETRAIN, INVESTIGATE)
            metrics: Current system metrics
            
        Returns:
            str: Description of the action taken
        """
        if decision == "RETRAIN":
            print("[Action] Triggering model retraining...")
            logger.info("Triggering background retraining pipeline...")
            
            try:
                # Execute the training script synchronously
                result = subprocess.run(
                    ["python", "-m", "training.train"],
                    check=True,
                    capture_output=True,
                    text=True
                )
                print("[Action] Training script output:", result.stdout)
                logger.info("Training script completed successfully")
                
                # Hot-reload the model into memory
                logger.info("Retraining complete. Hot-reloading model into memory...")
                from self_healing_system.services.inference_service.prediction_service import (
                    initialize_inference_system
                )
                initialize_inference_system()
                logger.info("Model hot-reload completed successfully")
                
                return "Triggered model retraining and successfully hot-reloaded the new artifact."
                
            except subprocess.CalledProcessError as e:
                logger.error(f"Retraining failed: {e}")
                logger.error(f"Error output: {e.stderr}")
                print(f"[Action] Retraining failed with error: {e.stderr}")
                return "Retraining failed. Check system logs."
                
            except Exception as e:
                logger.error(f"Unexpected error during retraining: {e}")
                return "Retraining failed. Check system logs."
                
        elif decision == "ALERT":
            print("[Action] Sending alert to system...")
            logger.info("Alert action triggered")
            return "NONE"
            
        elif decision == "INVESTIGATE":
            print("[Action] Escalating to deep analysis (HLLM)...")
            logger.info("Deep analysis triggered")
            DeepAnalysisEngine().run_analysis(metrics)
            return "NONE"
            
        elif decision == "HEALTHY":
            print("[Action] System is healthy. No action needed.")
            logger.info("System healthy - no action required")
            return "NONE"
            
        else:
            logger.warning(f"Unknown decision: {decision}")
            return "NONE"
