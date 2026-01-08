from django.db import models
from django.conf import settings

# Create your models here.
class Complaint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='complaints',null=True,blank=True
    )
    case_id = models.CharField(max_length=100, unique=True, blank=True)
    name = models.CharField(max_length=500, null=True, blank=True)
    age = models.PositiveIntegerField(null=True, blank=True)
    state = models.CharField(max_length=200, null=True, blank=True)
    district = models.CharField(max_length=200, null=True, blank=True)
    pincode = models.CharField(max_length=10, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    phone_no = models.CharField(max_length=15, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    complaint = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.case_id:
            last = Complaint.objects.order_by('-id').first()
            next_id = 1 if not last else last.id + 1
            self.case_id = f"{next_id:03d}"  # formats like 001, 002, ...
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Case {self.case_id} - {self.name}"


class Speak(models.Model):
    is_speaking = models.BooleanField(default=False)

    def __str__(self):
        return "Speaking" if self.is_speaking else "Silent"