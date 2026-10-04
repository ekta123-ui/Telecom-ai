import json
from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline


BACKEND_DIR = Path(__file__).resolve().parents[1]
DATASET_PATH = BACKEND_DIR / "datasets" / "intents.csv"
MODEL_DIR = BACKEND_DIR / "ml_models"
MODEL_PATH = MODEL_DIR / "intent_classifier.pkl"
LABELS_PATH = MODEL_DIR / "intent_labels.json"


def main() -> None:
    print("=" * 70)
    print("Loading intent dataset")
    print("=" * 70)
    df = pd.read_csv(DATASET_PATH)

    required_columns = {"text", "intent"}
    missing_columns = required_columns - set(df.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {sorted(missing_columns)}"
        )

    df = df.dropna(subset=["text", "intent"]).copy()
    df["text"] = df["text"].astype(str)
    df["intent"] = df["intent"].astype(str)
    intent_labels = sorted(df["intent"].unique().tolist())

    print(f"Dataset: {DATASET_PATH}")
    print(f"Samples: {len(df)}")
    print(f"Intents: {len(intent_labels)}")
    print(f"Labels: {', '.join(intent_labels)}")

    print("\n" + "=" * 70)
    print("Splitting dataset")
    print("=" * 70)
    X_train, X_test, y_train, y_test = train_test_split(
        df["text"],
        df["intent"],
        test_size=0.2,
        stratify=df["intent"],
        random_state=42,
    )
    print(f"Training samples: {len(X_train)}")
    print(f"Test samples: {len(X_test)}")

    print("\n" + "=" * 70)
    print("Training TF-IDF + Logistic Regression pipeline")
    print("=" * 70)
    pipeline = Pipeline(
        [
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=1,
                    lowercase=True,
                ),
            ),
            ("classifier", LogisticRegression(max_iter=1000)),
        ]
    )
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)

    print("\n" + "=" * 70)
    print("Evaluation")
    print("=" * 70)
    print(f"Overall accuracy: {accuracy_score(y_test, y_pred):.4f}")
    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=intent_labels,
            target_names=intent_labels,
            zero_division=0,
        )
    )

    confusion = confusion_matrix(y_test, y_pred, labels=intent_labels)
    confusion_df = pd.DataFrame(
        confusion,
        index=intent_labels,
        columns=intent_labels,
    )
    print("Confusion matrix:")
    print(confusion_df.to_string())

    print("\n" + "=" * 70)
    print("Saving model artifacts")
    print("=" * 70)
    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipeline, MODEL_PATH)
    LABELS_PATH.write_text(
        json.dumps(intent_labels, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"Pipeline saved to: {MODEL_PATH}")
    print(f"Intent labels saved to: {LABELS_PATH}")

    print("\n" + "=" * 70)
    print("Manual test predictions")
    print("=" * 70)
    sample_sentences = [
        "mera data kitna bacha hai",
        "I want to recharge with 399 plan",
        "network bahut slow chal raha hai",
        "what's the difference between 299 and 399",
        "hello how are you",
    ]
    probabilities = pipeline.predict_proba(sample_sentences)
    predictions = pipeline.predict(sample_sentences)

    for sentence, prediction, probability in zip(
        sample_sentences,
        predictions,
        probabilities,
    ):
        confidence = probability.max()
        print(f'Text: "{sentence}"')
        print(f"Intent: {prediction} | Confidence: {confidence:.4f}\n")


if __name__ == "__main__":
    main()
