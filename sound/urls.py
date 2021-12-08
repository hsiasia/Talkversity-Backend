from django.urls import path
from sound.views import SoundList, SoundQueryByUser, SoundQueryByUserLatest

urlpatterns = [
    path('sound/', SoundList.as_view()),
    path('sound/<int:user_id>/', SoundQueryByUser.as_view()),
    path('sound/<int:user_id>/latest/', SoundQueryByUserLatest.as_view()),
]
