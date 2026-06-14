from django.db import models
from django.conf import settings
from decimal import Decimal
class Sekolah(models.Model):
    TIPE_CHOICES = [
        ('regular', 'Reguler'),
        ('mitra', 'Mitra'),
    ]
    
    nama = models.CharField(max_length=100, verbose_name="Nama Sekolah")
    branch = models.CharField(max_length=50, verbose_name="Cabang / Branch")
    tipe = models.CharField(max_length=20, choices=TIPE_CHOICES, default='regular', verbose_name="Tipe Sekolah")

    def __str__(self):
        return f"{self.nama} ({self.branch})"
        
    class Meta:
        verbose_name = "Sekolah"
        verbose_name_plural = "Daftar Sekolah"
class JadwalKelas(models.Model):
    HARI_CHOICES = [
        ('Senin', 'Senin'),
        ('Selasa', 'Selasa'),
        ('Rabu', 'Rabu'),
        ('Kamis', 'Kamis'),
        ('Jumat', 'Jumat'),
        ('Sabtu', 'Sabtu'),
        ('Minggu', 'Minggu'),
    ]
    
    MODE_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
    ]
    
    TIPE_JADWAL_CHOICES = [
        ('regular', 'Regular'),
        ('event', 'Event'),
    ]
    
    KEGIATAN_CHOICES = [
        ('mengajar', 'Mengajar (Main)'),
        ('asistensi', 'Asistensi (Asst)'),
        ('lainnya', 'Lainnya'),
    ]
    guru = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='jadwal',
        verbose_name="Guru / Teacher"
    )
    sekolah = models.ForeignKey(
        Sekolah, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='jadwal',
        verbose_name="Sekolah / Lokasi"
    )
    
    nama_kelas = models.CharField(max_length=100, verbose_name="Nama Kelas")
    hari = models.CharField(max_length=15, choices=HARI_CHOICES, verbose_name="Hari Kelas")
    jam_mulai = models.TimeField(verbose_name="Jam Mulai")
    jam_selesai = models.TimeField(verbose_name="Jam Selesai")
    pertemuan_per_minggu = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Pertemuan per Minggu"
    )
    jam_berangkat_pulang = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name="Total Jam Berangkat dan Pulang"
    )
    kali_ke_sekolah_per_minggu = models.PositiveSmallIntegerField(
        default=1,
        verbose_name="Kali per Minggu ke Sekolah"
    )
    
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default='offline', verbose_name="Mode Belajar")
    tipe = models.CharField(max_length=50, default='Regular', verbose_name="Tipe Jadwal")
    kegiatan = models.CharField(max_length=20, choices=KEGIATAN_CHOICES, default='mengajar', verbose_name="Jenis Kegiatan")
    
    aktif = models.BooleanField(default=True, verbose_name="Status Aktif")
    tipe_repeat = models.CharField(
        max_length=20,
        choices=[('weekly', 'Repeatable (Tiap Minggu)'), ('one_time', 'One-Time (Sekali saja)')],
        default='weekly',
        verbose_name="Tipe Perulangan"
    )
    tanggal_spesifik = models.DateField(
        null=True, 
        blank=True, 
        verbose_name="Tanggal Spesifik (Untuk Sekali mengajar)"
    )
    tanggal_mulai_efektif = models.DateField(null=True, blank=True, verbose_name="Mulai Efektif")
    tanggal_selesai = models.DateField(null=True, blank=True, verbose_name="Selesai Efektif")

    @property
    def durasi_jam_mengajar(self):
        mulai = self.jam_mulai.hour * 60 + self.jam_mulai.minute
        selesai = self.jam_selesai.hour * 60 + self.jam_selesai.minute
        durasi_menit = max(selesai - mulai, 0)
        return (Decimal(durasi_menit) / Decimal('60')).quantize(Decimal('0.01'))

    @property
    def load_mengajar(self):
        return (self.durasi_jam_mengajar * Decimal(self.pertemuan_per_minggu)).quantize(Decimal('0.01'))

    @property
    def load_perjalanan(self):
        return (self.jam_berangkat_pulang * Decimal(self.kali_ke_sekolah_per_minggu)).quantize(Decimal('0.01'))

    @property
    def nilai_load(self):
        return (self.load_mengajar + self.load_perjalanan).quantize(Decimal('0.01'))

    def __str__(self):
        return f"{self.nama_kelas} - {self.guru} ({self.hari} {self.jam_mulai.strftime('%H:%M')}-{self.jam_selesai.strftime('%H:%M')})"
        
    class Meta:
        verbose_name = "Jadwal Kelas"
        verbose_name_plural = "Daftar Jadwal Kelas"
