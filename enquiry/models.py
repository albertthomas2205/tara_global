from django.db import models
from accounts.models import *




class Enquiry(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'user'})
    logo = models.ImageField(upload_to='enquiry_logos/', null=True, blank=True)
    heading = models.CharField(max_length=255)

    def __str__(self):
        return self.heading
class SubButton(models.Model):
    enquiry = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='subbuttons')
    subheading = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.enquiry.heading} - {self.subheading}"

class EnquiryDetails(models.Model):
    subheading = models.ForeignKey(SubButton, on_delete=models.CASCADE, related_name='details')
    heading = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to="enquiry_images/", null=True, blank=True)
    other_headings = models.CharField(max_length=255, null=True, blank=True)  # Example additional field

    def __str__(self):
        return self.heading
    
class Youtube(models.Model):
    title = models.CharField(max_length=500, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    link = models.URLField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title or "Untitled Video"


















