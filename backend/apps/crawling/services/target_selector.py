from datetime import timedelta

from django.db.models import F, ExpressionWrapper, DateTimeField, Q
from django.db.models.functions import Now
from django.utils import timezone

from apps.crawling.models import CrawlTarget


def get_due_targets(limit: int = 3, target_type: str = "search"):
    """
    이번 실행 차례가 된 target만 선택합니다.

    규칙
    1. is_active=True
    2. target_type=search
    3. 아직 한 번도 안 돌린 대상 우선
    4. 이미 돌린 대상은 last_crawled_at 오래된 순
    5. 단, crawl_interval_minutes가 지나지 않은 것은 제외
    """

    now = timezone.now()

    all_targets = CrawlTarget.objects.filter(
        is_active=True,
        target_type=target_type,
    )

    # 1) 아직 한 번도 안 돌린 대상
    never_crawled_qs = all_targets.filter(
        last_crawled_at__isnull=True
    ).order_by("-priority", "created_at")

    selected_ids = list(
        never_crawled_qs.values_list("id", flat=True)[:limit]
    )

    remaining = limit - len(selected_ids)

    if remaining > 0:
        # 2) 돌린 적은 있지만, interval이 지난 대상만 후보
        due_targets = []

        candidates = all_targets.filter(
            last_crawled_at__isnull=False
        ).order_by("last_crawled_at", "-priority", "created_at")

        for target in candidates:
            next_time = target.last_crawled_at + timedelta(
                minutes=target.crawl_interval_minutes
            )
            if next_time <= now:
                due_targets.append(target.id)

            if len(due_targets) >= remaining:
                break

        selected_ids.extend(due_targets)

    if not selected_ids:
        return CrawlTarget.objects.none()

    # 선택된 순서를 대충 유지하려면 단순 필터 후 후정렬
    selected_targets = CrawlTarget.objects.filter(
        id__in=selected_ids
    ).order_by("last_crawled_at", "-priority", "created_at")

    return selected_targets