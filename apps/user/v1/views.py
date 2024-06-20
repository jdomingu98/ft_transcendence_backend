from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.hashers import make_password

from ..enums import Visibility

from apps.user.models import User

class Register(APIView):

    def post(self, request):
        # TODO: Review params for endpoint
        name = request.data.get('name')
        password = request.data.get('password')
        passwordRepeat = request.data.get('passwordRepeat')

        if password != passwordRepeat:
            return Response({'message': 'passwords do not match'}, status=status.HTTP_400_BAD_REQUEST)

        hashed_password = make_password(password)

        user = User(
            username=name,
            password=hashed_password,
            language='es',
            visibility=Visibility.PUBLIC.value
        )
        user.save()
        return Response({'message': 'you are register'}, status=status.HTTP_200_OK)



