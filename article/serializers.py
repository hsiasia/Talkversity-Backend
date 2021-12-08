from rest_framework import serializers
from article.models import Article, ArticleDetail


class ArticleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleDetail
        fields = '__all__'


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = '__all__'


class ArticlePostSerializer(serializers.Serializer):
    video_file = serializers.FileField()
    user_id = serializers.IntegerField()
