
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('scheduling', '0002_jadwalkelas_tanggal_spesifik_jadwalkelas_tipe_repeat'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='LogAktivitas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('aksi', models.CharField(max_length=50, verbose_name='Aksi')),
                ('detail', models.TextField(blank=True, verbose_name='Detail Aktivitas')),
                ('timestamp', models.DateTimeField(auto_now_add=True, verbose_name='Waktu Kejadian')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='logs', to=settings.AUTH_USER_MODEL, verbose_name='User / Akun')),
            ],
            options={
                'verbose_name': 'Log Aktivitas',
                'verbose_name_plural': 'Daftar Log Aktivitas',
                'ordering': ['-timestamp'],
            },
        ),
        migrations.CreateModel(
            name='Absensi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tanggal', models.DateField(verbose_name='Tanggal')),
                ('waktu_absen', models.TimeField(verbose_name='Waktu Absen')),
                ('status', models.CharField(choices=[('Hadir', 'Hadir'), ('Terlambat', 'Terlambat')], default='Hadir', max_length=20, verbose_name='Status Kehadiran')),
                ('foto', models.ImageField(blank=True, null=True, upload_to='absensi_photos/', verbose_name='Foto Absensi')),
                ('wajah_terdeteksi', models.BooleanField(default=False, verbose_name='Wajah Terdeteksi')),
                ('dibuat_at', models.DateTimeField(auto_now_add=True, verbose_name='Waktu Pembuatan')),
                ('guru', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='absensi', to=settings.AUTH_USER_MODEL, verbose_name='Guru')),
                ('jadwal', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='absensi', to='scheduling.jadwalkelas', verbose_name='Jadwal Kelas')),
            ],
            options={
                'verbose_name': 'Absensi',
                'verbose_name_plural': 'Daftar Absensi',
                'ordering': ['-tanggal', '-waktu_absen'],
            },
        ),
    ]
