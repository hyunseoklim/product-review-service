from bs4 import BeautifulSoup


def get_soup(html: str) -> BeautifulSoup:
    """
    HTML 문자열을 BeautifulSoup 객체로 변환합니다.
    """
    return BeautifulSoup(html, "lxml")


def extract_page_info(html: str) -> dict:
    """
    페이지의 공통 정보를 추출합니다.
    """
    soup = get_soup(html)
    text = soup.get_text(" ", strip=True)

    return {
        "title": soup.title.get_text(strip=True) if soup.title else "",
        "a_count": len(soup.select("a[href]")),
        "contains_review_word": "리뷰" in text,
        "contains_keyword": "수분크림" in text,
        "text_preview": text[:500],
    }

# 3단계에서 이미 extract_candidate_links()는 제거된 상태 유지
# [4단계에서는 parser 수정 없음]