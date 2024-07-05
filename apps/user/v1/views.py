from rest_framework.generics import CreateAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from .serializers import RegisterSerializer, LoginSerializer
from ..models import User


class Register(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()

class LoginView(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data
            return Response({"message": "Successful login"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LogoutView(APIView):
    def post(self, request):
        if request.user.is_authenticated:
            request.user.is_connected = False
            request.user.save()
            logout(request)
            return Response({"message": "Successfully logged out."}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Not logged in."}, status=status.HTTP_400_BAD_REQUEST)