from django.contrib import admin

from .models import UserPermission,Principal
# Register your models here.

class UserPermissionAdmin(admin.ModelAdmin):
    list_display = ("user","is_student","is_teacher","is_company","is_principal","is_approved")
    list_editable = ("is_approved",)
    search_fields = ("user__username",)
    list_filter = ("is_student","is_teacher","is_company","is_principal","is_approved")

admin.site.register(UserPermission,UserPermissionAdmin)

class PrincipalAdmin(admin.ModelAdmin):
    list_display = ("user","name","email","phone","address","profile_picture")

admin.site.register(Principal,PrincipalAdmin)