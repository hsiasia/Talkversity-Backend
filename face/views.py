from django.db.models import Count
from django.forms import model_to_dict
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import GenericAPIView, ListAPIView
from django.http import JsonResponse, FileResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import AllowAny
from achievements.models import GradeAchievement, UserGrade, UserAchievement, Achievement
from article.models import Article
from sound.models import Sound
from login.models import SocialAccount
from records.models import Record
from .gaze_tracking import Tools
from pretest.models import PretestModel
from face.serializers import FaceSerializer, FacePostSerializer
from face.models import FaceModel
import time

class FaceView(GenericAPIView):
    queryset = FaceModel.objects.all()
    serializer_class = FaceSerializer
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description='新增實際影片',
        operation_summary='新增臉部數據',
        request_body=FacePostSerializer
    )
    def post(self, request, *args, **krgs):
        data = request.data
        try:
            serializer = FacePostSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            user_id = data.__getitem__('user')

            # 檔案上傳暫存
            serializer.save()

            face_Pre = FaceModel.objects.filter(user_id=user_id).latest("CreateDatetime")
            face_Pre = model_to_dict(face_Pre)
            Path = face_Pre['Videofile']

            PathSplit = str(Path).split('/')
            fileName = PathSplit[1]

            object = PretestModel.objects.filter(user_id=user_id).values()
            object = object[0]

            # 計時
            time_start = time.time()
            # 背景偵測與回傳值
            ToolsModel = Tools(fileName, object['PreEyebrowHeight'], object['PreEyebrowPitch'],
                               object['PreMouthHeight'], object['PreMouthPitch'], object['PreEyesPitch'])
            eyebrow_height, eyebrow_pitch, mouth_height, mouth_pitch, winktime, distractrate = ToolsModel.doAll()
            # 列印回傳值
            # print(eyebrow_height, eyebrow_pitch, mouth_height, mouth_pitch, winktime, distractrate)

            # 更新回傳值數據
            VideofilePath = './media/video/' + str(fileName)

            eyebrow_height_pr, eyebrow_pitch_pr, mouth_pr = self.CaculateScore(eyebrow_height, eyebrow_pitch,
                                                                               mouth_height, mouth_pitch)
            if eyebrow_pitch_pr == "過度":
                ori_score = (eyebrow_height_pr + mouth_pr + 60)
            elif eyebrow_pitch_pr == "適度":
                ori_score = (eyebrow_height_pr + mouth_pr + 80)
            elif eyebrow_pitch_pr == "放鬆":
                ori_score = (eyebrow_height_pr + mouth_pr + 100)

            if ori_score >= 90:
                score = 'S'
            elif ori_score >= 80:
                score = 'A'
            elif ori_score >= 70:
                score = 'B'
            elif ori_score >= 60:
                score = 'C'
            elif ori_score < 60:
                score = 'D'
            suggest = []
            if winktime < 20:
                suggest.append('The number of blinks is normal, please keep it up!')
            elif winktime > 20:
                suggest.append('Blinking frequency is slightly higher, so pay attention to it!')

            if distractrate > 0.8:
                suggest.append('Highly dedicated, very good!')
            elif distractrate < 0.6:
                suggest.append('Slightly distracted, could pay more attention to the interviewer!')
            else:
                suggest.append('Be extremely inattentive and pay special attention to looking directly at the audience!')

            if eyebrow_height_pr > 80:
                suggest.append('Impressive expressions!')
            elif eyebrow_height_pr < 60:
                suggest.append('Suggestions to increase the richness of expressions!')

            if mouth_pr > 80:
                suggest.append('Your smile is so charming!!')
            elif mouth_pr < 60:
                suggest.append('It is recommended to keep smiling more often and try to put on your smile while '
                               'talking!')

            suggest_dict = {}
            d_index = 0
            for i in suggest:
                suggest_dict[d_index] = i
                d_index += 1
            face = FaceModel.objects.filter(Videofile=Path)
            face.update(
                VideofileName=str(fileName),
                Videofile=VideofilePath,
                AvgEyebrowHeight=eyebrow_height,
                AvgEyebrowPitch=eyebrow_pitch,
                AvgMouthHeight=mouth_height,
                AvgMouthPitch=mouth_pitch,
                WinkTime=winktime,
                DistractTime=distractrate,
                EyebrowHeight_PR=eyebrow_height_pr,
                EyebrowPitch_PR=eyebrow_pitch_pr,
                Mouth_PR=mouth_pr,
                Suggest=suggest_dict,
                Total_Score=score)

            time_end = time.time()
            time_c = time_end - time_start  # 執行所花時間
            print('總花費時間', time_c, 's')
            # 檢查是否達成成就
            if score == 'A':
                # 新增一筆紀錄
                rank_a = Achievement.objects.filter(face_score='A').get()
                UserAchievement.objects.create(user_id=user_id, achievement=rank_a)
            elif score == 'S':
                # 新增S跟A兩筆紀錄
                rank_s = Achievement.objects.filter(face_score='S').get()
                rank_a = Achievement.objects.filter(face_score='A').get()
                UserAchievement.objects.create(user_id=user_id, achievement=rank_s)
                UserAchievement.objects.create(user_id=user_id, achievement=rank_a)



            # 使用者目前的年級
            grade = list(SocialAccount.objects.filter(id=user_id).values('grade'))[0]['grade']
            # 計算特定使用者拿到的不同成就的累積次數
            user_have = UserAchievement.objects.filter(user=user_id).order_by('achievement_id') \
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
                UserGrade.objects.create(user_id=user_id, grade_id=grade)
                SocialAccount.objects.filter(id=user_id).update(grade=grade)

            # 找到在record內最新一筆資料 更新article進去
            record = Record.objects.latest("created")
            record.face = FaceModel.objects.latest("CreateDatetime")
            # 更新總分
            sound_rank = Sound.objects.latest("created").rank
            if sound_rank == 'S':
                sound_score = 100
            elif sound_rank == 'A':
                sound_score = 80
            elif sound_rank == 'B':
                sound_score = 60
            elif sound_rank == 'C':
                sound_score = 40
            elif sound_rank == 'D':
                sound_score = 20
            article_score = Article.objects.latest("created").total_score
            total_score = ori_score * 0.3 + sound_score * 0.3 + article_score * 0.4

            if 0 <= total_score <= 20:
                total_rank = 'D'
            elif 20 < total_score <= 40:
                total_rank = 'C'
            elif 40 < total_score <= 60:
                total_rank = 'B'
            elif 60 < total_score <= 80:
                total_rank = 'A'
            elif 80 < total_score:
                total_rank = 'S'

            # 檢查總分是否達成成就
            if total_rank == 'A':
                # 新增一筆紀錄
                rank_a = Achievement.objects.filter(total_score='A').get()
                UserAchievement.objects.create(user_id=user_id, achievement=rank_a)
            elif total_rank == 'S':
                # 新增S跟A兩筆紀錄
                rank_s = Achievement.objects.filter(total_score='S').get()
                rank_a = Achievement.objects.filter(total_score='A').get()
                UserAchievement.objects.create(user_id=user_id, achievement=rank_s)
                UserAchievement.objects.create(user_id=user_id, achievement=rank_a)

            record.total_score = total_rank
            record.save()
            face_query = FaceModel.objects.latest("CreateDatetime")
            result = model_to_dict(face_query)
            result['Videofile'] = face_query.Videofile.name
            result['Overall_Rank'] = total_rank

            return JsonResponse({'data': result})

        except Exception as e:
            data = {'error': str(e)}

        return JsonResponse({'data': data})

    def CaculateScore(self, eyebrow_height, eyebrow_pitch, mouth_height, mouth_pitch):
        # 眉毛擺動
        object = FaceModel.objects.order_by('AvgEyebrowHeight').values()
        length_data = len(object) - 2
        for i in range(0, length_data + 1):
            # print(object[i]['AvgEyebrowHeight'])
            if i < length_data:
                if float(eyebrow_height) < float(object[i]['AvgEyebrowHeight']):
                    eyebrow_height_PR = 0
                    break
                elif float(object[i]['AvgEyebrowHeight']) <= float(eyebrow_height) <= float(
                        object[i + 1]['AvgEyebrowHeight']):
                    eyebrow_height_PR = (i + 1) / (length_data + 2)
                    eyebrow_height_PR = eyebrow_height_PR * 100
                    break
            else:
                eyebrow_height_PR = 100
        # print(eyebrow_height_PR)

        # 皺眉程度
        if eyebrow_pitch < 0.9:
            eyebrow_pitch_PR = "過度"
        elif 0.9 < eyebrow_pitch < 1:
            eyebrow_pitch_PR = "適度"
        elif eyebrow_pitch > 1:
            eyebrow_pitch_PR = "放鬆"
        # print(eyebrow_pitch_PR)

        # 嘴尾
        object = FaceModel.objects.order_by('AvgMouthHeight').values()
        for i in range(0, length_data + 1):  # 4
            # print(object[i]['AvgMouthHeight'])
            if i < length_data:
                if float(mouth_height) <= float(object[i]['AvgMouthHeight']):
                    mouth_height_PR = 0
                    break
                elif float(object[i]['AvgMouthHeight']) <= float(mouth_height) <= float(
                        object[i + 1]['AvgMouthHeight']):
                    mouth_height_PR = (i + 1) / (length_data + 2)
                    mouth_height_PR = mouth_height_PR * 100
                    break
            else:
                mouth_height_PR = 100
        # print(mouth_height_PR)

        # 嘴開
        object = FaceModel.objects.order_by('AvgMouthPitch').values()

        for i in range(0, length_data + 1):
            # print(object[i]['AvgMouthPitch'])
            if i < length_data:
                if float(mouth_pitch) <= float(object[i]['AvgMouthPitch']):
                    mouth_pitch_pr = 0
                    break
                elif float(object[i]['AvgMouthPitch']) < float(mouth_pitch) < float(
                        object[i + 1]['AvgMouthPitch']):
                    mouth_pitch_pr = (i + 1) / (length_data + 2)
                    mouth_pitch_pr = mouth_pitch_pr * 100
                    break
            else:
                mouth_pitch_pr = 100
        # print(mouth_pitch_pr)

        mouth_pr = (mouth_pitch_pr + mouth_height_PR) / 2

        return eyebrow_height_PR, eyebrow_pitch_PR, mouth_pr


