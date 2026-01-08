from django.db import models
from django.conf import settings

# Create your models here.
class Student(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='student',null=True,blank=True
    )
    student_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    image = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.student_id} - {self.name}"
    

class Subject(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subject',null=True,blank=True
    )
    name=models.CharField(max_length=500,null=True,blank=True,unique=True)
    def __str__(self):
        return self.name
    
class PDFDocument(models.Model):
    subject = models.ForeignKey(
        Subject, 
        on_delete=models.CASCADE,
        related_name='pdfs',
        null=True, blank=True
    )
    module_name = models.CharField(max_length=255, null=True, blank=True)
    file = models.URLField(max_length=500, blank=True, null=True)  # use URL, not FileField
    uploaded_at = models.DateTimeField(auto_now_add=True)
    ppt_file = models.URLField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.module_name} ({self.subject})"


class Lastmodule(models.Model):
    pdf = models.ForeignKey(PDFDocument, on_delete=models.CASCADE, related_name='lastpdf', null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)  # auto-update timestamp

    def __str__(self):
        return f"Lastmodule → {self.pdf.module_name if self.pdf else 'None'}"