from .models import FaceModel
from rest_framework import serializers

class FaceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceModel
        fields = '__all__'

class FacePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceModel
        fields = ('user', 'Videofile')

class FaceGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaceModel
        fields = ('CreateDatetime')