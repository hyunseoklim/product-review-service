from apps.crawling.models import CrawlRawData


# [4단계 추가]
# 이 파일은 DB 직접 접근(ORM)만 담당합니다.
# save_service.py 에서 비즈니스 흐름을 짜고,
# repository.py 에서는 create/update/get_or_create/update_or_create만 담당합니다.


def upsert_raw_data(unique_key: str, defaults: dict):
    """
    unique_key 기준으로 CrawlRawData를 update_or_create 합니다.
    """
    obj, created = CrawlRawData.objects.update_or_create(
        unique_key=unique_key,
        defaults=defaults,
    )
    return obj, created