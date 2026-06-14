
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Sekolah',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama', models.CharField(max_length=100, verbose_name='Nama Sekolah')),
                ('branch', models.CharField(max_length=50, verbose_name='Cabang / Branch')),
                ('tipe', models.CharField(choices=[('regular', 'Regular'), ('mitra', 'Mitra')], default='regular', max_length=20, verbose_name='Tipe Sekolah')),
            ],
            options={
                'verbose_name': 'Sekolah',
                'verbose_name_plural': 'Daftar Sekolah',
            },
        ),
        migrations.CreateModel(
            name='RequestJadwal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('detail', models.TextField(verbose_name='Detail Request Jadwal')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending', max_length=15, verbose_name='Status Request')),
                ('dibuat_at', models.DateTimeField(auto_now_add=True, verbose_name='Tanggal Pengajuan')),
                ('diproses_at', models.DateTimeField(blank=True, null=True, verbose_name='Tanggal Diproses')),
                ('diproses_oleh', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='prosesor', to=settings.AUTH_USER_MODEL, verbose_name='Diproses Oleh')),
                ('pengaju', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request_jadwal', to=settings.AUTH_USER_MODEL, verbose_name='Pengaju')),
            ],
            options={
                'verbose_name': 'Request Jadwal',
                'verbose_name_plural': 'Daftar Request Jadwal',
            },
        ),
        migrations.CreateModel(
            name='JadwalKelas',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nama_kelas', models.CharField(max_length=100, verbose_name='Nama Kelas')),
                ('hari', models.CharField(choices=[('Senin', 'Senin'), ('Selasa', 'Selasa'), ('Rabu', 'Rabu'), ('Kamis', 'Kamis'), ('Jumat', 'Jumat'), ('Sabtu', 'Sabtu'), ('Minggu', 'Minggu')], max_length=15, verbose_name='Hari Kelas')),
                ('jam_mulai', models.TimeField(verbose_name='Jam Mulai')),
                ('jam_selesai', models.TimeField(verbose_name='Jam Selesai')),
                ('mode', models.CharField(choices=[('online', 'Online'), ('offline', 'Offline')], default='offline', max_length=10, verbose_name='Mode Belajar')),
                ('tipe', models.CharField(choices=[('regular', 'Regular'), ('event', 'Event')], default='regular', max_length=20, verbose_name='Tipe Jadwal')),
                ('kegiatan', models.CharField(choices=[('mengajar', 'Mengajar (Main)'), ('asistensi', 'Asistensi (Asst)'), ('lainnya', 'Lainnya')], default='mengajar', max_length=20, verbose_name='Jenis Kegiatan')),
                ('aktif', models.BooleanField(default=True, verbose_name='Status Aktif')),
                ('tanggal_mulai_efektif', models.DateField(blank=True, null=True, verbose_name='Mulai Efektif')),
                ('tanggal_selesai', models.DateField(blank=True, null=True, verbose_name='Selesai Efektif')),
                ('guru', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jadwal', to=settings.AUTH_USER_MODEL, verbose_name='Guru / Teacher')),
                ('sekolah', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='jadwal', to='scheduling.sekolah', verbose_name='Sekolah / Lokasi')),
            ],
            options={
                'verbose_name': 'Jadwal Kelas',
                'verbose_name_plural': 'Daftar Jadwal Kelas',
            },
        ),
    ]
