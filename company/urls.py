from django.urls import path
from .views import *

app_name = "company"

urlpatterns = [
    path("",dashboard,name="company"),
    path("profile",profile,name="profile"),    
    path("jobs",jobs,name="jobs"),
    path("deletejob/<int:id>",deletejob,name="deletejob"),
    path("eligible_students/<int:id>",eligible_students,name="eligible_students"),
    path("applied_students/<int:id>",applied_students,name="applied_students"),


]