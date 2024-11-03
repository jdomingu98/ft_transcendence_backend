from rest_framework.viewsets import ModelViewSet
from ..models import LocalMatch
from .serializers import LocalMatchSerializer


class GameViewSet(ModelViewSet):
    queryset = LocalMatch.objects.all()
    http_method_names = ['post']
    serializer_class = LocalMatchSerializer
