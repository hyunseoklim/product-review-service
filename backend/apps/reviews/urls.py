from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ReviewViewSet,
    MyReviewListAPIView,
    ReviewImageUploadAPIView,
    ReviewAIResultAPIView,
)

router = DefaultRouter()
router.register("", ReviewViewSet, basename="review")

urlpatterns = [
    path("my/", MyReviewListAPIView.as_view(), name="my-review-list"),
    path("<int:review_id>/images/", ReviewImageUploadAPIView.as_view(), name="review-image-upload"),
    path("<int:review_id>/ai/", ReviewAIResultAPIView.as_view(), name="review-ai-result"),
    path("", include(router.urls)),
]