class RequestJadwal(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    REQUEST_TYPE_CHOICES = [
        ('add', 'Jadwal Baru'),
        ('edit', 'Perubahan Jadwal'),
    ]
    pengaju = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='request_jadwal',
        verbose_name="Pengaju"
    )

    request_type = models.CharField(
        max_length=10,
        choices=REQUEST_TYPE_CHOICES,
        default='add',
        verbose_name="Jenis Request"
    )
    target_jadwal = models.ForeignKey(
        JadwalKelas,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='request_perubahan',
        verbose_name="Jadwal yang Diubah"
    )
    guru = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='request_jadwal_diajukan',
        null=True,
        blank=True,
        verbose_name="Guru / Teacher"
    )
    sekolah = models.ForeignKey(
        Sekolah,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='request_jadwal',
        verbose_name="Sekolah / Lokasi"
    )
    nama_kelas = models.CharField(max_length=100, blank=True, verbose_name="Nama Kelas")
    hari = models.CharField(max_length=15, choices=JadwalKelas.HARI_CHOICES, blank=True, verbose_name="Hari Kelas")
    jam_mulai = models.TimeField(null=True, blank=True, verbose_name="Jam Mulai")
    jam_selesai = models.TimeField(null=True, blank=True, verbose_name="Jam Selesai")
    pertemuan_per_minggu = models.PositiveSmallIntegerField(default=1, verbose_name="Pertemuan per Minggu")
    jam_berangkat_pulang = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('0.00'), verbose_name="Total Jam Berangkat dan Pulang")
    kali_ke_sekolah_per_minggu = models.PositiveSmallIntegerField(default=1, verbose_name="Kali per Minggu ke Sekolah")
    mode = models.CharField(max_length=10, choices=JadwalKelas.MODE_CHOICES, default='offline', verbose_name="Mode Belajar")
    tipe = models.CharField(max_length=50, default='Regular', verbose_name="Tipe Jadwal")
    kegiatan = models.CharField(max_length=20, choices=JadwalKelas.KEGIATAN_CHOICES, default='mengajar', verbose_name="Jenis Kegiatan")
    tipe_repeat = models.CharField(
        max_length=20,
        choices=[('weekly', 'Repeatable (Tiap Minggu)'), ('one_time', 'One-Time (Sekali saja)')],
        default='weekly',
        verbose_name="Tipe Perulangan"
    )
    tanggal_spesifik = models.DateField(null=True, blank=True, verbose_name="Tanggal Spesifik")
    tanggal_mulai_efektif = models.DateField(null=True, blank=True, verbose_name="Mulai Efektif")
    tanggal_selesai = models.DateField(null=True, blank=True, verbose_name="Selesai Efektif")
    
    detail = models.TextField(verbose_name="Detail Request Jadwal")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending', verbose_name="Status Request")
    
    dibuat_at = models.DateTimeField(auto_now_add=True, verbose_name="Tanggal Pengajuan")
    diproses_at = models.DateTimeField(null=True, blank=True, verbose_name="Tanggal Diproses")
    diproses_oleh = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='prosesor',
        verbose_name="Diproses Oleh"
    )

    def __str__(self):
        return f"Request #{self.id} oleh {self.pengaju} ({self.status})"

    def apply_to_schedule(self):
        data = {
            'guru': self.guru,
            'sekolah': self.sekolah,
            'nama_kelas': self.nama_kelas,
            'hari': self.hari,
            'jam_mulai': self.jam_mulai,
            'jam_selesai': self.jam_selesai,
            'pertemuan_per_minggu': self.pertemuan_per_minggu,
            'jam_berangkat_pulang': self.jam_berangkat_pulang,
            'kali_ke_sekolah_per_minggu': self.kali_ke_sekolah_per_minggu,
            'mode': self.mode,
            'tipe': self.tipe,
            'kegiatan': self.kegiatan,
            'tipe_repeat': self.tipe_repeat,
            'tanggal_spesifik': self.tanggal_spesifik,
            'tanggal_mulai_efektif': self.tanggal_mulai_efektif,
            'tanggal_selesai': self.tanggal_selesai,
            'aktif': True,
        }

        if self.request_type == 'edit' and self.target_jadwal:
            for field, value in data.items():
                setattr(self.target_jadwal, field, value)
            self.target_jadwal.save()
            return self.target_jadwal

        return JadwalKelas.objects.create(**data)
        
    class Meta:
        verbose_name = "Request Jadwal"
        verbose_name_plural = "Daftar Request Jadwal"
