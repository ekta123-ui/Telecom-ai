import csv
from pathlib import Path

from app.ai.intent_classifier import save_classifier, train_classifier


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "datasets" / "intent_samples.csv"


def load_dataset(dataset_path: Path) -> tuple[list[str], list[str]]:
    with dataset_path.open(newline="", encoding="utf-8") as dataset_file:
        rows = list(csv.DictReader(dataset_file))

    if not rows or any(not row["text"].strip() or not row["intent"].strip() for row in rows):
        raise ValueError(f"Dataset must contain non-empty text and intent values: {dataset_path}")

    return [row["text"] for row in rows], [row["intent"] for row in rows]


def main() -> None:
    texts, labels = load_dataset(DATASET_PATH)
    model = train_classifier(texts, labels)
    save_classifier(model)
    print(f"Trained {len(texts)} samples across {len(set(labels))} intents.")


if __name__ == "__main__":
    main()
