from django.urls import path
from achievements.views import AchievementList, AchievementQueryByUser, AddUserAchievement, GradeList, GradeDetail, \
    UserGradeList, AchievementQueryByUserWithoutCount, AchievementGetTotalData

urlpatterns = [
    path('achievement/', AchievementList.as_view()),
    path('achievement/<int:user_id>/', AchievementQueryByUser.as_view()),
    path('achievement/<int:user_id>/date/', AchievementQueryByUserWithoutCount.as_view()),
    path('achievement/<int:user_id>/alldata/', AchievementGetTotalData.as_view()),
    path('achievement/add/', AddUserAchievement.as_view()),
    path('grade/', GradeList.as_view()),
    path('grade/<int:grade_id>/', GradeDetail.as_view()),
    path('grade/user/', UserGradeList.as_view())
]
