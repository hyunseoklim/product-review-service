from rest_framework import serializers

from .models import (
    ReviewLike,
    ReviewBookmark,
    ReviewComment,
    ReviewReport,
)


class ReviewLikeSerializer(serializers.ModelSerializer):
    """
    리뷰 좋아요 Serializer
    """

    class Meta:
        model = ReviewLike
        fields = [
            "id",
            "user",
            "review",
            "created_at",
        ]

        # [10번에서 변경] user를 request.user로 처리하는 구조에 맞게
        # id, user, created_at을 읽기 전용으로 추가
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]


class ReviewBookmarkSerializer(serializers.ModelSerializer):
    """
    리뷰 북마크 Serializer
    """

    class Meta:
        model = ReviewBookmark
        fields = [
            "id",
            "user",
            "review",
            "created_at",
        ]

        # [10번에서 변경] 북마크도 user를 직접 받지 않고
        # View에서 자동 처리할 수 있도록 읽기 전용 필드 추가
        read_only_fields = [
            "id",
            "user",
            "created_at",
        ]


class ReviewCommentSerializer(serializers.ModelSerializer):
    """
    리뷰 댓글 Serializer
    """

    # [10번에서 변경] 댓글 작성자의 username 표시용 필드 추가
    # source="user.username" 으로 User 모델의 username을 응답에 포함
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = ReviewComment
        fields = [
            "id",
            "user",

            # [10번에서 변경] 작성자 username 응답 필드 추가
            "username",

            "review",
            "content",
            "created_at",

            # [10번에서 변경] models.py에 추가된 updated_at 반영
            "updated_at",
        ]

        # [10번에서 변경] 댓글은 user, review를 View/URL에서 처리하는 구조라
        # 클라이언트 수정 불가 필드들을 읽기 전용으로 추가
        read_only_fields = [
            "id",
            "user",
            "username",
            "review",
            "created_at",
            "updated_at",
        ]


class ReviewReportSerializer(serializers.ModelSerializer):
    """
    리뷰 신고 Serializer
    """

    # [10번에서 변경] 신고자 username 표시용 필드 추가
    username = serializers.CharField(
        source="user.username",
        read_only=True
    )

    class Meta:
        model = ReviewReport
        fields = [
            "id",
            "user",

            # [10번에서 변경] 신고자 username 응답 필드 추가
            "username",

            "review",
            "reason",
            "created_at",
        ]

        # [10번에서 변경] 신고도 user, review를 View에서 자동 처리하므로
        # 읽기 전용 필드 추가
        read_only_fields = [
            "id",
            "user",
            "username",
            "review",
            "created_at",
        ]