from pathlib import Path

import joblib
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


DEFAULT_MODEL_PATH = Path(__file__).resolve().parent / "models" / "intent_classifier.joblib"


def train_classifier(texts: list[str], labels: list[str]) -> Pipeline:
    model = Pipeline(
        [
            ("tfidf", TfidfVectorizer(lowercase=True, ngram_range=(1, 2))),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    model.fit(texts, labels)
    return model


def save_classifier(model: Pipeline, output_path: Path = DEFAULT_MODEL_PATH) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, output_path)
