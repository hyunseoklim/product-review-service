import re
import requests
from bs4 import BeautifulSoup


class GlowpickReviewCollector:
    """
    글로우픽 상품 상세 페이지 리뷰 휴리스틱 버전
    """
    HEADERS = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    def _clean_text(self, text: str) -> str:
        return re.sub(r"\s+", " ", text.replace("\n", " ")).strip()

    def _looks_like_review(self, text: str) -> bool:
        if len(text) < 15 or len(text) > 350:
            return False

        stop_keywords = [
            "랭킹", "브랜드", "카테고리", "필터", "정렬", "구매", "광고",
            "이벤트", "성분", "추천", "별점",
        ]
        if any(k in text for k in stop_keywords):
            return False

        return True

    def collect_reviews(self, product_url: str, limit: int = 20) -> list[dict]:
        try:
            response = requests.get(product_url, headers=self.HEADERS, timeout=20)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "lxml")

            texts = []
            for tag in soup.find_all(["p", "div", "span", "li"]):
                text = self._clean_text(tag.get_text(" ", strip=True))
                if self._looks_like_review(text):
                    texts.append(text)

            unique_texts = []
            seen = set()
            for text in texts:
                if text not in seen:
                    seen.add(text)
                    unique_texts.append(text)

            results = []
            for idx, review_text in enumerate(unique_texts[:limit], start=1):
                results.append({
                    "source": "glowpick",
                    "url": product_url,
                    "author_info": f"glowpick_user_{idx}",
                    "review": review_text,
                })

            return results

        except Exception as e:
            print(f"glowpick 리뷰 수집 실패: {e}")
            return []