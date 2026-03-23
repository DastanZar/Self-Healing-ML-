import json
from datetime import datetime
import os


LOG_FILE = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    "logs",
    "predictions.jsonl"
)


def log_prediction(input_data: dict, prediction: int):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "input": input_data,
        "prediction": prediction
    }

    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")