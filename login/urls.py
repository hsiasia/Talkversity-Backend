from django.urls import path
from login.views import SocialUsersView, UsersGender, CoachGender, SocialUsersByIdView, UsersTotalWordQuery, userPretest

urlpatterns = [
    # get user info
    path('users/', SocialUsersView.as_view()),
    path('users/<int:user_id>/', SocialUsersByIdView.as_view()),
    path('users/gender/', UsersGender.as_view()),
    path('users/pretest/', userPretest.as_view()),
    path('users/coach/gender/', CoachGender.as_view()),
    path('users/totalword/<int:user_id>/', UsersTotalWordQuery.as_view()),
]
