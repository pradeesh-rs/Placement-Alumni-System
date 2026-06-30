from django.urls import path
from .views import *

app_name ="teacher"

urlpatterns = [
    path("",dashboard,name="teacher"),
    path("profile/",profile,name="profile"),
    path("approvestudents/",approvestudents,name="approvestudents"),
    path("approve/<int:id>",approve,name="approve"),
    path("reject/<int:id>",reject,name="reject"),
    path("resume",resume,name="resume"),
    path("recjec_resume",reject_resume,name="reject_resume"),
    path("allstudent",all_student,name="allstudent"),
    path("studentdelete/<int:id>",student_delete,name="student_delete"),
    path("group_notification",group_notification,name="group_notification"),
    path("training",training,name="training"),
    path("training/edit/", edit_training, name="edit_training"),
    path("delete/<int:id>",delete_training,name="delete_training"),
    path("approve_teacher",approve_teacher,name="approve_teacher"),
    path("assign_designation",assign_designation,name="assign_designation"),
    path("update_placement_details",update_placement_details,name="update_placement_details"),
    path("report",report,name="report"),
    path("alumni",alumin,name="alumni"),

    
]


