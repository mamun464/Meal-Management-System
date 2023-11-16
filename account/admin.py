from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin

class UserAdminConfig(UserAdmin):
    search_fields = ('email', 'fullName','phone_no',)
    list_filter =('is_active','is_staff','is_superuser')
    ordering = ('id','phone_no')
    list_display =('id','email','fullName','phone_no','user_profile_img','is_active','is_staff','is_superuser','is_manager','last_login')

    fieldsets = (
    (None, {'fields': ('fullName', 'email', 'phone_no', 'password',)}),
    ('Personal', {'fields': ('user_profile_img',)}),
    ('Permission', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_manager')}),
    )

    add_fieldsets = (
        (None,{
            'classes': ('wide',),
            'fields': ('fullName','email','phone_no','user_profile_img','password1','password2','is_active','is_staff','is_manager','is_superuser')}
        ),
    )
    

admin.site.register(CustomUser,UserAdminConfig)

# Register your models here.
