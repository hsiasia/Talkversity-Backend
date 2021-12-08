import datetime

from django.forms import model_to_dict
from django.http import JsonResponse
from records.models import Record
from rest_framework import generics
from records.serializers import RecordSerializer, RecordPostSerializer
from drf_yasg.utils import swagger_auto_schema
from datetime import timedelta, datetime
from article.models import Article
from face.models import FaceModel
from sound.models import Sound


class RecordList(generics.ListCreateAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    @swagger_auto_schema(
        operation_summary='取得所有訓練紀錄',
        operation_description='列出所有訓練紀錄',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='新增訓練紀錄',
        operation_description='新增訓練紀錄',
        request_body=RecordPostSerializer
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RecordDetail(generics.RetrieveUpdateAPIView):
    queryset = Record.objects.all()
    serializer_class = RecordSerializer

    @swagger_auto_schema(
        operation_summary='取得特定訓練紀錄',
        operation_description='給id拿到特定的訓練紀錄',
    )
    def get(self, request, *args, **kwargs):
        record_id = self.kwargs['pk']
        q = Record.objects.get(id=record_id)
        result_list = {}
        face_video_url = 'http://140.115.81.245:8000/face/' + str(q.face_id) + '/'
        article = Article.objects.filter(id=q.article_id).values()
        sound = Sound.objects.filter(id=q.sound_id).values()
        face = FaceModel.objects.filter(id=q.face_id).values()
        result_list['total_score'] = q.total_score
        if not (list(face)):
            result_list['face'] = []
        else:
            list(face)[0]['Videofile'] = face_video_url
        result_list['article'] = list(article)
        result_list['sound'] = list(sound)
        result_list['face'] = list(face)
        return JsonResponse({'data': result_list})

    @swagger_auto_schema(
        operation_summary='更新特定訓練紀錄',
        operation_description='id為要修改的情境id，data為修改後的內容，可更改原本的目標id以及情境內容',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class RecordQueryByUser(generics.ListAPIView):
    serializer_class = RecordSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的所有訓練紀錄',
        operation_description='列出特定使用者的所有訓練紀錄',
    )
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        q = Record.objects.filter(user_id=user_id).values('id', 'created', 'scenario__content',
                                                          'sound__rank',
                                                          'face__Total_Score',
                                                          'article__rank',
                                                          'total_score')
        return JsonResponse({'data': list(q)})


class WeekRecordQueryByUser(generics.ListAPIView):
    serializer_class = RecordSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的一周的所有訓練紀錄',
        operation_description='列出特定使用者一周的所有訓練紀錄',
    )
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        q = Record.objects.filter(user_id=user_id, created__gte=start_date,
                                  created__lt=end_date).values('id', 'created', 'scenario__content',
                                                               'sound__rank',
                                                               'face__Total_Score',
                                                               'article__rank',
                                                               'total_score')
        return JsonResponse({'data': list(q)})


class SevenRecordQueryByUser(generics.ListAPIView):
    serializer_class = RecordSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的最後七筆訓練紀錄',
        operation_description='列出特定使用者的最後七筆訓練紀錄',
    )
    def get(self, request, *args, **kwargs):
        user_id = self.kwargs['user_id']
        q = Record.objects.filter(user_id=user_id).order_by('-id')[:7].values('id', 'created', 'scenario__content',
                                                                              'sound__rank',
                                                                              'face__Total_Score',
                                                                              'article__rank',
                                                                              'total_score')
        return JsonResponse({'data': list(q)})
