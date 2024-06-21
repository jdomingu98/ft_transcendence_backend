from rest_framework.generics import CreateAPIView
from .serializers import RegisterSerializer
from ..models import User


class Register(CreateAPIView):
    serializer_class = RegisterSerializer
    queryset = User.objects.all()
