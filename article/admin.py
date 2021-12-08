from django.contrib import admin
from article.models import Article
from article.models import ArticleDetail

admin.site.register(Article)
admin.site.register(ArticleDetail)