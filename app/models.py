from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from student.models import StudentDetails
from teacher.models import TeacherDetails

# Create your models here.

class UserPermission(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="user_permission")
    is_teacher = models.BooleanField(default=False)
    is_company = models.BooleanField(default=False)
    is_student = models.BooleanField(default=False)
    is_principal = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)

   

class DegreeSpecialization(models.Model):
    user = models.ForeignKey(User,on_delete=models.SET_NULL,null=True,blank=True)
    degree = models.CharField(max_length=100)
    specialization = models.CharField(max_length=100)

class Principal(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    profile_picture = models.ImageField(upload_to="principalProfilePicture",null=True,blank= True)    


class Notification(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,related_name="notifications")
    teacher = models.ForeignKey(TeacherDetails, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    admin = models.ForeignKey(Principal, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    message = models.CharField(max_length=100)
    is_read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)