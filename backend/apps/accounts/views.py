from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet

from .models import User
from .serializers import UserSerializer, SignupSerializer


# -------------------------------------------------
# API Views
# -------------------------------------------------
class UserViewSet(ViewSet):
    """
    사용자 조회용 ViewSet
    """

    permission_classes = [permissions.AllowAny]

    def list(self, request):
        users = User.objects.all().order_by("-id")
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class SignupAPIView(generics.CreateAPIView):
    """
    회원가입 API
    POST /accounts/api/signup/
    """

    serializer_class = SignupSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "created_at": user.created_at,
            },
            status=status.HTTP_201_CREATED,
        )


class MeAPIView(generics.RetrieveAPIView):
    """
    현재 로그인한 사용자 정보 조회 API
    GET /accounts/api/me/
    """

    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


# -------------------------------------------------
# Template Views
# -------------------------------------------------
class SignupPageView(TemplateView):
    template_name = "accounts/signup.html"


class LoginPageView(TemplateView):
    template_name = "accounts/login.html"


class MyPageView(TemplateView):
    template_name = "accounts/mypage.html"