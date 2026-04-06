from sklearn.metrics.pairwise import cosine_similarity
from models.embedding_model import embedding_model

# 임베딩 생성
def make_embeddings(texts: list[str]) -> list[list[float]]:
    """
    여러 문장을 받아 임베딩 벡터 리스트로 반환
    """
    vectors = embedding_model.encode(texts)
    return [vector.tolist() for vector in vectors]

# 유사도 계산
def calculate_similarity(text1: str, text2: str) -> float:
    """
    두 문장의 cosine similarity 계산
    """
    vectors = embedding_model.encode([text1, text2])
    score = cosine_similarity([vectors[0]], [vectors[1]])[0][0]
    return float(score)