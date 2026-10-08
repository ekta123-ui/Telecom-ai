from pathlib import Path

import joblib


MODEL_PATH = (
    Path(__file__).resolve().parent
    / ".."
    / ".."
    / "ml_models"
    / "intent_classifier.pkl"
).resolve()

if not MODEL_PATH.exists():
    raise RuntimeError(
        f"Intent classifier model not found at {MODEL_PATH}. "
        "Run the intent model training script first."
    )

intent_pipeline = joblib.load(MODEL_PATH)


def predict_intent(text: str) -> tuple[str, float]:
    probabilities = intent_pipeline.predict_proba([text])[0]
    predicted_index = probabilities.argmax()
    confidence = float(probabilities[predicted_index])
    intent = str(intent_pipeline.classes_[predicted_index])

    if confidence < 0.35:
        return "UNCLEAR", confidence

    return intent, confidence
