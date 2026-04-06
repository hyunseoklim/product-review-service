from sentence_transformers import SentenceTransformer


# FastAPI 서버가 뜰 때 모델을 한 번만 메모리에 로딩
embedding_model = SentenceTransformer("upskyy/e5-small-korean")