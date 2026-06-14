from django.contrib import admin
from .models import Sekolah, JadwalKelas, RequestJadwal
@admin.register(Sekolah)
class SekolahAdmin(admin.ModelAdmin):
    list_display = ('nama', 'branch', 'tipe')
    list_filter = ('branch', 'tipe')
    search_fields = ('nama', 'branch')
    ordering = ('branch', 'nama')
@admin.register(JadwalKelas)
class JadwalKelasAdmin(admin.ModelAdmin):
    list_display = ('nama_kelas', 'guru', 'sekolah', 'hari', 'jam_mulai', 'jam_selesai', 'pertemuan_per_minggu', 'jam_berangkat_pulang', 'kali_ke_sekolah_per_minggu', 'nilai_load', 'mode', 'tipe_repeat', 'tanggal_spesifik', 'aktif')
    list_filter = ('hari', 'mode', 'tipe_repeat', 'tipe', 'kegiatan', 'aktif', 'sekolah__branch')
    search_fields = ('nama_kelas', 'guru__nama_lengkap', 'guru__username', 'sekolah__nama')
    ordering = ('hari', 'jam_mulai')
    list_editable = ('aktif',)
@admin.register(RequestJadwal)
class RequestJadwalAdmin(admin.ModelAdmin):
    list_display = ('id', 'request_type', 'nama_kelas', 'guru', 'pengaju', 'status', 'dibuat_at', 'diproses_oleh', 'diproses_at')
    list_filter = ('status', 'request_type', 'dibuat_at')
    search_fields = ('pengaju__nama_lengkap', 'pengaju__username', 'guru__nama_lengkap', 'nama_kelas', 'detail')
    ordering = ('-dibuat_at',)
    readonly_fields = ('dibuat_at',)
