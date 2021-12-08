from django.db import models
from datetime import datetime
# Create your models here.
from login.models import SocialAccount


# 成就列表
class Achievement(models.Model):
    name = models.CharField(max_length=50)
    speech_score = models.CharField(max_length=4, null=True, default='null')
    face_score = models.CharField(max_length=4, null=True, default='null')
    article_score = models.CharField(max_length=4, null=True, default='null')
    total_word = models.IntegerField(null=True, default=0)
    total_score = models.CharField(max_length=4, null=True, default='null')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'achievement'


# user有的成就
class UserAchievement(models.Model):
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, null=True)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now=True,null=True)
    class Meta:
        db_table = 'user_achievement'


# 年級任務
class GradeAchievement(models.Model):
    grade = models.IntegerField()
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE, null=True)
    time = models.IntegerField()

    class Meta:
        db_table = 'grade'


# 年級對照
class UserGrade(models.Model):
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, null=True)
    grade = models.ForeignKey(GradeAchievement, on_delete=models.CASCADE, null=True)
    created_date = models.DateTimeField(auto_now=True,null=True)

    class Meta:
        db_table = 'user_grade'
