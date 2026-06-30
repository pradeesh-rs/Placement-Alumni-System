from django.contrib import admin
from .models import CompanyDetails

# Register your models here.
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name","email","phone","location","industry_type")

admin.site.register(CompanyDetails,CompanyAdmin)


