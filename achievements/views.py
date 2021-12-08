from django.db.models import Count
from django.http import JsonResponse

from achievements.models import Achievement, UserAchievement, UserGrade, GradeAchievement
from login.models import SocialAccount
from achievements.serializers import AchievementSerializer, UserAchievementSerializer, GradeSerializer, \
    UserGradeSerializer
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema


# Create your views here.
class AchievementList(generics.ListCreateAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    @swagger_auto_schema(
        operation_summary='取得所有成就',
        operation_description='列出所有成就',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='新增成就',
        operation_description='新增成就以及成就條件',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# 取得特定使用者的有的成就資訊
class AchievementQueryByUser(generics.ListAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的所有成就資訊(有記次數)',
        operation_description='列出特定使用者的所有成就資訊',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        # 計算特定使用者拿到的不同成就的累積次數
        q = UserAchievement.objects.filter(user=user_id).order_by('achievement_id'). \
            values('user_id', 'achievement_id',
                   'achievement__name'
                   ).annotate(
            achievement_count=Count('achievement_id'))
        return JsonResponse({'data': list(q)})


# 取得特定使用者的有的成就資訊，依時間排序
class AchievementQueryByUserWithoutCount(generics.ListAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的所有成就資訊',
        operation_description='取得特定使用者的所有成就資訊，依完成時間排序',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        # 計算特定使用者拿到的不同成就的累積次數
        q = UserAchievement.objects.filter(user=user_id). \
            values('user_id', 'achievement_id',
                   'achievement__name',
                   'created_date'
                   )
        return JsonResponse({'data': list(q)})


# 新增使用者的成就
# 在新增成就的時候也去確認有沒有達到年級任務
# 在每次測驗完要記錄結果的時候call 確認達到哪些成就
class AddUserAchievement(generics.CreateAPIView):

    @swagger_auto_schema(
        operation_summary='新增特定使用者的成就',
        operation_description='新增特定使用者的成就',
        request_body=UserAchievementSerializer
    )
    def post(self, request, *args, **kwargs):
        user = SocialAccount.objects.filter(id=request.data['user']).get()
        achievement = Achievement.objects.filter(id=request.data['achievement']).get()
        UserAchievement.objects.create(user=user, achievement=achievement)
        data = UserAchievement.objects.filter(user=user, achievement=achievement) \
            .values('id',
                    'user_id',
                    'achievement_id',
                    'achievement__name',
                    'created_date').latest(
            'created_date')
        # 使用者目前的年級
        grade = list(SocialAccount.objects.filter(id=request.data['user']).values('grade'))[0]['grade']
        # 下個年級需要的成就
        next_grade_requirement = GradeAchievement.objects.filter(grade=grade + 1). \
            values(
            'grade',
            'achievement_id',
            'achievement__name',
            'time')

        # 計算特定使用者拿到的不同成就的累積次數
        # 使用者現在有的成就

        user_have = UserAchievement.objects.filter(user=user).order_by('achievement_id') \
            .values('user_id', 'achievement_id',
                    'achievement__name').annotate(time=Count('achievement_id'))
        # 比對
        # 看user_have的有沒有達到next_grade_requirement 拿到五個條件
        g_require = 0
        for i in list(user_have):
            a_id = i['achievement_id']
            g_time = i['time']
            check_point_1 = GradeAchievement.objects.filter(grade=grade + 1, achievement=a_id,
                                                            time__lte=g_time).values()
            if len(check_point_1):
                g_require += 1

        # print(g_require)

        # 達成條件 升等
        if g_require == 5:
            print('upgrade')
            grade = grade + 1
            UserGrade.objects.create(user_id=user, grade_id=grade)
            SocialAccount.objects.filter(id=user).update(grade=grade)

        return JsonResponse({'data': data})


# 年級任務
class GradeList(generics.ListCreateAPIView):
    queryset = GradeAchievement.objects.all()
    serializer_class = GradeSerializer

    @swagger_auto_schema(
        operation_summary='取得所有年級資訊',
        operation_description='列出所有年級資訊',
    )
    def get(self, request, *args, **kwargs):
        q = GradeAchievement.objects.all().values('id', 'grade', 'achievement_id', 'achievement__name', 'time')
        return JsonResponse({'data': list(q)})

    @swagger_auto_schema(
        operation_summary='新增年級以及年級任務',
        operation_description='新增年級以及年級任務',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


# 拿到特定年即需要的任務
class GradeDetail(generics.RetrieveAPIView):
    queryset = GradeAchievement.objects.all()
    serializer_class = GradeSerializer

    @swagger_auto_schema(
        operation_summary='取得特定年級任務的資訊',
        operation_description='列出特定年級任務的資訊',
    )
    def get(self, request, *args, **kwargs):
        grade_id = self.kwargs['grade_id']
        q = GradeAchievement.objects.filter(grade=grade_id).values('id', 'grade', 'achievement_id', 'achievement__name',
                                                                   'time')
        return JsonResponse({'data': list(q)})


#  年級對照使用者，用來新增使用者現在是幾年級，會順便更新user table裡面的grade
class UserGradeList(generics.ListCreateAPIView):
    queryset = UserGrade.objects.all()
    serializer_class = UserGradeSerializer

    @swagger_auto_schema(
        operation_summary='取得所有使用者跟年級的紀錄',
        operation_description='列出所有使用者跟年級的紀錄',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='新增使用者的年級紀錄',
        operation_description='新增使用者的年級紀錄',
    )
    def post(self, request, *args, **kwargs):
        grade = request.data['grade']
        SocialAccount.objects.filter(id=request.data['user']).update(grade=grade)
        return self.create(request, *args, **kwargs)


class AchievementGetTotalData(generics.ListAPIView):
    queryset = Achievement.objects.all()
    serializer_class = AchievementSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的所有成就狀態',
        operation_description='列出特定使用者的所有成就狀態',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        grade_detail = GradeAchievement.objects.all().values('grade', 'achievement_id', 'achievement__name', 'time')
        # 計算特定使用者拿到的不同成就的累積次數
        user_have = UserAchievement.objects.filter(user=user_id).order_by('achievement_id') \
            .values('user_id', 'achievement_id',
                    'achievement__name').annotate(current=Count('achievement_id'))

        for grade_detail_index in list(grade_detail):
            grade_detail_index['current'] = 0
            grade_detail_index['is_achieve'] = 0
            for user_have_index in list(user_have):
                if grade_detail_index['achievement__name'] == user_have_index['achievement__name']:
                    if user_have_index['current'] != 0:
                        grade_detail_index['current'] = user_have_index['current']
                        # 達成成就
                        if user_have_index['current'] >= grade_detail_index['time']:
                            grade_detail_index['is_achieve'] = 1
                        else:
                            grade_detail_index['is_achieve'] = 0

        return JsonResponse({'data': list(grade_detail)})
