from django.contrib import admin
from .models import User,StaffUser
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# Register your models here.
@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2','assigned_staff','phone_number', 'email', 'first_name', 'last_name','question'),
        }),
    )
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (("Personal info"), {"fields": ("first_name", "last_name", "email")}),
        (("Staff Info"),{'fields':('assigned_staff',)}),
        (
            ("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    

@admin.register(StaffUser)
class StaffUserAdmin(admin.ModelAdmin):
    pass
