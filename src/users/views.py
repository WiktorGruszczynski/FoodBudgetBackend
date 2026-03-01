from django.contrib.auth import authenticate, login
from drf_spectacular.utils import OpenApiResponse, extend_schema
from foodbudget_core.views import BasePublicAPIView
from rest_framework import status
from rest_framework.response import Response

from users.models import User
from users.serializers import CredentialsSerializer


@extend_schema(tags=["Users"])
class RegisterUserView(BasePublicAPIView):
    @extend_schema(
        summary="Register new user",
        request=CredentialsSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="Registered new user"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid request"),
            status.HTTP_409_CONFLICT: OpenApiResponse(description="Account already exists"),
        },
    )
    def post(self, request):
        serializer = CredentialsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"status": "error"}, status=400)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        if User.objects.filter(email=email).exists():
            return Response({"status": "error"}, status=409)

        user = User(email=email)
        user.set_password(password)
        user.save()

        return Response({"status": "success"}, status=201)


@extend_schema(tags=["Users"])
class LoginUserView(BasePublicAPIView):
    @extend_schema(
        summary="Log in user",
        request=CredentialsSerializer,
        responses={
            status.HTTP_200_OK: OpenApiResponse(description="Succesfully logged in user"),
            status.HTTP_401_UNAUTHORIZED: OpenApiResponse(description="Unauthorized access"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid request"),
        },
    )
    def post(self, request):
        serializer = CredentialsSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"status": "error"}, status=400)

        user = authenticate(request, email=serializer.validated_data["email"], password=serializer.validated_data["password"])

        if user is not None:
            login(request, user)
            return Response({"status": "ok"}, status=200)

        return Response({"status": "error"}, status=401)
