from rest_framework import serializers
from achievements.models import Achievement, UserAchievement, GradeAchievement, UserGrade
from login.models import SocialAccount


class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'


class UserAchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserAchievement
        fields = '__all__'


class GradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = GradeAchievement
        fields = '__all__'


class UserGradeSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserGrade
        fields = '__all__'
