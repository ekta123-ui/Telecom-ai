import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ai.embedding_service import embedding_model
from app.database import SessionLocal
from app.models.core import Document
from app.models.telecom import TelecomFAQ, Troubleshooting


def ingest_documents() -> tuple[int, int]:
    db = SessionLocal()
    inserted = 0
    updated = 0

    try:
        documents: list[dict] = []

        for faq in db.query(TelecomFAQ).all():
            documents.append(
                {
                    "source_table": "telecom_faqs",
                    "source_id": faq.faq_id,
                    "provider_id": faq.provider_id,
                    "title": faq.question[:200],
                    "content": f"Q: {faq.question}\nA: {faq.answer}",
                }
            )

        for issue in db.query(Troubleshooting).all():
            documents.append(
                {
                    "source_table": "troubleshooting",
                    "source_id": issue.issue_id,
                    "provider_id": None,
                    "title": issue.symptom[:200],
                    "content": (
                        f"Issue: {issue.symptom}\n"
                        f"Cause: {issue.possible_cause or ''}\n"
                        f"Solution: {issue.solution}"
                    ),
                }
            )

        if documents:
            embeddings = embedding_model.encode(
                [document["content"] for document in documents],
                convert_to_numpy=True,
            )

            for document_data, embedding in zip(documents, embeddings):
                document = (
                    db.query(Document)
                    .filter(
                        Document.source_table == document_data["source_table"],
                        Document.source_id == document_data["source_id"],
                    )
                    .one_or_none()
                )
                if document is None:
                    db.add(
                        Document(
                            **document_data,
                            embedding=embedding.tolist(),
                        )
                    )
                    inserted += 1
                else:
                    document.provider_id = document_data["provider_id"]
                    document.title = document_data["title"]
                    document.content = document_data["content"]
                    document.embedding = embedding.tolist()
                    updated += 1

        db.commit()
        return inserted, updated
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    inserted_count, updated_count = ingest_documents()
    print(
        f"Documents inserted: {inserted_count}; "
        f"updated: {updated_count}"
    )
