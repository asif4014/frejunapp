from rest_framework import serializers
from . models import Candidate


class DataSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = '__all__'
