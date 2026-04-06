from django.conf import settings
from django.db import models
from pgvector.django import VectorField


class ReviewEmbedding(models.Model):
    """
    핵심 모델 (Vector DB 역할)
    """

    review = models.OneToOneField(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="embedding"
    )

    # e5-small-korean = 384 차원
    embedding = VectorField(dimensions=384)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReviewEmbedding(review_id={self.review_id})"


class ReviewSimilarityResult(models.Model):
    """
    [유지]
    AI 유사도 분석 결과 저장 모델 (최종 결과 데이터)
    """

    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="similarity_results",
    )
    # 어떤 상품 기준으로 분석했는지 연결

    source_review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="source_similarity_results",
    )
    # 분석 기준이 된 리뷰

    compared_review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="compared_similarity_results",
    )
    # 비교 대상 리뷰

    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="similarity_results",
    )
    # 분석 요청한 사용자

    similarity_score = models.FloatField()
    # 유사도 점수 (0.0 ~ 1.0)

    similarity_label = models.CharField(max_length=50)
    # 유사도 라벨 (매우 비슷 / 비슷 / 약간 비슷 등)

    similarity_threshold = models.FloatField(default=0.45)
    # 분석 시 사용한 기준 임계값

    model_name = models.CharField(max_length=100, default="upskyy/e5-small-korean")
    # 사용한 AI 모델명

    source_review_snapshot = models.TextField()
    # 분석 시점의 기준 리뷰 내용 스냅샷

    compared_review_snapshot = models.TextField()
    # 분석 시점의 비교 리뷰 내용 스냅샷

    compared_username_snapshot = models.CharField(max_length=150)
    # 분석 시점의 비교 리뷰 작성자명 스냅샷

    analyzed_at = models.DateTimeField(auto_now_add=True)
    # 분석 완료 시각

    class Meta:
        ordering = ["-analyzed_at"]

    def __str__(self):
        return f"{self.source_review_id} vs {self.compared_review_id} ({self.similarity_score})"


class AIAnalysisTask(models.Model):
    """
    [추가]
    Celery 비동기 작업 상태를 DB에서 추적하기 위한 모델
    """

    # =========================
    # [상태 값 정의]
    # =========================
    STATUS_PENDING = "PENDING"     # 작업 대기중
    STATUS_STARTED = "STARTED"     # 작업 진행중
    STATUS_SUCCESS = "SUCCESS"     # 작업 완료
    STATUS_FAILURE = "FAILURE"     # 작업 실패

    STATUS_CHOICES = [
        (STATUS_PENDING, "대기중"),
        (STATUS_STARTED, "진행중"),
        (STATUS_SUCCESS, "완료"),
        (STATUS_FAILURE, "실패"),
    ]

    # =========================
    # [어떤 리뷰를 분석했는지]
    # =========================
    source_review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="ai_analysis_tasks",
    )
    # 분석 기준이 되는 리뷰 (버튼 누른 리뷰)

    # =========================
    # [누가 요청했는지]
    # =========================
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ai_analysis_tasks",
    )
    # 어떤 사용자가 분석 요청했는지 (로그 추적용)

    # =========================
    # [Celery 연결 키]
    # =========================
    task_id = models.CharField(
        max_length=255,
        unique=True,
        db_index=True,
    )
    # Celery 작업 고유 ID (이걸로 작업 상태 추적)

    # =========================
    # [현재 작업 상태]
    # =========================
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
    )
    # 현재 상태 (대기중 / 진행중 / 완료 / 실패)

    # =========================
    # [사용한 AI 모델]
    # =========================
    model_name = models.CharField(
        max_length=100,
        default="upskyy/e5-small-korean",
    )
    # 어떤 AI 모델로 분석했는지 기록

    # =========================
    # [유사도 기준값]
    # =========================
    similarity_threshold = models.FloatField(default=0.45)
    # 이 점수 이상만 결과로 인정 (필터 기준)

    # =========================
    # [분석 통계]
    # =========================
    candidate_count = models.PositiveIntegerField(default=0)
    # 비교 대상 리뷰 개수

    result_count = models.PositiveIntegerField(default=0)
    # 최종 유사하다고 판단된 결과 개수

    # =========================
    # [에러 정보]
    # =========================
    error_message = models.TextField(blank=True)
    # 실패 시 에러 내용 저장

    # =========================
    # [시간 기록]
    # =========================
    created_at = models.DateTimeField(auto_now_add=True)
    # 작업 생성 시간

    started_at = models.DateTimeField(null=True, blank=True)
    # 실제 작업 시작 시간

    finished_at = models.DateTimeField(null=True, blank=True)
    # 작업 완료 시간

    # =========================
    # [정렬 기준]
    # =========================
    class Meta:
        ordering = ["-created_at"]
    # 최신 작업이 위로 보이도록 정렬

    # =========================
    # [관리자 표시용]
    # =========================
    def __str__(self):
        return f"{self.task_id} - {self.status}"
    # admin / 로그에서 "task_id - 상태" 형태로 표시