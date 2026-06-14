
from decimal import Decimal
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('scheduling', '0004_jadwalkelas_load_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='requestjadwal',
            name='request_type',
            field=models.CharField(choices=[('add', 'Jadwal Baru'), ('edit', 'Perubahan Jadwal')], default='add', max_length=10, verbose_name='Jenis Request'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='target_jadwal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='request_perubahan', to='scheduling.jadwalkelas', verbose_name='Jadwal yang Diubah'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='guru',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='request_jadwal_diajukan', to=settings.AUTH_USER_MODEL, verbose_name='Guru / Teacher'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='sekolah',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='request_jadwal', to='scheduling.sekolah', verbose_name='Sekolah / Lokasi'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='nama_kelas',
            field=models.CharField(blank=True, max_length=100, verbose_name='Nama Kelas'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='hari',
            field=models.CharField(blank=True, choices=[('Senin', 'Senin'), ('Selasa', 'Selasa'), ('Rabu', 'Rabu'), ('Kamis', 'Kamis'), ('Jumat', 'Jumat'), ('Sabtu', 'Sabtu'), ('Minggu', 'Minggu')], max_length=15, verbose_name='Hari Kelas'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='jam_mulai',
            field=models.TimeField(blank=True, null=True, verbose_name='Jam Mulai'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='jam_selesai',
            field=models.TimeField(blank=True, null=True, verbose_name='Jam Selesai'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='pertemuan_per_minggu',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Pertemuan per Minggu'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='jam_berangkat_pulang',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Total Jam Berangkat dan Pulang'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='kali_ke_sekolah_per_minggu',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Kali per Minggu ke Sekolah'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='mode',
            field=models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], default='offline', max_length=10, verbose_name='Mode Belajar'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='tipe',
            field=models.CharField(default='Regular', max_length=50, verbose_name='Tipe Jadwal'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='kegiatan',
            field=models.CharField(choices=[('mengajar', 'Mengajar (Main)'), ('asistensi', 'Asistensi (Asst)'), ('lainnya', 'Lainnya')], default='mengajar', max_length=20, verbose_name='Jenis Kegiatan'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='tipe_repeat',
            field=models.CharField(choices=[('weekly', 'Repeatable (Tiap Minggu)'), ('one_time', 'One-Time (Sekali saja)')], default='weekly', max_length=20, verbose_name='Tipe Perulangan'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='tanggal_spesifik',
            field=models.DateField(blank=True, null=True, verbose_name='Tanggal Spesifik'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='tanggal_mulai_efektif',
            field=models.DateField(blank=True, null=True, verbose_name='Mulai Efektif'),
        ),
        migrations.AddField(
            model_name='requestjadwal',
            name='tanggal_selesai',
            field=models.DateField(blank=True, null=True, verbose_name='Selesai Efektif'),
        ),
    ]
