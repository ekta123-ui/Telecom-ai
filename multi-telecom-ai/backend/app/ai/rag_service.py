from sqlalchemy.orm import Session

from app.ai.embedding_service import embedding_model
from app.models.core import Document


def retrieve_relevant_documents(
    query: str,
    db: Session,
    top_k: int = 4,
    min_similarity: float = 0.3,
) -> list[dict]:
    query_embedding = embedding_model.encode(
        query,
        convert_to_numpy=True,
    ).tolist()
    distance = Document.embedding.cosine_distance(query_embedding)
    rows = (
        db.query(Document, distance.label("distance"))
        .filter(Document.embedding.is_not(None))
        .order_by(distance.asc())
        .limit(top_k)
        .all()
    )

    results = []
    for document, cosine_distance in rows:
        similarity = 1 - float(cosine_distance)
        if similarity >= min_similarity:
            results.append(
                {
                    "title": document.title,
                    "content": document.content,
                    "source_table": document.source_table,
                    "similarity": similarity,
                }
            )
    return results
