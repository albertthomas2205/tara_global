from django.db import models
from django.conf import settings
# Create your models here.

class Patient(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patients',null=True,blank=True
    )
    patient_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    registration_date = models.DateField(auto_now_add=True)  
    status=models.BooleanField(default=True,null=True,blank=True)
    pdf = models.URLField(
        max_length=2000,  # Azure URLs can be long, so increase limit
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.name} ({self.patient_id})"
    

class Room(models.Model):
    room_number = models.CharField(max_length=100)  # Removed unique=True
    is_available = models.BooleanField(default=True)
    robot = models.CharField(null=True, blank=True, max_length=200)

    class Meta:
        unique_together = ('room_number', 'robot') 

    def __str__(self):
        return self.room_number
    

class PatientRoomAssignment(models.Model):
    patient = models.OneToOneField(
        Patient,
        on_delete=models.CASCADE,
        related_name='room_assignment'
    )
    room = models.OneToOneField(
        Room,
        on_delete=models.CASCADE,
        related_name='patient_assignment'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    pdf = models.FileField(upload_to='assignment_pdfs/',null=True,blank=True)
    text = models.TextField(null=True,blank=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient',null=True,blank=True
    )

    def __str__(self):
        return f"{self.patient.name} assigned to Room {self.room.room_number}"

