from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.products.models import Product
from apps.core.models import SoftDeleteModel


User = settings.AUTH_USER_MODEL


class Review(SoftDeleteModel):
    """
    제품 리뷰 모델
    - 리뷰 본문, 평점, 공개 여부 저장
    - Soft Delete 적용 대상
    """

    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,   # 사용자 삭제 시 리뷰까지 지우지 않고 user만 null 처리
        null=True,
        blank=True,
        related_name="reviews",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,    # 리뷰가 달린 상품은 실수로 삭제되지 않게 막음
        related_name="reviews",
    )

    content = models.TextField()
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        username = self.user.username if self.user else "탈퇴한 사용자"
        return f"{self.product} - {username}"


class ReviewImage(models.Model):
    """
    리뷰 이미지 모델
    - 리뷰 1개에 여러 이미지가 연결될 수 있음
    """

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,  # 리뷰가 완전 삭제(hard delete)되면 이미지도 함께 삭제
        related_name="images",
    )
    image = models.ImageField(upload_to="reviews/")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReviewImage(review_id={self.review_id})"


class ReviewAI(models.Model):
    """
    리뷰 AI 분석 결과 모델
    - 리뷰 1개당 AI 결과 1개 저장
    """

    review = models.OneToOneField(
        Review,
        on_delete=models.CASCADE,  # 리뷰가 완전 삭제(hard delete)되면 AI 결과도 함께 삭제
        related_name="ai_result",
    )
    sentiment = models.CharField(max_length=50)
    confidence = models.FloatField()
    keywords = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ReviewAI(review_id={self.review_id})"
