import json
from django.contrib.auth.models import User
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from drf_yasg import openapi
from rest_framework import mixins
from rest_framework.generics import GenericAPIView, ListAPIView
import requests as r
from login.serializers import LoginSerializer, UserGenderSerializer, CoachGenderSerializer
from login.models import SocialAccount
from drf_yasg.utils import swagger_auto_schema

response_schema_dict = {
    "200": openapi.Response(
        description="custom 200 description",
        examples={
            "application/json": {
                "id": "100611561679456185777",
                "email": "test@gmail.com",
                "verified_email": "true",
                "name": "test test",
                "given_name": "test",
                "family_name": "test",
                "picture": "https://lh3.googleusercontent.com/a-/AOh14Gi1hf5LKMi7kRIxh0zcWGBHnGSQ8NV2KfOwgERaHQ=s96-c",
                "locale": "zh-TW"
            }
        }
    ),
}


def handler404(request, exception):
    response = render(request, '404.html')
    response.status_code = 404
    return response


def handler500(request):
    response = render(request, '500.html')
    response.status_code = 500
    return response


class SocialUsersByIdView(ListAPIView):
    queryset = SocialAccount.objects.all()
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的登入資訊',
        operation_description='列出特定使用者的登入資訊',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        queryset = SocialAccount.objects.filter(id=user_id).values()
        return JsonResponse({'data': list(queryset)})


class UsersTotalWordQuery(ListAPIView):
    queryset = SocialAccount.objects.all()
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的累積字數',
        operation_description='列出特定使用者的累積字數',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        queryset = SocialAccount.objects.filter(id=user_id).values('total_word')
        return JsonResponse({'data': list(queryset)})


class SocialUsersView(GenericAPIView):
    queryset = SocialAccount.objects.all()
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        operation_summary='取得使用者列表',
        operation_description='列出所有的使用者',
        responses=response_schema_dict,
    )
    def get(self, request, *args, **krgs):
        users = self.get_queryset()
        serializer = self.serializer_class(users, many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    @swagger_auto_schema(
        operation_summary='使用者登入',
        operation_description='若使用者未登入過則新增新的使用者並回傳使用者資料，若登入過則回傳使用者資料',
        responses=response_schema_dict,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'access_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='token'
                )
            }
        )
    )
    def post(self, request, *args, **krgs):
        data = request.data
        token = data['access_token']
        google_api_url = 'https://www.googleapis.com/oauth2/v1/userinfo'
        my_params = {
            'access_token': token}
        response = r.get(google_api_url, params=my_params)
        response = response.json()
        # check user exist
        if not SocialAccount.objects.filter(unique_id=response['id']).exists():
            print("user not exist")
            user = User.objects.create_user(
                username=f"{response['name']}",  # Username has to be unique
                first_name=response['given_name'],
                last_name=response['family_name'],
                email=response['email']
            )
            SocialAccount.objects.create(
                unique_id=response['id'],
                user=user,
                email=response['email'],
                name=response['name'],  # Username has to be unique
                given_name=response['given_name'],
                family_name=response['family_name'],
                picture=response['picture'],
                locale=response['locale']
            )
            old_user = SocialAccount.objects.filter(unique_id=response['id']).values()
            return JsonResponse({'data': list(old_user)})

        else:
            old_user = SocialAccount.objects.filter(unique_id=response['id']).values()
            return JsonResponse({'data': list(old_user)})

        return JsonResponse(data)


class PatchAPIView(mixins.RetrieveModelMixin,
                   GenericAPIView):
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class UsersGender(PatchAPIView):
    queryset = SocialAccount.objects.all()
    serializer_class = UserGenderSerializer

    @swagger_auto_schema(
        operation_summary='更新使用者的性別',
        operation_description='更新使用者的性別',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='id'
                ),
                'gender': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='gender'
                )
            }
        )
    )
    def patch(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        user_gender = request.data['gender']
        user = SocialAccount.objects.filter(id=user_id)
        user.update(gender=user_gender)
        return JsonResponse({'data': list(user.values())})


class CoachGender(PatchAPIView):
    queryset = SocialAccount.objects.all()
    serializer_class = CoachGenderSerializer

    @swagger_auto_schema(
        operation_summary='更新教練的性別',
        operation_description='更新教練的性別',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='id'
                ),
                'coach_gender': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='gender'
                )
            }
        )
    )
    def patch(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        coach_gender = request.data['coach_gender']
        user = SocialAccount.objects.filter(id=user_id)
        user.update(coach_gender=coach_gender)
        return JsonResponse({'data': list(user.values())})


class userPretest(PatchAPIView):
    queryset = SocialAccount.objects.all()
    serializer_class = CoachGenderSerializer

    @swagger_auto_schema(
        operation_summary='更新前測與否紀錄',
        operation_description='更新前測與否紀錄',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'user_id': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='id'
                ),
                'initial': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='initial_pretest'
                )
            }
        )
    )
    def patch(self, request, *args, **kwargs):
        user_id = request.data['user_id']
        initial = request.data['initial']
        user = SocialAccount.objects.filter(id=user_id)
        user.update(initial=initial)
        return JsonResponse({'data': list(user.values())})
