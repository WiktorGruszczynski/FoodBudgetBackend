from rest_framework import permissions
from rest_framework.views import APIView


class BasePublicAPIView(APIView):
    permission_classes = [permissions.AllowAny]


class BaseAuthApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
