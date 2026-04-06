from django.utils import timezone

from apps.crawling.models import CrawlRawData
from apps.crawling.services.save_service import save_review_result
from .http import fetch_page
from .parser import extract_page_info


def crawl_search_target(target):
    """
    검색 페이지 크롤링 함수

    전체 흐름:
    1. 페이지 요청 (robots.txt 검사 + retry + delay 적용됨)
    2. HTML 파싱
    3. 페이지 정보 저장
    4. 마지막 크롤링 시간 업데이트
    """

    # 1. 페이지 요청
    response = fetch_page(target.url)
    html = response.text

    # 2. HTML 분석
    page_info = extract_page_info(html)

    # 3. 후보 링크 (현재는 빈 리스트)
    candidate_links = []

    # 4. 페이지 전체 정보 저장 (로그 성격)
    CrawlRawData.objects.create(
        target=target,
        source_url=target.url,
        page_title=page_info["title"],
        raw_text=page_info["text_preview"],
        raw_html=html[:5000],
        extra_data={
            "a_count": page_info["a_count"],
            "contains_review_word": page_info["contains_review_word"],
            "contains_keyword": page_info["contains_keyword"],
            "type": "page_info",
        },
    )

    # 5. 후보 링크 저장 (있다면)
    for item in candidate_links[:20]:
        CrawlRawData.objects.create(
            target=target,
            source_url=target.url,
            page_title=page_info["title"],
            item_title=item["title"],
            item_url=item["url"],
            raw_text="",
            raw_html="",
            extra_data={"type": "candidate_link"},
        )

    # 6. 마지막 크롤링 시간 업데이트
    target.last_crawled_at = timezone.now()
    target.save(update_fields=["last_crawled_at"])

    return {
        "page_title": page_info["title"],
        "candidate_count": len(candidate_links),
    }


def crawl_product_review_target(target, review_limit: int = 20) -> dict:
    """
    product target에 대해 사이트별 리뷰 collector를 실행하고 저장합니다.
    사이트별 collector를 지연 import(lazy import)하여 불필요한 의존성 로딩을 방지합니다.
    """

    if target.site == "danawa":
        from apps.crawling.collectors.danawa_review_collector import DanawaReviewCollector
        collector = DanawaReviewCollector()
    elif target.site == "hwahae":
        from apps.crawling.collectors.hwahae_review_collector import HwahaeReviewCollector
        collector = HwahaeReviewCollector()
    elif target.site == "glowpick":
        from apps.crawling.collectors.glowpick_review_collector import GlowpickReviewCollector
        collector = GlowpickReviewCollector()
    else:
        raise ValueError(f"지원하지 않는 사이트입니다: {target.site}")

    reviews = collector.collect_reviews(target.url, limit=review_limit)
    save_result = save_review_result(target, reviews)

    return {
        "review_count": save_result["review_count"],
        "created_count": save_result["created_count"],
        "updated_count": save_result["updated_count"],
    }