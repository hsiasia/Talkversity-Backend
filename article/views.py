from django.forms.models import model_to_dict
from rest_framework.parsers import MultiPartParser
from django.db.models import F, Count
from article.text_emotion import *
from rest_framework.generics import GenericAPIView, RetrieveAPIView, ListAPIView
from article.models import Article, ArticleDetail
from login.models import SocialAccount
from achievements.models import Achievement, UserAchievement, GradeAchievement, UserGrade
from records.models import Record
from article.serializers import ArticleSerializer, ArticlePostSerializer, ArticleDetailSerializer
from drf_yasg.utils import swagger_auto_schema
from django.http import JsonResponse


# 新增文字記錄
class ArticleList(GenericAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_summary='取得文章列表',
        operation_description='列出所有的文章',
    )
    def get(self, request, *args):
        article = self.get_queryset()
        serializer = self.serializer_class(article, many=True)
        data = serializer.data
        return JsonResponse(data, safe=False)

    @swagger_auto_schema(
        operation_description='新增整篇文章的分析結果',
        operation_summary='新增文章分析結果',
        request_body=ArticlePostSerializer
    )
    def post(self, request, *args, **kwargs):

        try:
            user_id = request.POST['user_id']
            video_file = request.FILES['video_file']
            user = SocialAccount.objects.filter(id=user_id).get()
            video_file_path = video_file.temporary_file_path()
            audio_file_path = video2audio(video_file_path)
            frame_rate, channels = frame_rate_channel(audio_file_path)
            response = transcribe_file(audio_file_path, frame_rate, channels)
            article = Article.objects.create(
                user=user,
                fulltext=response['全文'],
                text_len=response['文章長度'],
                pure_text_len=response['文章長度(不含標點符號)'],
                redundant_1_count=response['就是次數'],
                redundant_2_count=response['那個次數'],
                redundant_3_count=response['然後次數'],
                redundant_4_count=response['所以次數'],
                joy_score=response['joy'],
                trust_score=response['trust'],
                surprise_score=response['surprise'],
                anticipation_score=response['anticipation'],
                fear_score=response['fear'],
                sadness_score=response['sadness'],
                anger_score=response['anger'],
                disgust_score=response['disgust'],
                total_score=response['total_score'],
                rank=response['rank'],
                talk_speed=response['talk_speed'],
                suggest=response['suggest_json'],
                suggest_json=response['suggest_json']
            )

            # 文章長度
            pure_text_len = response['文章長度(不含標點符號)']
            # 用來存放每句的s2
            article_list = []
            for line in response['detail']:
                article_line = ArticleDetail(article=article, sentence=line, sentiment=response['detail'][line])
                article_list.append(article_line)
            # 新增句意分析的資料
            ArticleDetail.objects.bulk_create(article_list)
            # 新增累積字數
            SocialAccount.objects.filter(id=user_id).update(
                total_word=F('total_word') + pure_text_len)
            # 拿到累積字數
            user_total_word = SocialAccount.objects.filter(id=user_id).values('total_word')[0][
                'total_word']
            # 拿到當次的article成績
            article_rank = response['rank']
            # 檢查是否達成成就
            if article_rank == 'A':
                # 新增一筆紀錄
                rank_a = Achievement.objects.filter(article_score='A').get()
                UserAchievement.objects.create(user=user, achievement=rank_a)
            elif article_rank == 'S':
                # 新增S跟A兩筆紀錄
                rank_s = Achievement.objects.filter(article_score='S').get()
                rank_a = Achievement.objects.filter(article_score='A').get()
                UserAchievement.objects.create(user=user, achievement=rank_s)
                UserAchievement.objects.create(user=user, achievement=rank_a)

            # 達成字數成就
            a = Achievement.objects.filter(total_word__lte=user_total_word).last()
            if a:
                UserAchievement.objects.create(achievement=a, user=user)
            else:
                print('word not exceed!')
            # 使用者目前的年級
            grade = list(SocialAccount.objects.filter(id=user).values('grade'))[0]['grade']
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

            # 找到在record內最新一筆資料 更新article進去
            record = Record.objects.latest("created")
            record.article = article
            record.save()
            print('success')

            return JsonResponse({'data': response})

        except Exception as e:
            response = {'error': str(e)}
        return JsonResponse(response)


class ArticleQueryByUser(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者的文章資訊',
        operation_description='列出特定使用者的文章資訊',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        queryset = Article.objects.filter(user_id=user_id).values()
        return JsonResponse({'data': list(queryset)})


class ArticleQueryByUserLatest(ListAPIView):
    queryset = Article.objects.all()
    serializer_class = ArticleSerializer

    @swagger_auto_schema(
        operation_summary='取得特定使用者最新的文章資訊',
        operation_description='列出特定使用者最新的文章資訊',
    )
    def get(self, request, *args, **krgs):
        user_id = self.kwargs['user_id']
        queryset = Article.objects.filter(user_id=user_id).latest("created")
        return JsonResponse({'data': model_to_dict(queryset)})


class ArticleDetailList(ListAPIView):
    queryset = ArticleDetail.objects.all()
    serializer_class = ArticleDetailSerializer

    @swagger_auto_schema(
        operation_summary='取得所有句意分析',
        operation_description='列出所有句意分析',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class ArticleDetailQuery(RetrieveAPIView):
    queryset = ArticleDetail.objects.all()
    serializer_class = ArticleDetailSerializer

    @swagger_auto_schema(
        operation_summary='取得特定文章的句意分析',
        operation_description='列出特定文章的句意分析',
    )
    def get(self, request, *args, **krgs):
        article_id = self.kwargs['article_id']
        queryset = ArticleDetail.objects.filter(article_id=article_id).values()
        return JsonResponse({'data': list(queryset)})
