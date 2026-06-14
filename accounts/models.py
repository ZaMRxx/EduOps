from django.db import models
from django.contrib.auth.models import AbstractUser
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('super_admin', 'Super Admin'),
        ('admin_op', 'Admin Operasional'),
        ('admin_hr', 'Admin HR'),
        ('admin_branch', 'Admin Branch'),
        ('teacher', 'Teacher'),
    ]
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='teacher',
        verbose_name="Peran"
    )
    nama_lengkap = models.CharField(
        max_length=100, 
        verbose_name="Nama Lengkap"
    )
    no_wa = models.CharField(
        max_length=20, 
        blank=True, 
        verbose_name="Nomor WhatsApp"
    )
    branch = models.CharField(
        max_length=50, 
        blank=True, 
        verbose_name="Cabang"
    )
    warna_kalender = models.CharField(
        max_length=7, 
        default='#4CAF50', 
        verbose_name="Warna Kalender"
    )
    foto_profile = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
        verbose_name="Foto Profil"
    )

    def __str__(self):
        return self.nama_lengkap if self.nama_lengkap else self.username
