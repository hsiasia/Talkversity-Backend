from rest_framework import serializers
from sound.models import Sound


class SoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sound
        fields = '__all__'


class SoundPostSerializer(serializers.Serializer):
    video_file = serializers.FileField()
    user_id = serializers.IntegerField()
