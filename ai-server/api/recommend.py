from fastapi import APIRouter
from schemas.recommend_schema import (
    EmbeddingRequest,
    EmbeddingResponse,
    SimilarityRequest,
    SimilarityResponse,
)
from services.recommend_service import make_embeddings, calculate_similarity

router = APIRouter(prefix="/api/v1/recommend", tags=["recommend"])


@router.post("/embed", response_model=EmbeddingResponse)
def embed_texts(payload: EmbeddingRequest):
    return {"embeddings": make_embeddings(payload.texts)}


@router.post("/similarity", response_model=SimilarityResponse)
def similarity(payload: SimilarityRequest):
    return {"similarity": calculate_similarity(payload.text1, payload.text2)}