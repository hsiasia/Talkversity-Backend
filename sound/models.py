from django.db import models
from login.models import SocialAccount


# Create your models here.
class Sound(models.Model):
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, null=True)
    pretest_db = models.FloatField(null=True)
    avg_db = models.FloatField(null=True)
    stop_too_long_score = models.IntegerField(null=True)
    weird_sound_score = models.IntegerField(null=True)
    voice_calm_score = models.IntegerField(null=True)
    frequency_score = models.IntegerField(null=True)
    amplitude_score = models.IntegerField(null=True)
    overall_score = models.IntegerField(null=True)
    rank = models.CharField(null=True, max_length=1)
    analyze = models.CharField(max_length=250, null=True)
    analyze_json = models.JSONField(null=True)
    feedback = models.CharField(max_length=250, null=True)
    created = models.DateTimeField(auto_now_add=True, null=True)


    class Meta:
        db_table = "sound"
