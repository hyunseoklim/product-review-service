from urllib.parse import urljoin

from apps.crawling.services.http import fetch_page
from apps.crawling.services.parser import extract_page_info, get_soup


def collect_hwahae_search(target) -> dict:
    """
    화해 검색 페이지를 수집해서
    페이지 기본 정보와 상품 상세 링크 후보를 반환합니다.
    """
    response = fetch_page(target.url)
    html = response.text

    page_info = extract_page_info(html)
    soup = get_soup(html)

    candidates = []
    seen = set()

    for a in soup.select("a[href]"):
        href = (a.get("href") or "").strip()
        text = a.get_text(" ", strip=True)

        if not href:
            continue

        full_url = urljoin(target.url, href)

        if "hwahae.co.kr" not in full_url:
            continue

        if not (
            "/product/" in full_url
            or "/products/" in full_url
            or "/goods/" in full_url
        ):
            continue

        if full_url in seen:
            continue

        seen.add(full_url)

        candidates.append({
            "title": text[:255],
            "url": full_url,
        })

    return {
        "site": "hwahae",
        "page_info": page_info,
        "candidate_links": candidates[:20],
        "html": html,
    }