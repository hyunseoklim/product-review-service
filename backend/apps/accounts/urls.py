from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import (
    UserViewSet,
    SignupAPIView,
    MeAPIView,
    SignupPageView,
    LoginPageView,
    MyPageView,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    # =================================================
    # Template Page URLs
    # =================================================
    path("signup/", SignupPageView.as_view(), name="signup-page"),
    path("login/", LoginPageView.as_view(), name="login-page"),
    path("mypage/", MyPageView.as_view(), name="mypage"),

    # =================================================
    # API URLs
    # =================================================
    path("api/", include(router.urls)),
    path("api/signup/", SignupAPIView.as_view(), name="signup-api"),
    path("api/login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/me/", MeAPIView.as_view(), name="me-api"),
]