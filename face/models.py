from django.db import models
from login.models import SocialAccount


# Create your models here.
class FaceModel(models.Model):
    user = models.ForeignKey(SocialAccount, related_name='social_account_to_face', on_delete=models.CASCADE, null=True)
    CreateDatetime = models.DateTimeField(auto_now_add=True)

    VideofileName = models.CharField(max_length=50)
    Videofile = models.FileField(upload_to='video')

    # #可能用不到
    # CsvfileName = models.CharField(max_length=50,default='null')
    # CsvfilePath = models.CharField(max_length=50,default='null')

    AvgEyebrowHeight = models.CharField(max_length=50, default='null')
    AvgEyebrowPitch = models.CharField(max_length=50, default='null')
    AvgMouthHeight = models.CharField(max_length=50, default='null')
    AvgMouthPitch = models.CharField(max_length=50, default='null')

    EyebrowHeight_PR = models.CharField(max_length=50, default='null')
    EyebrowPitch_PR = models.CharField(max_length=50, default='null')
    Mouth_PR = models.CharField(max_length=50, default='null')

    WinkTime = models.CharField(max_length=50, default='null')
    DistractTime = models.CharField(max_length=50, default='null')

    Suggest = models.JSONField(null=True)

    Total_Score = models.CharField(max_length=50, default='null')

    class Meta:
        db_table = "face"

