from django.urls import path
from .views import *

app_name = "app"

urlpatterns = [
    path("",index,name="home"),
    path("login/",userlogin,name="login"),
    path("register",userregister,name="register"),
    path("logout",userlogout,name="logout"),
    path("dashboard",dashboard,name="dashboard"),
    path("profile",profile,name="profile"),
    path("approve",approve,name="approve"),
    path("allstudents",allStudents,name="allstudents"),
    path("teacher",teacher,name="teacher"),
    path("company",company,name="company"),
    path("add_degree_specialization",add_degree_specialization,name="add_degree_specialization"),
    path("delete_degree_specialization/<int:id>",delete_degree_specialization,name="delete_degree_specialization"),
    path("report",report,name="report"),
    path("clear_notifications",clear_notifications,name="clear_notifications"),
    path("alumni",alumni,name="alumni"),

]
