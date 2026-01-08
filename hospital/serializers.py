from rest_framework import serializers
from .models import *


class PatientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Patient
        fields = ['id', 'patient_id', 'name', 'registration_date', 'user','status','pdf']
        read_only_fields = ['registration_date', 'user']


class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Room
        fields = '__all__'




class PatientRoomAssignmentSerializer(serializers.ModelSerializer):
    # Nested serializers for full details
    patient = PatientSerializer(read_only=True)
    room = RoomSerializer(read_only=True)

    # Still keep computed fields
    patient_name = serializers.CharField(source='patient.name', read_only=True)
    room_number = serializers.CharField(source='room.room_number', read_only=True)
    pdf = serializers.SerializerMethodField()

    class Meta:
        model = PatientRoomAssignment
        fields = [
            'id', 'patient', 'room', 'assigned_at',
            'patient_name', 'room_number',
            'pdf', 'text'
        ]
        read_only_fields = ['assigned_at']

    def get_pdf(self, obj):
        """Return the Patient's Azure Blob PDF URL"""
        if obj.patient and obj.patient.pdf:
            return obj.patient.pdf
        return None

    def validate(self, data):
        if self.instance is None:
            patient = data.get('patient')
            room = data.get('room')

            if PatientRoomAssignment.objects.filter(patient=patient).exists():
                raise serializers.ValidationError(
                    {"patient": "This patient is already assigned to a room."}
                )

            if PatientRoomAssignment.objects.filter(room=room).exists():
                raise serializers.ValidationError(
                    {"room": "This room is already occupied by another patient."}
                )

            if room and not room.is_available:
                raise serializers.ValidationError(
                    {"room": "This room is not available."}
                )
        return data


    

class AssignmentTextUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientRoomAssignment
        fields = ['text']
