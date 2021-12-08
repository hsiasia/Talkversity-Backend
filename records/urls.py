from django.urls import path
from records.views import RecordList, RecordDetail, RecordQueryByUser, WeekRecordQueryByUser, SevenRecordQueryByUser

urlpatterns = [
    path('record/', RecordList.as_view()),
    path('record/<int:pk>/', RecordDetail.as_view()),
    path('record/user/<int:user_id>/', RecordQueryByUser.as_view()),
    path('record/<int:user_id>/weekdate/', WeekRecordQueryByUser.as_view()),
    path('record/<int:user_id>/latest/', SevenRecordQueryByUser.as_view()),
]