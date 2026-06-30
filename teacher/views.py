from django.shortcuts import render,redirect
from django.contrib import messages
from app.models import Principal, UserPermission,Notification,DegreeSpecialization
from .models import TeacherDetails, Training
from student.models import StudentDetails,JobInfo
from django.db.models import Count
from django.db.models.functions import ExtractYear
from company.models import CompanyDetails
import json
from django.contrib.auth.models import User

def add_notifications(request):
    user = request.user
    teacher = TeacherDetails.objects.get(user=request.user)

    # Check for pending approvals
    re_student = StudentDetails.objects.filter(user__user_permission__is_approved=False,user__user_permission__is_student=True,branch=teacher.specialization,course=teacher.department)
    res_student = StudentDetails.objects.filter(branch=teacher.specialization,course=teacher.department,user__user_permission__is_approved=True,user__user_permission__is_student=True,is_resume_approved=False).exclude(resume="")
    print(res_student)
    active_notifications = []
    msg = f"There are {re_student.count()} student accounts awaiting approval."
    if Notification.objects.filter(user=user,message__icontains=msg).exists():
        notifications = Notification.objects.filter(user=user).order_by("-date")
        return notifications
    if res_student.exists():
        msg = f"There are {res_student.count()} student accounts with resume."
        Notification.objects.update_or_create(
            user=user,
            message=msg,
            defaults={"is_read": False}
        )
        active_notifications.append(msg)

    # Remove outdated approval notifications (for company/teacher/student)
    Notification.objects.filter(
        user=user,
        message__icontains="accounts awaiting approval."
    ).exclude(message__in=active_notifications).delete()

    # Fetch remaining notifications for display
    notifications = Notification.objects.filter(user=user).order_by("-date")
    return notifications

# Create your views here.
def dashboard(request):
    teacher = TeacherDetails.objects.get(user=request.user)
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "trainings":Training.objects.all(),
        "approve_teacher":UserPermission.objects.filter(is_teacher=True,is_approved=False),
        "approve_student":UserPermission.objects.filter(is_student=True,is_approved=False),
        "approve_resume":StudentDetails.objects.filter(branch=teacher.specialization,course=teacher.department,user__user_permission__is_approved=True,user__user_permission__is_student=True,is_resume_approved=False).exclude(resume=""),
        "approved_student":StudentDetails.objects.filter(branch=teacher.specialization,course=teacher.department,user__user_permission__is_approved=True,user__user_permission__is_student=True,is_resume_approved=True),
        "notifications":add_notifications(request),
         "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    print(content["user_data"].is_teacher)
    
    return render(request,"teacher/dashboard.html",content)

def profile(request):
    if request.method == 'POST':
        try:
            img = request.FILES.get("profile_picture")
        except:
            img = None
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")
        dob = request.POST.get("date_of_birth")
        gender = request.POST.get("gender")
        blood_group = request.POST.get("blood_group")
        address = request.POST.get("address")
        hide = request.POST.get("hide")
        if hide is None:
            print(name,email,phone,dob,gender,blood_group,address,img)
            TeacherDetails.objects.create(user=request.user,name=name,email=email,phone=phone,date_of_birth=dob,gender=gender,blood_group=blood_group,address=address,profile_picture=img).save()
            messages.success(request,"Your Profile has been added")
            return redirect("teacher:profile")
        else:
            teacher = TeacherDetails.objects.get(user= request.user)
            teacher.name = name
            teacher.email = email
            teacher.phone = phone
            teacher.address = address
            teacher.gender = gender
            teacher.date_of_birth = dob
            teacher.blood_group = blood_group
            if img:
                if teacher.profile_picture:
                    teacher.profile_picture.delete()
                teacher.profile_picture = img
            teacher.save()
            messages.success(request,"Profile has been updated")
            return redirect("teacher:profile")
    
    blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
    genders = ['Male', 'Female', 'Other']
    
    try:
        teacher = TeacherDetails.objects.get(user=request.user)
    except:
        teacher = None
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        'blood_groups': blood_groups,
        'genders': genders,
        "notifications":add_notifications(request),
        'teacher':teacher,
    }
    return render(request,"teacher/profile.html",content)

