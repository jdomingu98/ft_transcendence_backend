from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import RegisterSerializer


class Register(APIView):

    def post(self, request):
        register_serializer = RegisterSerializer(data=request.data)
        register_serializer.is_valid(raise_exception=True)        
        register_serializer.save()
        return Response(status=status.HTTP_201_CREATED)
