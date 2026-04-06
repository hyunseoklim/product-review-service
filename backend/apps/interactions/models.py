from django.db import models
from django.conf import settings


class ReviewLike(models.Model):
    """
    리뷰 좋아요 모델
    - 한 사용자가 하나의 리뷰에 좋아요를 누르는 정보 저장
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="likes"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        unique_together = ("user", "review")

        # [10번에서 변경] 최신순 정렬 추가
        ordering = ["-id"]

    # [10번에서 변경] 관리자/디버깅용 문자열 표시 추가
    def __str__(self):
        return f"{self.user} - {self.review}"


class ReviewBookmark(models.Model):
    """
    리뷰 북마크 모델
    - 사용자가 나중에 보기 위해 리뷰를 저장하는 기능
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="bookmarks"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        # [10번에서 변경] 북마크도 중복 방지 제약 추가
        unique_together = ("user", "review")

        # [10번에서 변경] 최신순 정렬 추가
        ordering = ["-id"]

    # [10번에서 변경] 관리자/디버깅용 문자열 표시 추가
    def __str__(self):
        return f"{self.user} - {self.review}"


class ReviewComment(models.Model):
    """
    리뷰 댓글 모델
    - 리뷰에 대한 사용자 댓글 저장
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="comments"
    )

    content = models.TextField()

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    # [10번에서 변경] 댓글 수정 시간 추가
    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        # [10번에서 변경] 최신 댓글 우선 정렬 추가
        ordering = ["-id"]

    # [10번에서 변경] 관리자/디버깅용 문자열 표시 추가
    def __str__(self):
        return f"{self.user} - {self.review}"


class ReviewReport(models.Model):
    """
    리뷰 신고 모델
    - 부적절한 리뷰를 신고하는 기능
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    review = models.ForeignKey(
        "reviews.Review",
        on_delete=models.CASCADE,
        related_name="reports"
    )

    reason = models.CharField(
        max_length=255
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        # [10번에서 변경] 신고도 중복 방지 제약 추가
        unique_together = ("user", "review")

        # [10번에서 변경] 최신 신고 우선 정렬 추가
        ordering = ["-id"]

    # [10번에서 변경] 관리자/디버깅용 문자열 표시 추가
    def __str__(self):
        return f"{self.user} - {self.review}"
