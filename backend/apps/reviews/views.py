from django.shortcuts import get_object_or_404

from rest_framework import permissions, status, viewsets, generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Review, ReviewImage
from .serializers import (
    ReviewSerializer,
    ReviewImageSerializer,
    ReviewAISerializer,
)


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    읽기 요청은 누구나 허용
    수정/삭제는 작성자 본인만 허용
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user


class ReviewViewSet(viewsets.ModelViewSet):
    """
    리뷰 CRUD API
    - 삭제 시 물리 삭제가 아닌 Soft Delete(논리 삭제) 적용
    """

    serializer_class = ReviewSerializer
    parser_classes = [MultiPartParser, FormParser]

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Review.objects → Soft Delete 기본 매니저 사용
        → 삭제된 리뷰(is_deleted=True)는 자동으로 제외됨
        """
        queryset = (
            Review.objects
            .select_related("user", "product", "ai_result")
            .prefetch_related("images", "likes", "bookmarks")
            .filter(is_public=True)
            .order_by("-created_at")
        )

        product_id = self.request.query_params.get("product")
        if product_id:
            queryset = queryset.filter(product_id=product_id)

        return queryset

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user, is_public=True)
        else:
            raise ValidationError("리뷰 작성은 로그인 후 가능합니다.")

    def perform_update(self, serializer):
        review = self.get_object()
        if review.user != self.request.user:
            raise PermissionDenied("본인 리뷰만 수정할 수 있습니다.")
        serializer.save()

    def destroy(self, request, *args, **kwargs):
        """
        Soft Delete: DB에서 실제 삭제하지 않고 is_deleted=True로 변경
        """
        instance = self.get_object()

        if instance.user != request.user:
            return Response(
                {"detail": "본인 리뷰만 삭제할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        instance.delete()  # SoftDeleteModel.delete() → is_deleted=True

        return Response(
            {
                "message": "리뷰가 삭제되었습니다.",
                "soft_deleted": True,
            },
            status=status.HTTP_200_OK,
        )


class MyReviewListAPIView(generics.ListAPIView):
    """
    내 리뷰 목록 조회 API
    - 삭제된 리뷰는 Soft Delete 기본 매니저에 의해 자동 제외
    """

    serializer_class = ReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Review.objects
            .select_related("user", "product", "ai_result")
            .prefetch_related("images", "likes", "bookmarks")
            .filter(user=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_context(self):
        return {"request": self.request}


class ReviewImageUploadAPIView(APIView):
    """
    리뷰 이미지 업로드 API
    - 삭제된 리뷰에는 이미지 업로드 불가 (Soft Delete 매니저로 자동 차단)
    """

    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, review_id):
        review = get_object_or_404(Review, id=review_id)

        if review.user != request.user:
            return Response(
                {"detail": "본인 리뷰에만 이미지를 추가할 수 있습니다."},
                status=status.HTTP_403_FORBIDDEN,
            )

        files = request.FILES.getlist("uploaded_images")

        if not files:
            return Response(
                {"detail": "업로드할 이미지가 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        created_images = []
        for file in files:
            image = ReviewImage.objects.create(
                review=review,
                image=file,
            )
            created_images.append(image)

        serializer = ReviewImageSerializer(
            created_images,
            many=True,
            context={"request": request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReviewAIResultAPIView(APIView):
    """
    특정 리뷰의 AI 분석 결과 조회 API
    - 삭제된 리뷰는 Soft Delete 매니저에 의해 자동 제외
    """

    permission_classes = [permissions.AllowAny]

    def get(self, request, review_id):
        review = get_object_or_404(
            Review.objects.select_related("ai_result"),
            id=review_id,
        )

        if not hasattr(review, "ai_result"):
            return Response(
                {"detail": "AI 분석 결과가 없습니다."},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = ReviewAISerializer(review.ai_result)
        return Response(serializer.data, status=status.HTTP_200_OK)
