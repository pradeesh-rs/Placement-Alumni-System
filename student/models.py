from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class StudentDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,null=True,blank=True)
    email = models.EmailField(unique=True,null=True,blank=True)
    phone = models.CharField(max_length=100,unique=True,null=True,blank=True)
    address = models.CharField(max_length=100,null=True,blank=True)
    date_of_birth = models.DateField(null=True,blank=True)
    gender = models.CharField(max_length=100,null=True,blank=True)
    blood_group = models.CharField(max_length=100,null=True,blank=True)
    profile_picture = models.ImageField(upload_to="StudentProfilePicture",null=True,blank= True)
    course = models.CharField(max_length=100,null=True,blank=True)
    branch = models.CharField(max_length=100,null=True,blank=True)
    is_passed_out = models.BooleanField(null=True,blank=True)
    year = models.CharField(max_length=100,null=True,blank=True)
    sem = models.CharField(max_length=100,null=True,blank=True)
    roll_no = models.CharField(max_length=100,null=True,blank=True)
    reg_no = models.CharField(max_length=100,unique=True,null=True,blank=True)
    cgpa = models.FloatField(null=True,blank=True)
    resume = models.FileField(upload_to="StudentResume", default=None,null=True,blank=True)
    is_resume_approved = models.BooleanField(null=True,blank=True)
    


class JobInfo(models.Model):
    student = models.ForeignKey(StudentDetails,on_delete=models.CASCADE,related_name="job_info")
    job_title = models.CharField(max_length=100,null=True,blank=True)
    company_name = models.CharField(max_length=100,null=True,blank=True)
    company_location = models.CharField(max_length=100,null=True,blank=True)
    salary = models.FloatField(null=True,blank=True)
    date = models.DateField(auto_now_add=True)

class SemesterGrade(models.Model):
    student = models.ForeignKey(StudentDetails, on_delete=models.CASCADE, related_name="semester_grades")
    semester_name = models.CharField(max_length=100) # e.g. "CT - Semester 1"
    sgpa = models.FloatField()
    total_credits = models.FloatField()
    date_added = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'semester_name')
