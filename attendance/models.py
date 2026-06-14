from django.db import models
from django.conf import settings

class Absensi(models.Model):
    STATUS_CHOICES = [
        ('Hadir', 'Hadir'),
        ('Terlambat', 'Terlambat'),
    ]

    guru = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='absensi',
        verbose_name="Guru"
    )
    jadwal = models.ForeignKey(
        'scheduling.JadwalKelas',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='absensi',
        verbose_name="Jadwal Kelas"
    )
    tanggal = models.DateField(verbose_name="Tanggal")
    waktu_absen = models.TimeField(verbose_name="Waktu Absen")
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Hadir',
        verbose_name="Status Kehadiran"
    )
    foto = models.ImageField(
        upload_to='absensi_photos/',
        null=True,
        blank=True,
        verbose_name="Foto Absensi"
    )
    wajah_terdeteksi = models.BooleanField(
        default=False,
        verbose_name="Wajah Terdeteksi"
    )
    dibuat_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Waktu Pembuatan"
    )

    def __str__(self):
        return f"{self.guru.nama_lengkap} - {self.jadwal.nama_kelas if self.jadwal else 'Tanpa Jadwal'} ({self.tanggal} {self.waktu_absen.strftime('%H:%M')})"

    class Meta:
        verbose_name = "Absensi"
        verbose_name_plural = "Daftar Absensi"
        ordering = ['-tanggal', '-waktu_absen']

class LogAktivitas(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs',
        verbose_name="User / Akun"
    )
    aksi = models.CharField(
        max_length=50,
        verbose_name="Aksi"
    )
    detail = models.TextField(
        blank=True,
        verbose_name="Detail Aktivitas"
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Waktu Kejadian"
    )

    def __str__(self):
        username = self.user.username if self.user else "System/Anonymous"
        return f"[{self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}] {username} - {self.aksi}"

    class Meta:
        verbose_name = "Log Aktivitas"
        verbose_name_plural = "Daftar Log Aktivitas"
        ordering = ['-timestamp']
