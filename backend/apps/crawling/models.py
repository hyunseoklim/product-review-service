from django.db import models


class CrawlTarget(models.Model):
    """
    크롤링 대상 URL 저장
    - search: 검색 페이지
    - product: 상품 상세 페이지
    """

    SITE_CHOICES = [
        ("danawa", "다나와"),
        ("hwahae", "화해"),
        ("glowpick", "글로우픽"),
    ]

    TARGET_TYPE_CHOICES = [
        ("search", "검색 페이지"),
        ("product", "상품 상세 페이지"),
    ]

    site = models.CharField(max_length=30, choices=SITE_CHOICES)
    target_type = models.CharField(
        max_length=20,
        choices=TARGET_TYPE_CHOICES,
        default="product",
    )
    keyword = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=255, blank=True)
    url = models.URLField(max_length=1000, unique=True)

    is_active = models.BooleanField(default=True)

    # 스케줄링 제어용
    crawl_interval_minutes = models.PositiveIntegerField(
        default=60,
        help_text="이 target을 다시 수집할 최소 간격(분)"
    )
    priority = models.PositiveIntegerField(
        default=1,
        help_text="숫자가 클수록 우선 수집"
    )

    last_crawled_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-priority", "site", "target_type", "-created_at"]
        verbose_name = "크롤링 대상"
        verbose_name_plural = "크롤링 대상 목록"

    def __str__(self):
        return f"{self.site} | {self.target_type} | {self.url}"


class CrawlRawData(models.Model):
    """
    크롤링해서 가져온 원본 데이터 저장

    review 전용까지 포함:
    - page_info
    - candidate_link
    - review
    """

    RECORD_TYPE_CHOICES = [
        ("page_info", "페이지 정보"),
        ("candidate_link", "후보 링크"),
        ("review", "리뷰"),
    ]

    target = models.ForeignKey(
        CrawlTarget,
        on_delete=models.CASCADE,
        related_name="raw_items"
    )

    source_url = models.URLField(max_length=1000)
    page_title = models.CharField(max_length=255, blank=True)
    item_title = models.CharField(max_length=255, blank=True)
    item_url = models.URLField(max_length=1000, blank=True)

    raw_text = models.TextField(blank=True)
    raw_html = models.TextField(blank=True)

    extra_data = models.JSONField(default=dict, blank=True)

    record_type = models.CharField(
        max_length=30,
        choices=RECORD_TYPE_CHOICES,
        default="review",
        db_index=True,
    )

    unique_key = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
        blank=True,
        null=False,
    )

    crawled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-crawled_at"]
        verbose_name = "크롤링 원본 데이터"
        verbose_name_plural = "크롤링 원본 데이터 목록"
        indexes = [
            models.Index(fields=["target", "record_type"]),
            models.Index(fields=["source_url"]),
            models.Index(fields=["item_url"]),
        ]

    def __str__(self):
        return f"{self.target.site} | {self.record_type} | {self.item_title or self.page_title}"


class CrawlJobLog(models.Model):
    STATUS_CHOICES = [
        ("success", "성공"),
        ("failed", "실패"),
    ]

    site = models.CharField(max_length=30)
    command_name = models.CharField(max_length=100, default="scheduled_crawl")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)

    total_targets = models.PositiveIntegerField(default=0)
    success_count = models.PositiveIntegerField(default=0)
    fail_count = models.PositiveIntegerField(default=0)

    message = models.TextField(blank=True)

    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-started_at"]
        verbose_name = "크롤링 실행 로그"
        verbose_name_plural = "크롤링 실행 로그 목록"

    def __str__(self):
        return f"{self.site} | {self.status} | {self.started_at}"