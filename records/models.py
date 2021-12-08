from django.db import models
from login.models import SocialAccount
from article.models import Article
from sound.models import Sound
from target.models import Scenario
from face.models import FaceModel


# Create your models here.
class Record(models.Model):
    user = models.ForeignKey(SocialAccount, on_delete=models.CASCADE, null=True)
    scenario = models.ForeignKey(Scenario, on_delete=models.CASCADE, null=True)
    article = models.ForeignKey(Article, on_delete=models.CASCADE, null=True)
    sound = models.ForeignKey(Sound, on_delete=models.CASCADE, null=True)
    face = models.ForeignKey(FaceModel, on_delete=models.CASCADE, null=True)
    total_score = models.CharField(null=True, max_length=1)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "record"
