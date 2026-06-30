from django.urls import path
from .views import *

app_name = "student"

urlpatterns = [
    path("",dashboard,name="student"),
    path("profile/",profile,name="profile"),
    path("notifications/<int:pk>/read/", mark_notification_read, name="mark_notification_read"),
    path("notifications/modal/<int:pk>/read/", mark_notification_read_modal, name="mark_notification_read_modal"),
    path("training/",training,name="training"),
    path("cgpa-calculator/", cgpa_calculator, name="cgpa_calculator"),
    path("cgpa-calculator/delete/<int:pk>/", delete_semester_grade, name="delete_semester_grade"),
    path("cgpa-calculator/delete-all/", delete_all_cgpa_records, name="delete_all_cgpa_records"),
]