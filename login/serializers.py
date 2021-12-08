from login.models import SocialAccount
from rest_framework import serializers


class LoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ('__all__')


class UserGenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ('id', 'gender')


class CoachGenderSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialAccount
        fields = ('id', 'coach_gender')
