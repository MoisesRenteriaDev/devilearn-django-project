from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, InstructorProfile, Profile
# Register your models here.


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = BaseUserAdmin.fieldsets + \
        (('Rol personalizado', {'fields': ('is_instructor',)}),)
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (None, {'fields': ('is_instructor',)}),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company', 'profession', 'timezone', 'photo')


admin.site.register(InstructorProfile)
