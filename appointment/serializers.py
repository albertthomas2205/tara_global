from rest_framework import serializers
from .models import Person,Appointment

class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ['id', 'name']


class AppointmentSerializer(serializers.ModelSerializer):
    gender_display = serializers.CharField(source='get_gender_display', read_only=True)
    appointment_display = serializers.CharField(source='get_appointment_display', read_only=True)
    person_name = serializers.CharField(source='person.name', read_only=True)

    class Meta:
        model = Appointment
        fields = [ 'id','name','age','gender','gender_display','phone_number','email','reason_for_visit','appointment','appointment_display','person_name', 'person','user']
        read_only_fields = ['user'] 