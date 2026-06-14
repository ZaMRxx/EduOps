import os
import base64
import datetime
import cv2
import numpy as np

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db.models import Q
from django.conf import settings
from django.core.paginator import Paginator
from scheduling.models import JadwalKelas
from accounts.models import CustomUser
from accounts.decorators import role_required
from .models import Absensi, LogAktivitas
from .utils import catat_log

@login_required
def absensi_form(request):
    user = request.user
    hari_map = {
        'Monday': 'Senin',
        'Tuesday': 'Selasa',
        'Wednesday': 'Rabu',
        'Thursday': 'Kamis',
        'Friday': 'Jumat',
        'Saturday': 'Sabtu',
        'Sunday': 'Minggu'
    }
    today_dt = timezone.localtime(timezone.now())
    today_date = today_dt.date()
    hari_ini_nama = hari_map.get(today_dt.strftime('%A'), 'Senin')
    if user.role == 'teacher':
        schedules = JadwalKelas.objects.filter(guru=user, aktif=True)
    else:
        schedules = JadwalKelas.objects.filter(aktif=True)
    q_repeatable = Q(tipe_repeat='weekly', hari=hari_ini_nama)
    q_repeatable &= (Q(tanggal_mulai_efektif__isnull=True) | Q(tanggal_mulai_efektif__lte=today_date))
    q_repeatable &= (Q(tanggal_selesai__isnull=True) | Q(tanggal_selesai__gte=today_date))
    q_one_time = Q(tipe_repeat='one_time', tanggal_spesifik=today_date)
    
    schedules = schedules.filter(q_repeatable | q_one_time).order_by('jam_mulai')
    selected_jadwal_id = request.GET.get('jadwal_id')
    selected_jadwal = None
    if selected_jadwal_id:
        try:
            selected_jadwal = JadwalKelas.objects.get(id=selected_jadwal_id)
            if user.role == 'teacher' and selected_jadwal.guru != user:
                selected_jadwal = None
        except JadwalKelas.DoesNotExist:
            pass

    if request.method == 'POST':
        jadwal_id = request.POST.get('jadwal_id')
        image_data = request.POST.get('image_data')
        
        if not jadwal_id:
            messages.error(request, "Silakan pilih jadwal kelas terlebih dahulu.")
            return redirect(f"/attendance/absen/?jadwal_id={selected_jadwal_id or ''}")
            
        if not image_data:
            messages.error(request, "Foto absensi belum diambil. Silakan izinkan kamera dan ambil foto.")
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
        jadwal = get_object_or_404(JadwalKelas, id=jadwal_id)

        if user.role == 'teacher' and jadwal.guru != user:
            messages.error(request, "Anda tidak memiliki hak untuk melakukan absensi pada jadwal guru lain.")
            return redirect('absensi_form')

        current_time = timezone.localtime(timezone.now()).time()
        class_start = datetime.datetime.combine(today_date, jadwal.jam_mulai)
        earliest_allowed = class_start - datetime.timedelta(hours=1)
        late_limit = class_start + datetime.timedelta(minutes=15)
        current_simulated_dt = datetime.datetime.combine(today_date, current_time)

        if current_simulated_dt <= earliest_allowed:
            messages.error(
                request,
                f"Absensi belum dibuka. Anda baru bisa absen kurang dari 1 jam sebelum kelas dimulai (setelah {earliest_allowed.strftime('%H:%M')} WIB)."
            )
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
        duplicate_exists = Absensi.objects.filter(
            guru=user,
            jadwal=jadwal,
            tanggal=today_date
        ).exists()
        
        if duplicate_exists:
            messages.warning(request, f"Anda sudah melakukan absensi untuk kelas {jadwal.nama_kelas} hari ini.")
            return redirect('riwayat_absensi')
        try:
            if ';base64,' in image_data:
                format_header, imgstr = image_data.split(';base64,')
            else:
                imgstr = image_data
            img_bytes = base64.b64decode(imgstr)
        except Exception:
            messages.error(request, "Format data foto tidak valid.")
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            messages.error(request, "Gagal memproses foto. Pastikan kamera Anda bersih dan bekerja dengan baik.")
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
        cascade_path = os.path.join(cv2.data.haarcascades, 'haarcascade_frontalface_default.xml')
        if not os.path.exists(cascade_path):
            messages.error(request, "Konfigurasi sistem OpenCV XML tidak ditemukan.")
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
            
        face_cascade = cv2.CascadeClassifier(cascade_path)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(50, 50)
        )
        if len(faces) == 0:
            messages.error(request, "Verifikasi wajah gagal. Wajah Anda tidak terdeteksi. Pastikan pencahayaan cukup dan wajah menghadap kamera.")
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
        if len(faces) > 1:
            messages.error(request, "Absensi tidak valid. Sistem mendeteksi lebih dari satu wajah di kamera.")
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + h), (29, 158, 117), 3)
        ret, buf = cv2.imencode('.jpg', img)
        if not ret:
            messages.error(request, "Gagal memproses hasil foto berkotak hijau.")
            return redirect(f"/attendance/absen/?jadwal_id={jadwal_id}")
            
        annotated_bytes = buf.tobytes()
        filename = f"absen_{user.username}_{timezone.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        foto_file = ContentFile(annotated_bytes, name=filename)
        
        if current_simulated_dt > late_limit:
            status = 'Terlambat'
        else:
            status = 'Hadir'
        absen = Absensi.objects.create(
            guru=user,
            jadwal=jadwal,
            tanggal=today_date,
            waktu_absen=current_time,
            status=status,
            foto=foto_file,
            wajah_terdeteksi=True
        )
        catat_log(
            user=user,
            aksi='absen_masuk',
            detail=f"Melakukan absensi masuk pada kelas '{jadwal.nama_kelas}'. Jam kelas: {jadwal.jam_mulai.strftime('%H:%M')}. Absen masuk: {current_time.strftime('%H:%M')} (Status: {status})"
        )
        
        messages.success(request, f"Absensi Sukses! Anda tercatat {status} untuk kelas {jadwal.nama_kelas}.")
        return redirect('riwayat_absensi')
        
    context = {
        'schedules': schedules,
        'selected_jadwal': selected_jadwal,
        'today_date': today_date,
        'hari_ini_nama': hari_ini_nama,
    }
    return render(request, 'attendance/absensi_form.html', context)

