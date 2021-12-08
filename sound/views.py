from django.db.models import Count
from django.forms import model_to_dict
from django.http import JsonResponse
from rest_framework.parsers import MultiPartParser
import subprocess
from achievements.models import Achievement, UserAchievement, GradeAchievement, UserGrade
from login.models import SocialAccount
from records.models import Record
from sound.models import Sound
from pretest.models import PretestModel
from sound.sound_analysis_boy import *
from sound.sound_analysis_girl import *
from rest_framework.generics import GenericAPIView, ListAPIView
from sound.serializers import SoundSerializer, SoundPostSerializer
from drf_yasg.utils import swagger_auto_schema


def get_video_length(filename):
    import subprocess, json

    result = subprocess.check_output(
        f'ffprobe -v quiet -show_streams -select_streams v:0 -of json "{filename}"',
        shell=True).decode()
    fields = json.loads(result)['streams'][0]
    duration = fields['duration']
    return duration


# Create your views here.
# 新增聲音分析
class SoundList(GenericAPIView):
    queryset = Sound.objects.all()
    serializer_class = SoundSerializer
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary='取得聲音表現分析列表',
        operation_description='列出所有的聲音表現分析',
    )
    def get(self, request, *args):
        sound = self.get_queryset()
        serializer = self.serializer_class(sound, many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    @swagger_auto_schema(
        operation_description='新增聲音表現的分析結果',
        operation_summary='新增聲音表現分析結果',
        request_body=SoundPostSerializer
    )
    def post(self, request, *args, **kwargs):
        user_id = request.POST['user_id']
        video_file = request.FILES['video_file']

        user = SocialAccount.objects.filter(id=user_id).get()
        # 拿性別
        gender = user.gender
        # 拿最新的一筆前測資料
        pretest = PretestModel.objects.filter(user_id=user_id).order_by('-id')[0]
        pretest_fre = float(pretest.PreSoundFreq)
        pretest_db = float(pretest.PreSoundAvg)
        video_file_path = video_file.temporary_file_path()
        duration = get_video_length(video_file_path)

        if float(duration) <= 15.0:
            return JsonResponse({'data': 'video time too short'})

        if gender == 'F':
            response = main_girl(video_file_path, pretest_fre, pretest_db)
        else:
            response = main_boy(video_file_path, pretest_fre, pretest_db)

        Sound.objects.create(
            user=user,
            pretest_db=pretest_db,
            avg_db=response['avg_db'],
            stop_too_long_score=response['stop_too_long'],
            weird_sound_score=response['weird_sound'],
            voice_calm_score=response['voice_calm'],
            frequency_score=response['frequency'],
            amplitude_score=response['amplitude'],
            overall_score=response['overall_score'],
            rank=response['rank'],
            analyze_json=response['analyze_json'],
            feedback=response['feedback']
        )
        # 拿到當次的 sound 成績
        sound_rank = response['rank']
        # 檢查是否達成成就
        if sound_rank == 'A':
            # 新增一筆紀錄
            rank_a = Achievement.objects.filter(speech_score='A').get()
            UserAchievement.objects.create(user=user, achievement=rank_a)
        elif sound_rank == 'S':
            # 新增S跟A兩筆紀錄
            rank_s = Achievement.objects.filter(speech_score='S').get()
            rank_a = Achievement.objects.filter(speech_score='A').get()
            UserAchievement.objects.create(user=user, achievement=rank_s)
            UserAchievement.objects.create(user=user, achievement=rank_a)

        # 拿到剛建的 sound_object object
        sound_object = Sound.objects.last()

        # 使用者目前的年級
        grade = user.grade
        # 計算特定使用者拿到的不同成就的累積次數
        user_have = UserAchievement.objects.filter(user=user).order_by('achievement_id') \
            .values('user_id', 'achievement_id',
                    'achievement__name').annotate(time=Count('achievement_id'))
        # 看user_have的有沒有達到next_grade_requirement 拿到五個條件
        g_require = 0
        for i in list(user_have):
            a_id = i['achievement_id']
            g_time = i['time']
            check_point_1 = GradeAchievement.objects.filter(grade=grade + 1, achievement=a_id,
                                                            time__lte=g_time).values()
            if len(check_point_1):
                g_require += 1

        if g_require == 5:
            # 達成條件 升等
            grade = grade + 1
            UserGrade.objects.create(user_id=user, grade_id=grade)
            SocialAccount.objects.filter(id=user).update(grade=grade)

        # 找到在record內最新一筆資料 更新sound進去
        record = Record.objects.latest("created")
        record.sound = sound_object
        record.save()
        return JsonResponse({'data': model_to_dict(sound_object)})


class SoundQueryByUser(ListAPIView):
    queryset = Sound.objects.all()
    serializer_class = SoundSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的聲音表現資訊',
        operation_description='列出特定使用者的聲音表現資訊',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        queryset = Sound.objects.filter(user_id=user_id).values()
        return JsonResponse({'data': list(queryset)})


class SoundQueryByUserLatest(ListAPIView):
    queryset = Sound.objects.all()
    serializer_class = SoundSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者最新的聲音表現資訊',
        operation_description='列出特定使用者最新的聲音表現資訊',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        queryset = Sound.objects.filter(user_id=user_id).latest("created")
        return JsonResponse({'data': model_to_dict(queryset)})
