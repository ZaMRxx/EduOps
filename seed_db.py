import os
import datetime
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eoas.settings')
django.setup()

from accounts.models import CustomUser
from attendance.models import Absensi, LogAktivitas
from scheduling.models import JadwalKelas, RequestJadwal, Sekolah


def create_user(username, email, password, nama_lengkap, role, branch='', is_staff=False, is_superuser=False, warna='#08aeb3'):
    user = CustomUser.objects.create_user(
        username=username,
        email=email,
        password=password,
        nama_lengkap=nama_lengkap,
        role=role,
        branch=branch,
        warna_kalender=warna,
        is_staff=is_staff,
        is_superuser=is_superuser,
        is_active=True,
    )
    return user


def make_time(value):
    return datetime.datetime.strptime(value, '%H:%M').time()


print('Resetting demo data...')
Absensi.objects.all().delete()
LogAktivitas.objects.all().delete()
RequestJadwal.objects.all().delete()
JadwalKelas.objects.all().delete()
Sekolah.objects.all().delete()
CustomUser.objects.all().delete()

print('Creating users...')
superadmin = create_user(
    'superadmin',
    'superadmin@educourse.id',
    'Superadmin123!',
    'Super Admin EduOps',
    'super_admin',
    is_staff=True,
    is_superuser=True,
    warna='#111827',
)
admin_op = create_user(
    'admin.ops',
    'admin.ops@educourse.id',
    'AdminOps123!',
    'Admin Operasional',
    'admin_op',
    warna='#08aeb3',
)
admin_branch = create_user(
    'admin.bsd',
    'admin.bsd@educourse.id',
    'AdminBsd123!',
    'Admin Branch BSD',
    'admin_branch',
    'BSD',
    warna='#22c55e',
)
teachers = [
    create_user('teacher.ahmad', 'ahmad@educourse.id', 'Teacher123!', 'Ahmad Muhajir', 'teacher', 'BSD', warna='#12b3a8'),
    create_user('teacher.anisa', 'anisa@educourse.id', 'Teacher123!', 'Anisa Fitriyani', 'teacher', 'Bintaro', warna='#f6c44f'),
    create_user('teacher.cici', 'cici@educourse.id', 'Teacher123!', 'Cici Paramida', 'teacher', 'Bandung', warna='#a78bfa'),
    create_user('teacher.hadi', 'hadi@educourse.id', 'Teacher123!', 'Hadi Wijaya', 'teacher', 'Surabaya', warna='#2dd4bf'),
]

print('Creating schools...')
schools = {
    'bsd': Sekolah.objects.create(nama='Educourse BSD', branch='BSD', tipe='regular'),
    'bintaro': Sekolah.objects.create(nama='Educourse Bintaro', branch='Bintaro', tipe='regular'),
    'bandung': Sekolah.objects.create(nama='Educourse Bandung', branch='Bandung', tipe='regular'),
    'surabaya': Sekolah.objects.create(nama='Educourse Surabaya', branch='Surabaya', tipe='mitra'),
}

print('Creating schedules...')
schedules = [
    (teachers[0], schools['bsd'], 'Scratch Junior', 'Senin', '08:00', '09:30', 'offline', 'mengajar', 'Reguler'),
    (teachers[0], schools['bsd'], 'Robotics Beginner', 'Minggu', '10:00', '11:30', 'offline', 'mengajar', 'Reguler'),
    (teachers[1], schools['bintaro'], 'Creative Coding', 'Rabu', '15:00', '16:30', 'offline', 'asistensi', 'Reguler'),
    (teachers[1], schools['bintaro'], 'Mobile App Kids', 'Jumat', '18:30', '20:00', 'online', 'mengajar', 'Event'),
    (teachers[2], schools['bandung'], 'AI Kids Explorer', 'Minggu', '13:00', '14:30', 'offline', 'mengajar', 'Reguler'),
    (teachers[3], schools['surabaya'], 'STEM Project Class', 'Selasa', '14:00', '16:00', 'offline', 'mengajar', 'Workshop'),
]

for guru, sekolah, nama_kelas, hari, jam_mulai, jam_selesai, mode, kegiatan, tipe in schedules:
    JadwalKelas.objects.create(
        guru=guru,
        sekolah=sekolah,
        nama_kelas=nama_kelas,
        hari=hari,
        jam_mulai=make_time(jam_mulai),
        jam_selesai=make_time(jam_selesai),
        mode=mode,
        kegiatan=kegiatan,
        tipe=tipe,
        tipe_repeat='weekly',
        pertemuan_per_minggu=1,
        jam_berangkat_pulang=1,
        kali_ke_sekolah_per_minggu=1 if mode == 'offline' else 0,
        aktif=True,
    )

RequestJadwal.objects.create(
    pengaju=teachers[0],
    tipe_request='add',
    guru=teachers[0],
    sekolah=schools['bsd'],
    nama_kelas='Coding Trial Class',
    hari='Kamis',
    jam_mulai=make_time('16:00'),
    jam_selesai=make_time('17:30'),
    mode='offline',
    kegiatan='mengajar',
    tipe='Trial',
    status='pending',
)

print('Seed completed.')
print('')
print('Login credentials:')
print('Super Admin  : superadmin@educourse.id / Superadmin123!')
print('Admin Op     : admin.ops@educourse.id / AdminOps123!')
print('Admin Branch : admin.bsd@educourse.id / AdminBsd123!')
print('Teachers     : ahmad@educourse.id, anisa@educourse.id, cici@educourse.id, hadi@educourse.id / Teacher123!')
print('')
print(f'Superuser check: {superadmin.username} role={superadmin.role} is_superuser={superadmin.is_superuser}')
