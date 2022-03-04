from rest_framework.serializers import ModelSerializer

from rest.models import TaskModel


class TaskSerializer(ModelSerializer):
    class Meta:
        model = TaskModel
        fields = '__all__'
