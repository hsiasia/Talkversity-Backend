from target.models import Scenario
from target.serializers import ScenarioSerializer
from rest_framework import generics
from drf_yasg.utils import swagger_auto_schema


# Create your views here.
class ScenarioList(generics.ListCreateAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    @swagger_auto_schema(
        operation_summary='取得所有情境',
        operation_description='列出所有情境',
    )
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='新增情境',
        operation_description='新增情境，需要給目標(target id)，content則是情境內容',
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ScenarioDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Scenario.objects.all()
    serializer_class = ScenarioSerializer

    @swagger_auto_schema(
        operation_summary='取得特定情境',
        operation_description='給id拿到特定的情境',
    )
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary='更新特定情境',
        operation_description='id為要修改的情境id，data為修改後的內容，可更改原本的目標id以及情境內容',
    )
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
