from django.urls import path
from scenario import views

urlpatterns = [
    path('scenario/', views.ScenarioList.as_view()),
    path('scenario/<int:pk>/', views.ScenarioDetail.as_view()),
]