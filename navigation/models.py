from django.db import models

# Create your models here.
class Navigation(models.Model):
    name = models.CharField(max_length=100, null=True, blank=True)
    name1 = models.CharField(max_length=300, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    video = models.URLField(max_length=500, null=True, blank=True)  # Changed to URLField
    robot = models.CharField(max_length=10, null=True, blank=True)
    navigation_id = models.CharField(max_length=200, unique=True, null=True, blank=True)
    image = models.URLField(max_length=500, null=True, blank=True)  # Changed to URLField

    def __str__(self):
        return self.name
    

class FullTour(models.Model):
    robot = models.CharField(max_length=100,null=True,blank=True)  # or IntegerField if it's numeric
    navigations = models.JSONField(default=list)

    def __str__(self):
        return f"FullTour for Robot {self.robot}"
    

class DisplayVideo(models.Model):
    robot = models.CharField(max_length=10, null=True, blank=True)
    video = models.URLField(max_length=500, null=True, blank=True)

    def __str__(self):
        return f"{self.robot} - {self.video}"
    