def approvestudents(request):
    teacher = TeacherDetails.objects.get(user=request.user)
    print(teacher.department)
    print(StudentDetails.objects.filter(name="s1"))
    students = StudentDetails.objects.filter(user__user_permission__is_student=True,user__user_permission__is_approved=False,course=teacher.department,branch=teacher.specialization)
    print(students)
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "students":students,
        "notifications":add_notifications(request),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"teacher/approvestudents.html",content)


def approve(request,id):
    student = StudentDetails.objects.get(id=id)
    user_permission = UserPermission.objects.get(user=student.user)
    user_permission.is_approved = True
    user_permission.save()
    messages.success(request,"Student has been approved")
    return redirect("teacher:approvestudents")

def reject(request,id):
    student = StudentDetails.objects.get(id=id)
    user = User.objects.get(id=student.user.id)
    user.delete()
    messages.success(request,"Student has been deleted")
    return redirect("teacher:approvestudents")

def resume(request):
    if request.method == "POST":
        s_id = request.POST.get("s_id")
        print(s_id)
        student = StudentDetails.objects.get(id = s_id)
        student.is_resume_approved = True
        student.save()
        Notification(user=student.user,message="Your resume has been approved").save()
        return redirect("teacher:resume")
    teacher = TeacherDetails.objects.get(user=request.user)
    students = StudentDetails.objects.filter(user__user_permission__is_student=True,user__user_permission__is_approved=True,course=teacher.department,branch=teacher.specialization,is_resume_approved=False).exclude(resume="")    
    print(students)
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "students":students,
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"teacher/approveresume.html",content)
    
def reject_resume(request):
    if request.method == "POST":
        s_id = request.POST.get("s_id")
        student = StudentDetails.objects.get(id = s_id)
        message = request.POST.get("feedback_message")
        student.is_resume_approved = None
        student.resume.delete()
        student.resume = None
        student.save()
        Notification(user=student.user,teacher=TeacherDetails.objects.get(user=request.user),message=message).save()
        messages.success(request,"Resume has been rejected")
    return redirect("teacher:resume")



def all_student(request):
    if request.method == "POST":
        alumni_id = request.POST.get("alumni_id")

        s_id = request.POST.get("student_id")
        message = request.POST.get("message")
        print(s_id)
        student = StudentDetails.objects.get(id=s_id)
        if request.user.user_permission.filter(is_principal=True).exists():
            print(request.user)
            Notification(user=student.user,admin=Principal.objects.get(user=request.user),message=message).save()
            messages.success(request,f"Notification sent to {student.name} sucessfully")
            if alumni_id:
                return redirect("app:alumni")
            return redirect("app:allstudents")  
        Notification(user=student.user,teacher=TeacherDetails.objects.get(user=request.user),message=message).save()
        messages.success(request,f"Notification sent to {student.name} sucessfully")

        return redirect("teacher:allstudent")
    teacher = TeacherDetails.objects.get(user= request.user)
    students = StudentDetails.objects.filter(course= teacher.department,branch=teacher.specialization,user__user_permission__is_approved=True)
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "students":students,
        "notifications":add_notifications(request),
        
    }
    return render(request,"teacher/allstudent.html",content)

def student_delete(request,id):
    
    alumni_id = request.POST.get("alumni_id")
    student = StudentDetails.objects.get(id=id)
    student.user.delete()
    messages.success(request,"Student has been deleted")
    
    if request.user.user_permission.filter(is_principal=True).exists():
        if alumni_id:
            return redirect("app:alumni")
        return redirect("app:allstudents")
    if alumni_id:
        return redirect("teacher:alumni")
    return redirect("teacher:allstudent")

