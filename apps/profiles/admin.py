from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, InstructorProfile
# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + \
        (('Rol personalizado', {'fields': ('is_instructor',)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_instructor',)}),
    )


admin.site.register(InstructorProfile)
