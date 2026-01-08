from rest_framework import serializers
from .models import Complaint,Speak

class ComplaintSerializer(serializers.ModelSerializer):
    class Meta:
        model = Complaint
        fields = '__all__'
        read_only_fields = ['case_id', 'created_at']


class SpeakSerializer(serializers.ModelSerializer):
    class Meta:
        model = Speak
        fields = ['id', 'is_speaking']