def update_placement_details(request):
    if request.method == "POST":
        student_id = request.POST.get("student_id")
        job_title = request.POST.get("job_title")
        company_name = request.POST.get("company_name")
        company_location = request.POST.get("company_location")
        salary = request.POST.get("salary")
        alumni_redirect = request.POST.get("alumni_redirect")
        
        try:
            student = StudentDetails.objects.get(id=student_id)
            
            # Check if JobInfo already exists for this student
            if JobInfo.objects.filter(student=student).exists():
                # Update existing job info
                job_info = JobInfo.objects.get(student=student)
                job_info.job_title = job_title
                job_info.company_name = company_name
                job_info.company_location = company_location
                job_info.salary = float(salary) if salary else 0
                job_info.save()
                messages.success(request, f"Placement details updated for {student.name}")
            else:
                # Create new job info
                JobInfo.objects.create(
                    student=student,
                    job_title=job_title,
                    company_name=company_name,
                    company_location=company_location,
                    salary=float(salary) if salary else 0
                )
                messages.success(request, f"Placement details added for {student.name}")
            
            # Send notification to student
            Notification.objects.create(
                user=student.user,
                teacher=TeacherDetails.objects.get(user=request.user),
                message=f"Your placement details have been updated: {job_title} at {company_name}"
            )
            
        except StudentDetails.DoesNotExist:
            messages.error(request, "Student not found")
        except Exception as e:
            messages.error(request, f"Error updating placement details: {str(e)}")
        
        # Redirect based on source page
        if alumni_redirect:
            return redirect("teacher:alumni")
        return redirect("teacher:allstudent")
    
    return redirect("teacher:allstudent")

def group_notification(request):
    if request.method == "POST":
        filter_p = request.POST.get("filter_params")
        alumni_id = request.POST.get("alumni_id")
        message = request.POST.get("message")
        if not filter_p:
            filter_p = {}
        elif isinstance(filter_p, str):
            try:
                filter_p = json.loads(filter_p)
            except json.JSONDecodeError:
                filter_p = {}

        # guarantee keys exist
        filter_p.setdefault("search", "")
        filter_p.setdefault("year", "")
        print(filter_p)
        print(alumni_id)
        if request.user.user_permission.filter(is_principal=True).exists():
            if alumni_id:
            
                students = StudentDetails.objects.filter(is_passed_out=True)
            else:
                students = StudentDetails.objects.all()
            if filter_p["search"] != "" and filter_p["year"] != "":
                students = StudentDetails.objects.filter(name__contains= filter_p["search"],year=filter_p["year"])
            elif filter_p["year"] != "":
                print("year")
                students = StudentDetails.objects.filter(year=filter_p["year"])
            else:

                if alumni_id:
                    student = StudentDetails.objects.filter(is_passed_out=True)
                else:
                    students = StudentDetails.objects.filter(name__icontains= filter_p["search"])
            for student in students:  
                Notification(user=student.user,message=message).save()
            print(len(students))
            messages.success(request,f"Notification sent to {len(students)} students sucessfully")
            if alumni_id:
                return redirect("app:alumni")
            return redirect("app:allstudents")
        else:
            teacher = TeacherDetails.objects.get(user= request.user)
            if filter_p["search"] != "" and filter_p["year"] != "":
                students = StudentDetails.objects.filter(name__contains= filter_p["search"],year=filter_p["year"],course= teacher.department,branch=teacher.specialization)
            elif filter_p["year"] != "":
                print("year")
                students = StudentDetails.objects.filter(year=filter_p["year"],course= teacher.department,branch=teacher.specialization)
            else:
                if alumni_id:
                    students = StudentDetails.objects.filter(is_passed_out=True,course= teacher.department,branch=teacher.specialization)
                else:
                    students = StudentDetails.objects.filter(name__icontains= filter_p["search"],course= teacher.department,    branch=teacher.specialization)
            for student in students:  
                Notification(user=student.user,teacher=request.user.teacher.first(),message=message).save()
            messages.success(request,f"Notification sent to {len(students)} students sucessfully")
            if alumni_id:
                return redirect("teacher:alumni")
            return redirect("teacher:allstudent")
    return redirect("teacher:allstudent")

