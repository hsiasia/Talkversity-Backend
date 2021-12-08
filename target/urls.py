from django.urls import path
from target import views

urlpatterns = [
    path('target/', views.TargetList.as_view()),
    path('target/<int:pk>/', views.TargetDetail.as_view()),
]