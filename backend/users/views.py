from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from drf_spectacular.utils import extend_schema

from .serializers import RegisterSerializer, UserSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    @extend_schema(
        summary="ثبت‌نام کاربر",
        description="ایجاد یک حساب کاربری جدید.",
        tags=["Authentication"],
        auth=[],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class LoginView(TokenObtainPairView):

    @extend_schema(
        summary="ورود کاربر",
        description="دریافت Access Token و Refresh Token.",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="اطلاعات کاربر فعلی",
        description="نمایش اطلاعات کاربری که با JWT وارد شده است.",
        tags=["Authentication"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_object(self):
        return self.request.user


class RefreshTokenView(TokenRefreshView):

    @extend_schema(
        summary="تازه‌سازی Access Token",
        description="دریافت Access Token جدید با استفاده از Refresh Token.",
        tags=["Authentication"],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)