def training(request):
    teacher = request.user.teacher.first()
    if not teacher:
        messages.error(request, "Teacher profile not found")
        return redirect("teacher:training")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        training_type = request.POST.get("training_type")
        file = request.FILES.get("file")

        if training_type == "video":
            if not file:
                messages.error(request, "Video file required")
                return redirect("teacher:training")
            Training(user=teacher, title=title, description=description, vedio=file).save()

        elif training_type == "quiz":
            quiz_link = request.POST.get("quiz_link")
            if not quiz_link:
                messages.error(request, "Quiz link required")
                return redirect("teacher:training")
            Training(user=teacher, title=title, description=description, quiz_link=quiz_link).save()

        elif training_type == "meet":
            meet_link = request.POST.get("meet_link")
            meet_date = request.POST.get("meet_date")
            Training(
                user=teacher,
                title=title,
                description=description,
                gogle_meet_link=meet_link,
                date=meet_date
            ).save()

        else:
            messages.error(request, "Invalid training type")
            return redirect("teacher:training")

        messages.success(request, "Training has been added")
        return redirect("teacher:training")

    content = {
        "user_data": UserPermission.objects.get(user=request.user),
        "trainings": Training.objects.all(),
        "notifications": Notification.objects.filter(user=request.user).order_by("-id"),
        "notifications_count": Notification.objects.filter(user=request.user, is_read=False).count()
    }
    return render(request, "teacher/training.html", content)

def edit_training(request):
    if request.method != "POST":
        return redirect("teacher:training")

    training_id = request.POST.get("training_id")
    training = Training.objects.get(id=training_id)

    # Basic fields
    training.title = request.POST.get("title")
    training.description = request.POST.get("description")

    # File replacement (video / quiz)
    new_file = request.FILES.get("file")

    if training.gogle_meet_link:
        # Editing a Google Meet training
        training.gogle_meet_link = request.POST.get("meet_link")
        training.date = request.POST.get("meet_date")

    elif training.quiz_link:
        # Editing a Quiz training
        training.quiz_link = request.POST.get("quiz_link")

    elif new_file:
        # Replace existing file only if a new one is uploaded
        if training.vedio:
            training.vedio = new_file

    training.save()
    messages.success(request, "Training updated successfully")
    return redirect("teacher:training")

def delete_training(request,id):
    training = Training.objects.get(id=id)
    training.delete()
    messages.success(request,"Training has been deleted")
    return redirect("teacher:training")

def approve_teacher(request):
    if request.method == "POST":
        username = request.POST.get("username")
        
        teacher = UserPermission.objects.get(user__username=username)

        teacher.is_approved = True
        teacher.save()
        messages.success(request,"Teacher has been approved")
        return redirect("teacher:approve_teacher")
    teachers = UserPermission.objects.filter(is_teacher= True,is_approved= False)
    
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "teachers":teachers,
        "approved_teachers":TeacherDetails.objects.filter(user__user_permission__is_approved=True,user__user_permission__is_teacher=True,is_hod=False),
        "notifications":add_notifications(request),
        "notifications" : Notification.objects.filter(user=request.user).order_by("-id"),
        "degrees":DegreeSpecialization.objects.values("degree").distinct(),
        "specializations":DegreeSpecialization.objects.all(),
        "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request,"teacher/approve.html",content)


def assign_designation(request):
    if request.method == "POST":
        id = request.POST.get("teacher_id")
        designation = request.POST.get("designation")
        placement_faculty = request.POST.get("is_placement") == "on"
        print(placement_faculty)
        teacher = TeacherDetails.objects.get(id=id)
        teacher.designation = designation
   
        teacher.is_placement_faculty = placement_faculty
        teacher.save()
        messages.success(request,"Your profile has been updated") 
        return redirect("teacher:approve_teacher")
    return redirect("teacher:approve_teacher")


