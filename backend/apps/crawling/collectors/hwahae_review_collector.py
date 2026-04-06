import re
import time

import undetected_chromedriver as uc
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By


class HwahaeReviewCollector:
    """
    화해 상품 상세 페이지에서 리뷰 데이터를 수집합니다.
    """

    def _build_driver(self):
        options = uc.ChromeOptions()
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--start-maximized")
        options.add_argument("--window-size=1400,1200")
        options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/145.0.0.0 Safari/537.36"
        )

        driver = uc.Chrome(
            options=options,
            version_main=145,
            headless=True,
            use_subprocess=True,
        )
        return driver

    def _is_author_line(self, text: str) -> bool:
        """
        예: nkiihu 20대/복합성 2026.03.12
        """
        has_date = bool(re.search(r"\d{4}\.\d{2}\.\d{2}", text))
        has_age_skin = bool(re.search(r"(10대|20대|30대|40대|50대|건성|지성|복합성|민감성)", text))
        return has_date and has_age_skin

    def _is_stop_line(self, text: str) -> bool:
        stop_keywords = [
            "성분", "장바구니", "구매", "배송", "브랜드", "광고", "추천순",
            "평점", "별점", "필터", "정렬", "상품정보", "전성분", "리뷰쓰기",
        ]
        return any(keyword in text for keyword in stop_keywords)

    def _clean_review_text(self, text: str) -> str:
        text = text.replace("\n", " ")
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def collect_reviews(self, product_url: str, limit: int = 20) -> list[dict]:
        driver = None
        results = []

        try:
            driver = self._build_driver()

            driver.get("https://www.hwahae.co.kr/")
            time.sleep(3)

            driver.get(product_url)
            time.sleep(5)

            for _ in range(5):
                driver.execute_script("window.scrollBy(0, 1000);")
                time.sleep(1.5)

            buttons = driver.find_elements(By.XPATH, "//*[contains(text(),'리뷰')]")
            for b in buttons:
                try:
                    if "리뷰" in b.text:
                        driver.execute_script("arguments[0].click();", b)
                        time.sleep(5)
                        break
                except Exception:
                    continue

            html = driver.page_source
            soup = BeautifulSoup(html, "lxml")

            texts = []
            for tag in soup.find_all(["p", "span", "div"]):
                text = tag.get_text(" ", strip=True)
                if 2 <= len(text) <= 200:
                    texts.append(text)

            unique_texts = []
            seen = set()
            for t in texts:
                if t not in seen:
                    seen.add(t)
                    unique_texts.append(t)

            i = 0
            while i < len(unique_texts):
                line = unique_texts[i]

                if self._is_author_line(line):
                    author_info = line
                    review_parts = []
                    j = i + 1

                    while j < len(unique_texts):
                        next_line = unique_texts[j]

                        if self._is_author_line(next_line):
                            break

                        if self._is_stop_line(next_line):
                            break

                        if len(next_line) >= 8:
                            review_parts.append(next_line)

                        if len(review_parts) >= 3:
                            break

                        j += 1

                    review_text = self._clean_review_text(" ".join(review_parts))

                    if review_text and 10 <= len(review_text) <= 300:
                        results.append({
                            "source": "hwahae",
                            "url": product_url,
                            "author_info": author_info,
                            "review": review_text,
                        })

                    i = j
                else:
                    i += 1

            return results[:limit]

        except Exception as e:
            print(f"hwahae 리뷰 수집 실패: {e}")
            return []

        finally:
            if driver:
                try:
                    driver.quit()
                except Exception:
                    pass