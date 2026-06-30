from django.shortcuts import render,redirect,get_object_or_404
from app.models import UserPermission
from .models import StudentDetails,JobInfo
from django.contrib.auth.models import User
from django.contrib import messages
from company.models import JobDetails,JobApplication
from app.models import DegreeSpecialization,Notification
import json
from django.http import HttpResponse
from django_htmx.http import trigger_client_event
from teacher.models import Training
from .cgpa import calculate_cgpa
from .models import SemesterGrade
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt



# Create your views here.
def dashboard(request):
    if request.method == 'POST':
        job_id = request.POST.get("job_id")
        cover_letter = request.POST.get("cover_letter")
        availability = request.POST.get('availability')
        cgpa_required = request.POST.get('cgpa_met') == 'yes'
        confirm_info = request.POST.get('confirm_info') == 'on'
        job = JobDetails.objects.get(id=job_id)
        student = StudentDetails.objects.get(user= request.user)
        if JobApplication.objects.filter(job=job,user=student).exists():
            messages.error(request,"You have already applied for this job")
            return redirect("student:student")
        
        JobApplication(job=job,user=student,cover_letter=cover_letter,available_to_work_in=availability,cgpa_required=cgpa_required,confirm_info=confirm_info).save()
        messages.success(request,"Your Application has been submitted")
        return redirect("student:student")
        
    student = StudentDetails.objects.get(user= request.user)
    try:
        jobs = JobDetails.objects.filter(
            cgpa_threshold__lte=student.cgpa,
            is_active=True
        ).exclude(
            applications__user=student
        )
        locations =JobDetails.objects.filter(
            cgpa_threshold__lte=student.cgpa,
            is_active=True
        ).exclude(
            applications__user=student
        ).values_list("location",flat=True).distinct()
    except:
        
        jobs = None
        locations = None
        
    print(locations)
    print(jobs)
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "jobs" : jobs,
        "student" : student,
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count(),
        "location": locations

    }
    return render(request,"student/dashboard.html",content)

def profile(request):
    if request.method == 'POST':
        try:
            img = request.FILES.get("profile_picture")
        except:
            img = None
        name = request.POST.get("name")
        email = request.POST.get("email")
        ph_no = request.POST.get("phone")
        dob = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        blood_group = request.POST.get("blood_group")
        address =  request.POST.get("address")
        course = request.POST.get("course")
        branch = request.POST.get("branch")
        year = request.POST.get("year")
        semester = request.POST.get("sem")
        is_passed_out = request.POST.get("is_passed_out") == "on"
        roll_no = request.POST.get('roll_no')
        reg_no =  request.POST.get("reg_no")
        cgpa = request.POST.get("cgpa")
        is_edit = request.POST.get('hide')
        resume = None if request.FILES.get("resume") == "" else request.FILES.get("resume")
        job_title = request.POST.get("job_title")
        company_name = request.POST.get("company_name")
        company_location = request.POST.get("company_location")
        mark_sheet = request.FILES.get("marksheet")
        salary = 0 if request.POST.get("salary") == "" else request.POST.get("salary")
        user = User.objects.get(username=request.user)
        if mark_sheet:
            cgpa = calculate_cgpa(request.FILES.get("marksheet"))
        if is_edit is None:
            StudentDetails(user=user,name=name,email=email,phone=ph_no,address=address,date_of_birth=dob,gender=gender,blood_group=blood_group,profile_picture=img,course=course,branch=branch,year=year,sem= semester,roll_no=roll_no,reg_no=reg_no,cgpa=cgpa,resume=resume,job_title=job_title,company_name=company_name, is_passed_out= is_passed_out,company_location=company_location,salary=salary).save()
            messages.success(request,"Your Profile has been added")
            return redirect("student:profile")
        else:
            student = StudentDetails.objects.get(user=user)
            student.name = name
            student.email = email
            student.phone = ph_no
            student.address = address
            student.date_of_birth = dob
            student.blood_group = blood_group
            
            student.gender = gender
            if not is_passed_out:
                student.course = course
                student.branch = branch
                student.year = year
                student.sem = semester
                student.roll_no = roll_no
                student.reg_no = reg_no
            student.is_passed_out = is_passed_out
            if resume:
                if student.resume:
                    student.resume.delete()
                student.resume = resume
                student.is_resume_approved = False
            if cgpa:
                student.cgpa = cgpa
            
            
            if JobInfo.objects.filter(student=student).exists():
                job = JobInfo.objects.get(student=student)
                job.job_title = job_title
                job.company_name = company_name
                job.company_location = company_location
                job.salary = salary
                job.save()
            elif job_title and company_name and company_location and salary :
                JobInfo(student=student,job_title=job_title,company_name=company_name,company_location=company_location,salary=salary).save()
            if img:
                if student.profile_picture:
                    student.profile_picture.delete()
                student.profile_picture = img
            if student.is_resume_approved == None:
                student.is_resume_approved = False
            student.save()
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    semesters = [str(i) for i in range(1, 7)]
    years = ['1', '2', '3']
    degree = {}
    for i in DegreeSpecialization.objects.values("degree").distinct():
        specialization = []
        for j in DegreeSpecialization.objects.filter(degree=i["degree"]):
            specialization.append(j.specialization)
        degree[i["degree"]] = specialization
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "student":StudentDetails.objects.filter(user=request.user).first(),
        'blood_groups': blood_groups,
        'semesters': semesters,
        'years': years,
        'degrees': json.dumps(degree),
        "degrees_list":degree,
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"student/profile.html",content)


