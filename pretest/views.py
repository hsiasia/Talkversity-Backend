# from rest_framework import viewsets
# from rest_framework import status 
# from rest_framework.response import Response
# from django.db import transaction
from django.forms import model_to_dict
from rest_framework.parsers import MultiPartParser
from rest_framework.generics import GenericAPIView, RetrieveAPIView, ListAPIView
from django.http import HttpResponse, JsonResponse
from drf_yasg.utils import swagger_auto_schema
from django.core import serializers

from .gaze_tracking import Tools
from pretest.serializers import PretestSerializer, PrestestPostSerializer
from pretest.models import PretestModel
from login.models import SocialAccount


class PretestView(GenericAPIView):
    queryset = PretestModel.objects.all()
    serializer_class = PretestSerializer
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description='新增前測影片',
        operation_summary='新增前測臉部數據',
        request_body=PrestestPostSerializer
    )
    def post(self, request, *args, **krgs):
        data = request.data
        try:
            serializer = PrestestPostSerializer(data=data)
            serializer.is_valid(raise_exception=True)

            userid = data.__getitem__('user')
            gender = SocialAccount.objects.get(id=userid).gender


            # 檔案暫存
            serializer.save()

            pretestvideo_Pre = PretestModel.objects.filter(user_id=userid).latest("created")
            pretestvideo_Pre = model_to_dict(pretestvideo_Pre)
            Path = pretestvideo_Pre['Videofile']

            PathSplit = str(Path).split('/')
            fileName = PathSplit[1]
            print("VideofileName:", fileName)

            # 背景偵測與回傳值
            ToolsModel = Tools(fileName)
            eyebrow_height, eyebrow_pitch, mouth_height, mouth_pitch, eyes_pitch = ToolsModel.doAll()
            avg, freq = ToolsModel.presound(gender)
            # 列印回傳值
            # print(eyebrow_height, eyebrow_pitch, mouth_height, mouth_pitch, eyes_pitch)

            # 更新回傳值數據
            filePath = './media/prevideo/' + str(fileName)

            pretestvideo = PretestModel.objects.filter(Videofile=Path).first()
            pretestvideo.Videofile = filePath
            pretestvideo.PreEyebrowHeight = eyebrow_height
            pretestvideo.PreEyebrowPitch = eyebrow_pitch
            pretestvideo.PreMouthHeight = mouth_height
            pretestvideo.PreMouthPitch = mouth_pitch
            pretestvideo.PreEyesPitch = eyes_pitch
            pretestvideo.PreSoundAvg = avg
            pretestvideo.PreSoundFreq = freq
            pretestvideo.save()
            user = SocialAccount.objects.filter(id=userid)
            user.update(initial=1)
            result = model_to_dict(pretestvideo)
            result['Videofile'] = pretestvideo.Videofile.name


            return JsonResponse({'data': result})

        except Exception as e:
            data = {'error': str(e)}
        return JsonResponse({'data': data})

        # return HttpResponse(data, content_type='application/json')

    @swagger_auto_schema(
        operation_summary='取得所有已完成前側的使用者資料',
        operation_description='列出所有已完成前側的使用者資料',
    )
    def get(self, request, *args):
        pretest = self.get_queryset()
        serializer = self.serializer_class(pretest, many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)
