from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework import status
from .models import LocalMatch
from .serializers import LocalMatchSerializer
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from .utils.update_statistics import update_statistics

class GameViewSet(ModelViewSet):
    queryset = LocalMatch.objects.all()
    serializer_class = LocalMatchSerializer
    
