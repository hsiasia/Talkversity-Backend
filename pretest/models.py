from django.db import models
from login.models import SocialAccount


# Create your models here.
class PretestModel(models.Model):
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, null=True)
    VideofileName = models.CharField(max_length=50)
    Videofile = models.FileField(upload_to='prevideo')
    # csvfilename = models.CharField(max_length=50)
    # csvfilepath = models.FilePathField(upload_to='predata/')
    PreEyebrowHeight = models.CharField(max_length=50, default='null')
    PreEyebrowPitch = models.CharField(max_length=50, default='null')
    PreMouthHeight = models.CharField(max_length=50, default='null')
    PreMouthPitch = models.CharField(max_length=50, default='null')
    PreEyesPitch = models.CharField(max_length=50, default='null')
    PreSoundAvg = models.CharField(max_length=50, default='null')
    PreSoundFreq = models.CharField(max_length=50, default='null')
    Gender = models.CharField(max_length=50, default='M')

    created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "pretest"

    def __str__(self):
        return self.VideofileName
