from rest_framework import serializers
from .models import LeetCodeProblem

class LeetCodeProblemSerializer(serializers.ModelSerializer):
    class Meta:
        model = LeetCodeProblem
        fields = '__all__'
