import hashlib

from django.db import transaction
from django.utils import timezone

from apps.crawling.services.repository import upsert_raw_data


def make_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def build_review_unique_key(target, review: dict) -> str:
    raw = (
        f"{target.site}:review:"
        f"{target.url}:"
        f"{review.get('author_info', '')}:"
        f"{review.get('review', '')}"
    )
    return make_hash(raw)


def build_review_defaults(target, review: dict) -> dict:
    return {
        "target": target,
        "source_url": target.url,
        "page_title": target.title[:255] if target.title else "",
        "item_title": target.title[:255] if target.title else "",
        "item_url": target.url,
        "raw_text": review.get("review", "")[:5000],
        "raw_html": "",
        "record_type": "review",
        "extra_data": {
            "source": review.get("source", target.site),
            "author_info": review.get("author_info", ""),
        },
    }


@transaction.atomic
def save_review_result(target, reviews: list[dict]) -> dict:
    created_count = 0
    updated_count = 0

    for review in reviews:
        unique_key = build_review_unique_key(target, review)

        _, created = upsert_raw_data(
            unique_key=unique_key,
            defaults={
                **build_review_defaults(target, review),
                "unique_key": unique_key,
            }
        )

        if created:
            created_count += 1
        else:
            updated_count += 1

    target.last_crawled_at = timezone.now()
    target.save(update_fields=["last_crawled_at"])

    return {
        "review_count": len(reviews),
        "created_count": created_count,
        "updated_count": updated_count,
    }