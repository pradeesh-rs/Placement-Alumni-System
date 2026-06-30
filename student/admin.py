from django.contrib import admin
from .models import StudentDetails, JobInfo

# Register your models here.
class StudentAdmin(admin.ModelAdmin):
    list_display = ('user', 'name', 'email', 'phone', 'address', 'date_of_birth', 'gender', 'blood_group', 'profile_picture', 'course', 'branch', 'year', 'sem', 'roll_no', 'reg_no', 'cgpa')
    search_fields = ('name', 'email', 'phone', 'roll_no', 'reg_no')

class JobInfoAdmin(admin.ModelAdmin):
    list_display = ('student', 'job_title', 'company_name', 'company_location', 'salary')
    search_fields = ('student', 'job_title', 'company_name', 'company_location', 'salary')

admin.site.register(StudentDetails, StudentAdmin)
admin.site.register(JobInfo, JobInfoAdmin)
