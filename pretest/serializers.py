from .models import PretestModel
from rest_framework import serializers


class PretestSerializer(serializers.ModelSerializer):
    class Meta:
        model = PretestModel
        fields = '__all__'


class PrestestPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = PretestModel
        fields = ('user', 'Videofile')
