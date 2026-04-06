import requests
from django.conf import settings


class FastAPIClient:
    @staticmethod
    def get_embedding(text: str):
        response = requests.post(
            f"{settings.FASTAPI_BASE_URL}/api/v1/recommend/embed",
            json={"texts": [text]},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()["embeddings"][0]

    @staticmethod
    def get_similarity(text1: str, text2: str) -> dict:
        response = requests.post(
            f"{settings.FASTAPI_BASE_URL}/api/v1/recommend/similarity",
            json={
                "text1": text1,
                "text2": text2,
            },
            timeout=20,
        )
        response.raise_for_status()
        return response.json()