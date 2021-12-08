from rest_framework import serializers
from target.models import Target, Scenario


class ScenarioSerializer(serializers.ModelSerializer):

    class Meta:
        model = Scenario
        fields = '__all__'


class TargetSerializer(serializers.ModelSerializer):
    scenarios = ScenarioSerializer(many=True)

    class Meta:
        model = Target
        fields = '__all__'
