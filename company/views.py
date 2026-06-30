from django.shortcuts import render,redirect
from app.models import UserPermission
from .models import CompanyDetails,JobDetails,JobApplication
from django.contrib import messages
from student.models import StudentDetails
from app.models import DegreeSpecialization
import json
from app.models import Notification
# Create your views here.
def dashboard(request):
    total_applicants = JobApplication.objects.count()
    context = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "total_applicants" : total_applicants,
        "total_jobs" : JobDetails.objects.count(),
        "company": CompanyDetails.objects.get(user= request.user),
        "recent_applicants" : JobApplication.objects.order_by("-id")[:5],
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"company/dashboard.html",context)

def profile(request):
    if request.method == "POST":
        try:
            img = request.FILES.get("profile_picture")
        except:
            img = None
        c_name= request.POST.get("name")
        industry_type = request.POST.get("industry_type")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        location = request.POST.get("location")
        is_edit =  request.POST.get("hide")
        
        print(img)
        print(is_edit)
        if is_edit is None:

            CompanyDetails(user=request.user,name=c_name,email= email,phone=phone,location=location,industry_type=industry_type,profile_picture=img).save()
            messages.success(request,"Profile updated successfully")
            return redirect("company:profile")
        else:
            company = CompanyDetails.objects.get(user=request.user)
            company.name = c_name
            company.email = email
            company.phone = phone
            company.location = location
            company.industry_type = industry_type
            if img is not None:
                company.profile_picture = img
            company.save()
            messages.success(request,"Profile updated successfully")
            return redirect("company:profile")


    context = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "company" : CompanyDetails.objects.filter(user=request.user).first(),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"company/Profile.html",context)

def jobs(request):
    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        salary = request.POST.get("salary")
        location = request.POST.get("location")
        industry_type = request.POST.get("industry_type")
        cgpa_threshold = request.POST.get("cgpa_threshold")
        job_type = request.POST.get("job_type")
        job_mode = request.POST.get("job_mode")
        is_edit =  request.POST.get("hide")

        
        company = CompanyDetails.objects.get(user=request.user)
        print(title,description,salary,location,industry_type,cgpa_threshold,job_type,job_mode)
        if is_edit == "edit":
            job = JobDetails.objects.get(id=request.POST.get("job_id"))
            job.title = title
            job.description = description
            job.salary = salary
            job.location = location
            job.industry_type = industry_type
            job.cgpa_threshold = cgpa_threshold
            job.job_type = job_type
            job.job_mode = job_mode
            job.save()
            messages.success(request,"Job updated successfully")
            return redirect("company:jobs")
        else:
            JobDetails(company=company,title=title,description=description,salary=salary,location=location,industry_type=industry_type,cgpa_threshold=cgpa_threshold,job_type=job_type,job_mode=job_mode).save()
            messages.success(request,"Job added successfully")
            return redirect("company:jobs")
    
    context = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "jobs" : JobDetails.objects.filter(company__user=request.user),
        "students" : StudentDetails.objects.all(),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()

    }
    return render(request,"company/jobs.html",context)

def deletejob(request,id):
    print("delte")
    job = JobDetails.objects.get(id=id)
    job.delete()
    messages.success(request,"Job deleted successfully")
    return redirect("company:jobs")


def eligible_students(request,id):
    job = JobDetails.objects.get(id=id)
    degree = {}
    for i in DegreeSpecialization.objects.values("degree").distinct():
        specialization = []
        for j in DegreeSpecialization.objects.filter(degree=i["degree"]):
            specialization.append(j.specialization)
        degree[i["degree"]] = specialization
    context = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "job" : job,
        "students" : StudentDetails.objects.filter(cgpa__gte=job.cgpa_threshold),
        "degrees":json.dumps(degree),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"company/eligible_students.html",context)


def applied_students(request,id):
    job = JobDetails.objects.get(id=id)
    degree = {}
    for i in DegreeSpecialization.objects.values("degree").distinct():
        specialization = []
        for j in DegreeSpecialization.objects.filter(degree=i["degree"]):
            specialization.append(j.specialization)
        degree[i["degree"]] = specialization
    print(JobApplication.objects.filter(job=job).values("user"))
    context = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "job" : job,
        "students" : StudentDetails.objects.filter(
                    id__in=JobApplication.objects.filter(job=job).values("user")
                ),
        "degrees":json.dumps(degree),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"company/appliedstudents.html",context)