class FaceDataByIdView(ListAPIView):
    permission_classes = (AllowAny,)
    queryset = FaceModel.objects.all()
    serializer_class = FaceSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者特定時間的影片',
        operation_description='列出特定使用者的影片',
        # request_body=FaceGetSerializer
    )
    def get(self, request, *args, **krgs):
        file_id = self.kwargs['file_id']
        file = FaceModel.objects.filter(id=file_id).values()

        if file:
            file = file[0]
            # 讀取檔案
            try:
                open_file = open(file["Videofile"], 'rb')
                data = FileResponse(open_file)
                return data

            except IOError:
                # 檔案不存在
                data = {'error': 'file not found'}
                return JsonResponse(data)
        else:
            # index錯誤
            data = {'error': 'query out of index'}
            return JsonResponse(data)


class FaceQueryByUserLatest(ListAPIView):
    queryset = FaceModel.objects.all()
    serializer_class = FaceSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者最新的表情資訊',
        operation_description='列出特定使用者最新的表情資訊',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        queryset = FaceModel.objects.filter(user_id=user_id).latest("CreateDatetime")
        data = {
            'id': queryset.id,
            'VideofileName': queryset.VideofileName,
            'Videofile': queryset.Videofile.url,
            'AvgEyebrowHeight': queryset.AvgEyebrowHeight,
            'AvgEyebrowPitch': queryset.AvgEyebrowPitch,
            'AvgMouthHeight': queryset.AvgMouthHeight,
            'AvgMouthPitch': queryset.AvgMouthPitch,
            'EyebrowHeight_PR': queryset.EyebrowHeight_PR,
            'Mouth_PR': queryset.Mouth_PR,
            'EyebrowPitch_PR': queryset.EyebrowPitch_PR,
            'WinkTime': queryset.WinkTime,
            'DistractTime': queryset.DistractTime,
            'Total_Score': queryset.Total_Score,
            'user_id': queryset.user_id,
            'suggest': queryset.Suggest,
        }
        return JsonResponse({'data': data})
