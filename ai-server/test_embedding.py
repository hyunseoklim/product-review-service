from models.embedding_model import embedding_model
from sklearn.metrics.pairwise import cosine_similarity


def main():
    texts = [
        "보습력이 좋아서 겨울에 쓰기 좋았어요.",
        "수분감이 오래가고 건성 피부에 잘 맞아요.",
        "향이 너무 강하고 자극적이어서 별로였어요.",
    ]

    embeddings = embedding_model.encode(texts)

    print("임베딩 개수:", len(embeddings))
    print("벡터 차원:", len(embeddings[0]))

    sim_01 = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    sim_02 = cosine_similarity([embeddings[0]], [embeddings[2]])[0][0]

    print("1번-2번 유사도:", float(sim_01))
    print("1번-3번 유사도:", float(sim_02))


if __name__ == "__main__":
    main()