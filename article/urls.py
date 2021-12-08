from django.urls import path
from article.views import ArticleList, ArticleQueryByUserLatest
from article.views import ArticleDetailList, ArticleDetailQuery, ArticleQueryByUser

urlpatterns = [
    path('article/', ArticleList.as_view()),
    path('article/<int:user_id>/', ArticleQueryByUser.as_view()),
    path('article/<int:user_id>/latest/', ArticleQueryByUserLatest.as_view()),
    path('articleDetail/', ArticleDetailList.as_view()),
    path('articleDetail/<int:article_id>/', ArticleDetailQuery.as_view()),
]