def training(request):
    content = {
        "user_data" : UserPermission.objects.get(user=request.user),
        "student" : StudentDetails.objects.filter(user=request.user).first(),
        "trainings" : Training.objects.all(),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"student/training.html",content)


def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)

    notif.is_read = True
    notif.save()

    # Determine sender name in PYTHON (not template)
    if hasattr(notif, "teacher") and notif.teacher:
        sender = notif.teacher.user.username
    elif hasattr(notif, "admin") and notif.admin:
        sender = notif.admin.user.username
    else:
        sender = "System Message"

    response = HttpResponse(
        f"""
        <a class="dropdown-item d-flex py-3 border-bottom notification-item
           notification-read notification-fade"
           style="white-space: normal;"
           data-id="{notif.id}">
          <div class="w-100">
            <p class="mb-0 notification-text text-muted">
              <span class="notification-user">{sender}:</span>
              <span class="notification-message">{notif.message}</span>
            </p>
          </div>
        </a>
        """
    )

    return trigger_client_event(
        response,
        "notificationRead",
        {"id": pk}
    )

def mark_notification_read_modal(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)

    notif.is_read = True
    notif.save()

    # Determine sender name in PYTHON (not template)
    if hasattr(notif, "teacher") and notif.teacher:
        sender = notif.teacher.user.username
    elif hasattr(notif, "admin") and notif.admin:
        sender = notif.admin.user.username
    else:
        sender = "System Message"

    from django.utils.timesince import timesince
    time_ago = timesince(notif.date)
    avatar_initial = notif.user.username[0].upper() if notif.user.username else "S"

    response = HttpResponse(
        f"""
        <div id="notif-modal-{notif.id}" 
             class="notification-modal-item notification-read modal-notification-read"
             style="opacity: 0.75;">
          <div class="notification-content">
            <div class="notification-avatar">
              {avatar_initial}
            </div>
            <div class="notification-body">
              <p class="notification-text mb-1">
                <span class="notification-user">{sender}:</span>
                <span class="notification-message">{notif.message}</span>
              </p>
              <span class="notification-meta">{time_ago} ago</span>
            </div>
          </div>
        </div>
        """
    )

    return trigger_client_event(
        response,
        "notificationRead",
        {{"id": pk}}
    )

def cgpa_calculator(request):
    # student = get_object_or_404(StudentDetails, user=request.user)
    student =StudentDetails.objects.filter(user=request.user).first()
    if request.method == "POST":
        data = json.loads(request.body)
        semester_name = data.get("semester_name")
        sgpa = data.get("sgpa")
        total_credits = data.get("total_credits")
        
        # Save or update semester grade
        SemesterGrade.objects.update_or_create(
            student=student,
            semester_name=semester_name,
            defaults={"sgpa": sgpa, "total_credits": total_credits}
        )
        
        # Recalculate and update main student CGPA
        all_grades = SemesterGrade.objects.filter(student=student)
        total_weighted_points = sum(sg.sgpa * sg.total_credits for sg in all_grades)
        total_credits_sum = sum(sg.total_credits for sg in all_grades)
        
        if total_credits_sum > 0:
            student.cgpa = round(total_weighted_points / total_credits_sum, 3)
            student.save()
            
        return HttpResponse(json.dumps({"status": "success", "cgpa": student.cgpa}), content_type="application/json")

    saved_results = SemesterGrade.objects.filter(student=student)
    content = {
        "user_data": UserPermission.objects.get(user=request.user),
        "student": student,
        "saved_results": saved_results,
        "notifications": Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count": Notification.objects.filter(user=request.user, is_read=False).count()
    }
    return render(request, "student/cgpa_calculater.html", content)


def delete_semester_grade(request, pk):
    grade = get_object_or_404(SemesterGrade, pk=pk, student__user=request.user)
    student = grade.student
    grade.delete()
    
    # Recalculate main student CGPA
    all_grades = SemesterGrade.objects.filter(student=student)
    if all_grades.exists():
        total_weighted_points = sum(sg.sgpa * sg.total_credits for sg in all_grades)
        total_credits_sum = sum(sg.total_credits for sg in all_grades)
        student.cgpa = round(total_weighted_points / total_credits_sum, 3)
    else:
        student.cgpa = 0.0
    student.save()
    
    messages.success(request, "Semester record deleted.")
    return redirect("student:cgpa_calculator")

def delete_all_cgpa_records(request):
    grade = SemesterGrade.objects.filter(student=StudentDetails.objects.get(user=request.user))
    student = StudentDetails.objects.get(user=request.user)
    student.cgpa = 0.0
    student.save()
    grade.delete()
    return redirect("student:cgpa_calculator")
    