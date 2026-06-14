import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eoas.settings')
django.setup()

from accounts.models import CustomUser
from scheduling.models import Sekolah, JadwalKelas
import datetime

# 8 Branches
branches = ['BSD', 'Bintaro', 'Bandung', 'Surabaya', 'Yogyakarta', 'Medan', 'Makassar', 'Semarang']

# Create Sekolah for each branch
sekolah_data = [
    ('Educourse BSD', 'BSD', 'regular'),
    ('Educourse Bintaro', 'Bintaro', 'regular'),
    ('Educourse Bandung', 'Bandung', 'regular'),
    ('Educourse Surabaya', 'Surabaya', 'regular'),
    ('Educourse Yogyakarta', 'Yogyakarta', 'regular'),
    ('Educourse Medan', 'Medan', 'mitra'),
    ('Educourse Makassar', 'Makassar', 'mitra'),
    ('Educourse Semarang', 'Semarang', 'regular'),
]

for nama, branch, tipe in sekolah_data:
    Sekolah.objects.get_or_create(nama=nama, branch=branch, defaults={'tipe': tipe})

# 10 Teachers
teachers_data = [
    ('teacher_bsd1', 'Ahmad Dani', 'BSD', '#FF5733', '081234567891'),
    ('teacher_bintaro1', 'Siti Aminah', 'Bintaro', '#33FF57', '081234567892'),
    ('teacher_bandung1', 'Budi Santoso', 'Bandung', '#3357FF', '081234567893'),
    ('teacher_bandung2', 'Cici Paramida', 'Bandung', '#F3FF33', '081234567894'),
    ('teacher_surabaya1', 'Dedi Cahyadi', 'Surabaya', '#FF33F3', '081234567895'),
    ('teacher_surabaya2', 'Eliana Wijaya', 'Surabaya', '#33FFF0', '081234567896'),
    ('teacher_jogja1', 'Fajar Pratama', 'Yogyakarta', '#FFAF33', '081234567897'),
    ('teacher_medan1', 'Gita Gutawa', 'Medan', '#AF33FF', '081234567898'),
    ('teacher_makassar1', 'Hadi Wijaya', 'Makassar', '#33FFAF', '081234567899'),
    ('teacher_semarang1', 'Indah Permata', 'Semarang', '#E133FF', '081234567800'),
]

for username, nama_lengkap, branch, warna, no_wa in teachers_data:
    user, created = CustomUser.objects.get_or_create(
        username=username,
        defaults={
            'email': f'{username}@educourse.id',
            'nama_lengkap': nama_lengkap,
            'role': 'teacher',
            'branch': branch,
            'warna_kalender': warna,
            'no_wa': no_wa,
            'is_active': True
        }
    )
    if created:
        user.set_password('teacherpassword')
        user.save()
        print(f"Created teacher: {username}")
    else:
        print(f"Teacher already exists: {username}")

# Let's also create some dummy schedules for these teachers to make the grid look beautiful
# For Thursday, June 11, 2026 (hari='Kamis')
kamis_schedules = [
    ('teacher_bsd1', 'Robotics Basic', '08:00', '10:00', 'Educourse BSD', 'offline'),
    ('teacher_bintaro1', 'Coding Kids', '09:00', '11:00', 'Educourse Bintaro', 'offline'),
    ('teacher_bandung1', 'Scratch Jr', '10:00', '12:00', 'Educourse Bandung', 'offline'),
    ('teacher_bandung2', 'Web Development', '13:00', '15:00', 'Educourse Bandung', 'online'),
    ('teacher_surabaya1', 'Python Advanced', '14:00', '16:00', 'Educourse Surabaya', 'offline'),
    ('teacher_surabaya2', 'Game Dev Unity', '08:30', '10:30', 'Educourse Surabaya', 'online'),
    ('teacher_jogja1', 'AI for Kids', '11:00', '13:00', 'Educourse Yogyakarta', 'offline'),
    ('teacher_medan1', 'Design thinking', '09:00', '11:00', 'Educourse Medan', 'offline'),
    ('teacher_makassar1', 'Arduino IoT', '15:00', '17:00', 'Educourse Makassar', 'offline'),
    ('teacher_semarang1', 'STEM Project', '10:30', '12:30', 'Educourse Semarang', 'offline'),
]

for username, nama_kelas, jam_mulai_str, jam_selesai_str, sekolah_nama, mode in kamis_schedules:
    try:
        guru = CustomUser.objects.get(username=username)
        sekolah = Sekolah.objects.get(nama=sekolah_nama)
        
        jam_mulai = datetime.datetime.strptime(jam_mulai_str, '%H:%M').time()
        jam_selesai = datetime.datetime.strptime(jam_selesai_str, '%H:%M').time()
        
        JadwalKelas.objects.get_or_create(
            guru=guru,
            sekolah=sekolah,
            nama_kelas=nama_kelas,
            hari='Kamis',
            jam_mulai=jam_mulai,
            jam_selesai=jam_selesai,
            defaults={
                'mode': mode,
                'tipe': 'regular',
                'kegiatan': 'mengajar',
                'aktif': True,
                'tipe_repeat': 'weekly',
            }
        )
        print(f"Created schedule: {nama_kelas} for {username}")
    except Exception as e:
        print(f"Error creating schedule for {username}: {e}")

print("Seeding completed successfully!")
