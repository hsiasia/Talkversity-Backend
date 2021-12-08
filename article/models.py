from django.db import models
from login.models import SocialAccount


# Create your models here.
class Article(models.Model):
    user = models.ForeignKey(SocialAccount, related_name='social_account', on_delete=models.CASCADE, null=True)
    fulltext = models.TextField()
    text_len = models.IntegerField()
    pure_text_len = models.IntegerField()
    talk_speed = models.FloatField(null=True)
    redundant_1_count = models.IntegerField()
    redundant_2_count = models.IntegerField()
    redundant_3_count = models.IntegerField()
    redundant_4_count = models.IntegerField()
    joy_score = models.FloatField()
    trust_score = models.FloatField()
    surprise_score = models.FloatField()
    anticipation_score = models.FloatField()
    fear_score = models.FloatField()
    sadness_score = models.FloatField()
    anger_score = models.FloatField()
    disgust_score = models.FloatField()
    total_score = models.FloatField()
    rank = models.CharField(null=True, max_length=1)
    suggest = models.TextField(blank=True, null=True)
    suggest_json = models.JSONField(null=True)

    last_modify_date = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "article"


class ArticleDetail(models.Model):
    article = models.ForeignKey(Article,
                                related_name='articleDetails',
                                on_delete=models.CASCADE, null=True)
    sentence = models.CharField(max_length=200)
    sentiment = models.CharField(max_length=200)

    def __str__(self):
        return self.sentence

    class Meta:
        db_table = "article_detail"
