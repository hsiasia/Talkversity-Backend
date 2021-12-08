from django.db import models
from django.contrib.auth.models import User


class SocialAccount(models.Model):
    provider = models.CharField(max_length=200, default='google')  # 若未來新增其他的登入方式,如Facebook,GitHub
    given_name = models.CharField(max_length=200, null=True, blank=True)  # 名字
    family_name = models.CharField(max_length=200, null=True, blank=True)  # 姓氏
    name = models.CharField(max_length=200, null=True, blank=True)  # fullname
    picture = models.CharField(max_length=200, null=True, blank=True)  # 頭貼
    locale = models.CharField(max_length=200, default='zh-TW')  # 語系
    email = models.EmailField(max_length=200, null=True, blank=True)
    gender = models.CharField(max_length=1, null=True)
    coach_gender = models.CharField(max_length=1, null=True)
    grade = models.IntegerField(default=0)
    total_word = models.IntegerField(default=0)
    unique_id = models.CharField(max_length=200)
    initial = models.BooleanField(default=False)
    user = models.ForeignKey(
        User, related_name='social', on_delete=models.CASCADE)  # foreign_key to auth_user

    def __int__(self):
        return self.id
