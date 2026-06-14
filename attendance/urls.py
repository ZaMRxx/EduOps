from django.urls import path
from . import views

urlpatterns = [
    path('absen/', views.absensi_form, name='absensi_form'),
    path('riwayat/', views.riwayat_absensi, name='riwayat_absensi'),
    path('logs/', views.aktivitas_logs, name='aktivitas_logs'),
    path('riwayat/<int:pk>/delete/', views.absensi_delete, name='absensi_delete'),
]
