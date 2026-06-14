from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informasi EduOps', {'fields': ('role', 'nama_lengkap', 'no_wa', 'branch', 'warna_kalender', 'foto_profile')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Informasi EduOps', {'fields': ('role', 'nama_lengkap', 'no_wa', 'branch', 'warna_kalender', 'foto_profile', 'email')}),
    )
    
    list_display = ('username', 'nama_lengkap', 'role', 'branch', 'is_staff')
    list_filter = ('role', 'branch', 'is_active', 'is_staff')
    search_fields = ('username', 'nama_lengkap', 'email', 'branch')
    ordering = ('username',)