@login_required
def riwayat_absensi(request):
    user = request.user
    role = user.role
    if role == 'teacher':
        queryset = Absensi.objects.filter(guru=user)
    elif role == 'admin_branch':
        queryset = Absensi.objects.filter(guru__branch=user.branch)
    else:
        queryset = Absensi.objects.all()
    search_query = request.GET.get('search', '').strip()
    status_filter = request.GET.get('status', '').strip()
    tgl_mulai = request.GET.get('tanggal_mulai', '').strip()
    tgl_selesai = request.GET.get('tanggal_selesai', '').strip()
    
    if search_query:
        queryset = queryset.filter(
            Q(guru__nama_lengkap__icontains=search_query) |
            Q(guru__username__icontains=search_query) |
            Q(jadwal__nama_kelas__icontains=search_query)
        )
        
    if status_filter in ['Hadir', 'Terlambat']:
        queryset = queryset.filter(status=status_filter)
        
    if tgl_mulai:
        try:
            queryset = queryset.filter(tanggal__gte=tgl_mulai)
        except ValueError:
            pass
            
    if tgl_selesai:
        try:
            queryset = queryset.filter(tanggal__lte=tgl_selesai)
        except ValueError:
            pass
            
    queryset = queryset.order_by('-tanggal', '-waktu_absen')
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'riwayat_list': page_obj,
        'page_obj': page_obj,
        'search': search_query,
        'status_filter': status_filter,
        'tanggal_mulai': tgl_mulai,
        'tanggal_selesai': tgl_selesai,
        'role': role,
    }
    return render(request, 'attendance/riwayat.html', context)

@login_required
def aktivitas_logs(request):
    user = request.user
    role = user.role
    if not user.is_superuser and role not in ['admin_op', 'admin_hr']:
        messages.error(request, "Anda tidak memiliki hak akses untuk melihat Log Aktivitas Sistem.")
        return redirect('dashboard')
        
    queryset = LogAktivitas.objects.all()
    search_query = request.GET.get('search', '').strip()
    aksi_filter = request.GET.get('aksi', '').strip()
    
    if search_query:
        queryset = queryset.filter(
            Q(user__username__icontains=search_query) |
            Q(user__nama_lengkap__icontains=search_query) |
            Q(detail__icontains=search_query)
        )
        
    if aksi_filter:
        queryset = queryset.filter(aksi=aksi_filter)
        
    queryset = queryset.order_by('-timestamp')
    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    available_actions = LogAktivitas.objects.values_list('aksi', flat=True).distinct().order_by('aksi')
    
    context = {
        'logs_list': page_obj,
        'page_obj': page_obj,
        'search': search_query,
        'aksi_filter': aksi_filter,
        'available_actions': available_actions,
    }
    return render(request, 'attendance/logs.html', context)
@login_required
@role_required(['admin_op', 'admin_branch', 'admin_hr'])
def absensi_delete(request, pk):
    absen = get_object_or_404(Absensi, pk=pk)
    if request.user.role == 'admin_branch' and absen.guru.branch != request.user.branch:
        messages.error(request, "Anda tidak memiliki hak akses untuk menghapus absensi dari cabang lain.")
        return redirect('riwayat_absensi')
        
    if request.method == 'POST':
        guru_name = absen.guru.nama_lengkap or absen.guru.username
        kelas_name = absen.jadwal.nama_kelas if absen.jadwal else "Tanpa Kelas"
        tanggal_absen = absen.tanggal.strftime('%d-%m-%Y')
        if absen.foto:
            try:
                if os.path.isfile(absen.foto.path):
                    os.remove(absen.foto.path)
            except Exception:
                pass
                
        absen.delete()
        catat_log(
            user=request.user,
            aksi='hapus_absensi',
            detail=f"Menghapus absensi guru {guru_name} pada kelas {kelas_name} tanggal {tanggal_absen}"
        )
        
        messages.success(request, f"Data absensi '{guru_name}' pada kelas '{kelas_name}' tanggal {tanggal_absen} berhasil dihapus.")
        return redirect('riwayat_absensi')
        
    return redirect('riwayat_absensi')
