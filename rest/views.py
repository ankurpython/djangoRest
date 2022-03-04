from django.shortcuts import render
from rest_framework import viewsets, status
# Create your views here.
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from rest.models import TaskModel
from rest.serializers import TaskSerializer


class Tasks(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    queryset = TaskModel.objects.all()


class Logout(viewsets.ViewSet):
    @staticmethod
    def create(request):
        try:
            data = request.data
            refresh_token = data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"msg": "success"}, status=status.HTTP_200_OK)
        except Exception as msg:
            return Response({"msg": str(msg)}, status=status.HTTP_400_BAD_REQUEST)