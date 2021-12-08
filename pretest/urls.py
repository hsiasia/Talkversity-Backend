from django.urls import path
from pretest.views import PretestView

urlpatterns = [
    path('pretest/', PretestView.as_view()),
]
