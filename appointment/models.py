from django.db import models
from django.conf import settings

class Person(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='appointment',null=True,blank=True
    )
    name=models.CharField(max_length=300,null=True,blank=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    YES_NO_CHOICES = [
        (True, 'Yes'),
        (False, 'No'),
    ]

    name = models.CharField(max_length=255)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    phone_number = models.CharField(max_length=15)
    email = models.EmailField(null=True, blank=True)
    reason_for_visit = models.TextField()
    appointment = models.BooleanField(choices=YES_NO_CHOICES, default=True)
    person = models.ForeignKey(Person,on_delete=models.SET_NULL, null=True, blank=True, related_name="appointments")
    user = models.ForeignKey( settings.AUTH_USER_MODEL,on_delete=models.CASCADE,related_name="appointments",null=True,blank=True)

    def __str__(self):
        return self.name

