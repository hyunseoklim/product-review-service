from rest_framework import serializers

from .models import Review, ReviewImage


class ReviewImageSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = ReviewImage
        fields = [
            "id",
            "image",
            "image_url",
            "created_at",
        ]

    def get_image_url(self, obj):
        request = self.context.get("request")

        if not obj.image:
            return None

        try:
            image_url = obj.image.url
        except Exception:
            return None

        if request:
            return request.build_absolute_uri(image_url)

        return image_url


class ReviewAISerializer(serializers.Serializer):
    sentiment = serializers.CharField(read_only=True)
    confidence = serializers.FloatField(read_only=True, required=False)
    score = serializers.FloatField(read_only=True, required=False)
    summary = serializers.CharField(read_only=True, required=False)
    keywords = serializers.ListField(
        child=serializers.CharField(),
        read_only=True,
        required=False,
    )


class ReviewSerializer(serializers.ModelSerializer):
    # Soft Delete 구조에서 user가 null일 수 있으므로 SerializerMethodField 사용
    username = serializers.SerializerMethodField()

    images = ReviewImageSerializer(many=True, read_only=True)

    # AI 결과가 없는 리뷰도 있으므로 안전하게 처리
    ai_result = serializers.SerializerMethodField()

    likes_count = serializers.SerializerMethodField()
    bookmarks_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()

    class Meta:
        model = Review
        fields = [
            "id",
            "user",
            "username",
            "product",
            "content",
            "rating",
            "is_public",
            "created_at",
            "updated_at",
            "images",
            "ai_result",
            "likes_count",
            "bookmarks_count",
            "is_liked",
            "is_bookmarked",
        ]
        read_only_fields = [
            "id",
            "user",
            "username",
            "created_at",
            "updated_at",
            "images",
            "ai_result",
            "likes_count",
            "bookmarks_count",
            "is_liked",
            "is_bookmarked",
        ]

    def get_username(self, obj):
        # Soft Delete + SET_NULL 구조에서 user가 null일 수 있음
        if obj.user:
            return obj.user.username
        return "탈퇴한 사용자"

    def get_ai_result(self, obj):
        if not hasattr(obj, "ai_result"):
            return None
        return ReviewAISerializer(obj.ai_result).data

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count()

    def get_is_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.likes.filter(user=request.user).exists()

    def get_is_bookmarked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.bookmarks.filter(user=request.user).exists()
