from django.db import models
from django.contrib.auth.models import User
from student.models import StudentDetails
# Create your models here.

class CompanyDetails(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    name = models.CharField(max_length=100,blank=True,null=True)
    email = models.EmailField(unique=True,blank=True,null=True)
    phone = models.CharField(max_length=100,unique=True,blank=True,null=True)
    location = models.CharField(max_length=100,blank=True,null=True)
    industry_type = models.CharField(max_length=100,blank=True,null=True)
    profile_picture = models.ImageField(upload_to="CompanyProfilePicture",null=True,blank= True)

   


class JobDetails(models.Model):
    company = models.ForeignKey(CompanyDetails,on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    salary = models.FloatField()
    location = models.CharField(max_length=100)
    industry_type = models.CharField(max_length=100)
    cgpa_threshold = models.FloatField(null=True,blank=True)
    job_type = models.CharField(max_length=100)
    job_mode = models.CharField(max_length=100)
    date_posted = models.DateField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    

class JobApplication(models.Model):
    job = models.ForeignKey(JobDetails, on_delete=models.CASCADE, related_name="applications")
    user = models.ForeignKey(StudentDetails, on_delete=models.CASCADE, related_name="job_applications")
    cover_letter = models.TextField(blank=True,null=True)
    available_to_work_in = models.CharField(max_length=100)
    cgpa_required = models.FloatField(null=True,blank=True)
    date_applied = models.DateField(auto_now_add=True)
    confirm_info = models.BooleanField(default=True)
