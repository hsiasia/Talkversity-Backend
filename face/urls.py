from django.urls import path
from face.views import FaceView, FaceDataByIdView, FaceQueryByUserLatest

urlpatterns = [
    path('face/', FaceView.as_view()),
    path('face/<str:file_id>/', FaceDataByIdView.as_view()),
    path('face/<int:user_id>/latest/', FaceQueryByUserLatest.as_view())
]
