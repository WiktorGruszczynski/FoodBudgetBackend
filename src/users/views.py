from drf_spectacular.utils import OpenApiResponse, extend_schema
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User
from users.serializers import RegisterSerializer


class RegisterUserView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        summary="Register new user",
        request=RegisterSerializer,
        responses={
            status.HTTP_201_CREATED: OpenApiResponse(description="Registered new user"),
            status.HTTP_400_BAD_REQUEST: OpenApiResponse(description="Invalid request"),
            status.HTTP_409_CONFLICT: OpenApiResponse(description="Account already exists"),
        },
    )
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({"status": "error"}, status=400)

        email = serializer.validated_data["email"]
        password = serializer.validated_data["password"]

        if User.objects.filter(email=email).exists():
            return Response({"status": "error"}, status=409)

        user = User(email=email)
        user.set_password(password)
        user.save()

        return Response({"status": "success", "email": user.email}, status=201)
