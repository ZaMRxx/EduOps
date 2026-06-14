from django.contrib import admin
from .models import Absensi, LogAktivitas

@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    list_display = ('guru', 'jadwal', 'tanggal', 'waktu_absen', 'status', 'wajah_terdeteksi')
    list_filter = ('status', 'wajah_terdeteksi', 'tanggal')
    search_fields = ('guru__nama_lengkap', 'guru__username', 'jadwal__nama_kelas')

@admin.register(LogAktivitas)
class LogAktivitasAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'aksi', 'detail')
    list_filter = ('aksi', 'timestamp')
    search_fields = ('user__username', 'user__nama_lengkap', 'aksi', 'detail')