def report(request):
    year = None
    if request.method == "POST":
        year = request.POST.get("year")
        print(year)
        try:
            year = int(year)
        except (TypeError, ValueError):
            year = None
        if year is not None:
            students = StudentDetails.objects.filter(
                user__date_joined__year=year,
                user__user_permission__is_student=True,
                user__user_permission__is_approved=True
            )
            company = CompanyDetails.objects.all()
            placed_students = StudentDetails.objects.filter(
                job_info__isnull=False,
                job_info__date__year=year
            ).distinct()
            company_placed_students = (
                JobInfo.objects
                .filter(student__user__date_joined__year=year)
                .exclude(company_name__isnull=True)
                .exclude(company_name__exact="")
                .values("company_name")
                .annotate(placed_count=Count("student", distinct=True))
                .order_by("company_name")
            )
        else:
            students = StudentDetails.objects.filter(
                user__user_permission__is_student=True,
                user__user_permission__is_approved=True
            )
            company = CompanyDetails.objects.all()
            placed_students = StudentDetails.objects.filter(
                job_info__isnull=False,
            ).distinct()
            company_placed_students = (
                JobInfo.objects
                .exclude(company_name__isnull=True)
                .exclude(company_name__exact="")
                .values("company_name")
                .annotate(placed_count=Count("student", distinct=True))
                .order_by("company_name")
            )

    else:  # GET request or others
        company = CompanyDetails.objects.all()
        students = StudentDetails.objects.filter(
            user__user_permission__is_student=True,
            user__user_permission__is_approved=True
        )
        placed_students = StudentDetails.objects.filter(
            job_info__isnull=False
        ).distinct()

        company_placed_students = (
            JobInfo.objects
            .exclude(company_name__isnull=True)
            .exclude(company_name__exact="")
            .values("company_name")
            .annotate(placed_count=Count("student", distinct=True))
            .order_by("company_name")
        )

    available_years = (
        JobInfo.objects
        .annotate(year=ExtractYear("date"))
        .values_list("year", flat=True)
        .distinct()
        .order_by("-year")
    )
    print(len(company_placed_students))
    content = {
        "user_data": UserPermission.objects.get(user=request.user),
        "notifications": add_notifications(request),
        "notifications_count": Notification.objects.filter(user=request.user, is_read=False).count(),
        "company": company,
        "students": students,
        "placed_students": placed_students,
        "total_students": students.count(),
        "total_company": company.count() + len(company_placed_students),
        "total_placed_students": placed_students.count(),
        "total_not_placed_students": students.count() - placed_students.count(),
        "company_placed_students": company_placed_students,
        "available_years": available_years,
        "selected_year": int(year) if year else "",
    }

    return render(request, "app/report.html", content)


def alumin(request):
    if request.method == "POST":
        s_id = request.POST.get("student_id")
        message = request.POST.get("message")
        student = StudentDetails.objects.get(id=s_id)
        if request.user.user_permission.filter(is_principal=True).exists():
            print(request.user)
            Notification(user=student.user,admin=Principal.objects.get(user=request.user),message=message).save()
            messages.success(request,f"Notification sent to {student.name} sucessfully")
            return redirect("app:allstudents")  
        Notification(user=student.user,teacher=TeacherDetails.objects.get(user=request.user),message=message).save()
        messages.success(request,f"Notification sent to {student.name} sucessfully")
        return redirect("teacher:alumni")
    students = StudentDetails.objects.filter(
        user__user_permission__is_student=True,
        user__user_permission__is_approved=True,
        is_passed_out = True
    )
    teacher = TeacherDetails.objects.get(user=request.user)
    content = {
        "user_data":UserPermission.objects.get(user=request.user),
        "trainings":Training.objects.all(),
        "students":students,
        "approve_teacher":UserPermission.objects.filter(is_teacher=True,is_approved=False),
        "notifications":add_notifications(request),
         "notifications_count" : Notification.objects.filter(user=request.user,is_read=False).count()
    }
    return render(request, "teacher/alumni.html",content    )
