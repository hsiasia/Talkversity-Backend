from target.models import Target
from target.serializers import TargetSerializer
from rest_framework import generics


# Create your views here.
class TargetList(generics.ListCreateAPIView):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer


class TargetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Target.objects.all()
    serializer_class = TargetSerializer
