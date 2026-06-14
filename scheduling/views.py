from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from accounts.models import CustomUser
from accounts.decorators import role_required
from .models import Sekolah, JadwalKelas, RequestJadwal
from .forms import JadwalKelasForm, RequestJadwalForm, SekolahForm
from django.utils import timezone
from attendance.models import Absensi
import datetime
import json
from decimal import Decimal
from django.core.paginator import Paginator
try:
    from attendance.utils import catat_log
except ImportError:
    def catat_log(user, aksi, detail=''):
        pass
@login_required
def schedule_view(request):
    hide_sidebar = True
    
    DAY_MAPPING = {
        0: 'Senin',
        1: 'Selasa',
        2: 'Rabu',
        3: 'Kamis',
        4: 'Jumat',
        5: 'Sabtu',
        6: 'Minggu'
    }
    
    today_date = timezone.localdate()
    date_str = request.GET.get('tanggal')
    if date_str:
        try:
            selected_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            selected_date = today_date
    else:
        selected_date = today_date
    start_of_week = selected_date - datetime.timedelta(days=selected_date.weekday())
    active_day = request.GET.get('hari', DAY_MAPPING[selected_date.weekday()])
    
    try:
        active_day_index = list(DAY_MAPPING.values()).index(active_day)
    except ValueError:
        active_day_index = selected_date.weekday()
        active_day = DAY_MAPPING[active_day_index]
        
    active_date = start_of_week + datetime.timedelta(days=active_day_index)
    day_tabs = []
    for i in range(7):
        day_date = start_of_week + datetime.timedelta(days=i)
        day_name = DAY_MAPPING[i]
        day_tabs.append({
            'nama': day_name,
            'tanggal': day_date.strftime('%Y-%m-%d'),
            'is_active': (active_day == day_name)
        })

    branch_filter = request.GET.get('branch', '')
    tipe_filter = request.GET.get('tipe', '')
    search_query = request.GET.get('search_teacher', '')
    
    teachers = CustomUser.objects.filter(role='teacher')
    
    if request.user.role == 'teacher':
        teachers = teachers.filter(id=request.user.id)
    elif request.user.role == 'admin_branch':
        teachers = teachers.filter(branch=request.user.branch)
    
    if branch_filter:
        teachers = teachers.filter(branch=branch_filter)
    if search_query:
        teachers = teachers.filter(
            Q(nama_lengkap__icontains=search_query) |
            Q(username__icontains=search_query) |
            Q(jadwal__nama_kelas__icontains=search_query) |
            Q(jadwal__sekolah__nama__icontains=search_query) |
            Q(jadwal__sekolah__branch__icontains=search_query)
        ).distinct()
        
    teachers = teachers.order_by('nama_lengkap')
    q_repeatable = Q(
        tipe_repeat='weekly',
        hari=active_day
    )
    q_repeatable &= (Q(tanggal_mulai_efektif__isnull=True) | Q(tanggal_mulai_efektif__lte=active_date))
    q_repeatable &= (Q(tanggal_selesai__isnull=True) | Q(tanggal_selesai__gte=active_date))
    
    q_one_time = Q(
        tipe_repeat='one_time',
        tanggal_spesifik=active_date
    )
    
    schedules_qs = JadwalKelas.objects.filter(
        Q(aktif=True) & (q_repeatable | q_one_time)
    )
    
    if tipe_filter:
        schedules_qs = schedules_qs.filter(tipe=tipe_filter)

    if search_query:
        schedules_qs = schedules_qs.filter(
            Q(guru__nama_lengkap__icontains=search_query) |
            Q(guru__username__icontains=search_query) |
            Q(nama_kelas__icontains=search_query) |
            Q(sekolah__nama__icontains=search_query) |
            Q(sekolah__branch__icontains=search_query)
        )

    attended_schedule_ids = set(
        Absensi.objects.filter(
            tanggal=active_date,
            jadwal_id__in=schedules_qs.values_list('id', flat=True)
        ).values_list('jadwal_id', flat=True)
    )

    all_tipes_qs = JadwalKelas.objects.filter(aktif=True)
    if request.user.role == 'teacher':
        all_tipes_qs = all_tipes_qs.filter(guru=request.user)
    elif request.user.role == 'admin_branch':
        all_tipes_qs = all_tipes_qs.filter(Q(guru__branch=request.user.branch) | Q(sekolah__branch=request.user.branch))
    if branch_filter:
        all_tipes_qs = all_tipes_qs.filter(Q(guru__branch=branch_filter) | Q(sekolah__branch=branch_filter))

    all_tipes = list(
        all_tipes_qs.exclude(tipe__isnull=True)
        .exclude(tipe='')
        .values_list('tipe', flat=True)
        .distinct()
        .order_by('tipe')
    )
        
    jadwal_data = {}
    for teacher in teachers:
        teacher_schedules = schedules_qs.filter(guru=teacher)
        
        schedules_list = []
        for s in teacher_schedules:
            h1, m1 = s.jam_mulai.hour, s.jam_mulai.minute
            h2, m2 = s.jam_selesai.hour, s.jam_selesai.minute
            
            menit_dari_awal = (h1 - 7) * 60 + m1
            durasi_menit = (h2 - 7) * 60 + m2 - menit_dari_awal
            
            top_px = int((menit_dari_awal / 60) * 60)
            height_px = int((durasi_menit / 60) * 60)
            
            schedules_list.append({
                'id': s.id,
                'nama_kelas': s.nama_kelas,
                'jam_mulai': s.jam_mulai.strftime('%H:%M'),
                'jam_selesai': s.jam_selesai.strftime('%H:%M'),
                'mode': s.mode,
                'tipe': s.tipe,
                'kegiatan': s.kegiatan,
                'tipe_repeat': s.tipe_repeat,
                'tanggal_spesifik': s.tanggal_spesifik.strftime('%Y-%m-%d') if s.tanggal_spesifik else '',
                'sekolah': s.sekolah.nama if s.sekolah else 'Tanpa Sekolah',
                'branch': s.sekolah.branch if s.sekolah else teacher.branch or 'BSD',
                'top_px': top_px,
                'height_px': height_px,
                'sudah_absen': s.id in attended_schedule_ids,
            })
            
        jadwal_data[str(teacher.id)] = {
            'nama': teacher.nama_lengkap or teacher.username,
            'warna': teacher.warna_kalender,
            'jadwal': schedules_list
        }
    sekolah_branches = list(Sekolah.objects.values_list('branch', flat=True).distinct())
    user_branches = list(CustomUser.objects.exclude(branch__isnull=True).exclude(branch='').values_list('branch', flat=True).distinct())
    all_branches = sorted(list(set(sekolah_branches + user_branches)))
    if not all_branches:
        all_branches = ['BSD', 'Bintaro', 'Gading Serpong', 'Ciputat']
        
    jadwal_json = json.dumps(jadwal_data)
    
    context = {
        'hide_sidebar': hide_sidebar,
        'active_day': active_day,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'active_date': active_date.strftime('%Y-%m-%d'),
        'today_date': today_date.strftime('%Y-%m-%d'),
        'today_day': DAY_MAPPING[today_date.weekday()],
        'branch_filter': branch_filter,
        'tipe_filter': tipe_filter,
        'search_query': search_query,
        'all_branches': all_branches,
        'all_tipes': all_tipes,
        'jadwal_json': jadwal_json,
        'teachers': teachers,
        'day_tabs': day_tabs,
    }
    
    return render(request, 'scheduling/schedule_view.html', context)
@login_required
@role_required(['admin_op', 'admin_hr', 'admin_branch'])
def jadwal_list(request):
    query = JadwalKelas.objects.all()
    search = request.GET.get('q', '')
    status_filter = request.GET.get('status', 'aktif')
    hari_filter = request.GET.get('hari', '')
    show_all = request.GET.get('show_all') == '1'
    if search:
        query = query.filter(
            Q(nama_kelas__icontains=search) | 
            Q(guru__nama_lengkap__icontains=search) | 
            Q(guru__username__icontains=search) |
            Q(guru__branch__icontains=search) |
            Q(sekolah__nama__icontains=search) |
            Q(sekolah__branch__icontains=search) |
            Q(sekolah__tipe__icontains=search)
        )
    branch_filter = request.GET.get('branch', '')
    if branch_filter:
        query = query.filter(guru__branch=branch_filter)
    tipe_filter = request.GET.get('tipe', '')
    if tipe_filter:
        query = query.filter(tipe=tipe_filter)
    if hari_filter:
        query = query.filter(hari=hari_filter)
    if status_filter == 'aktif':
        query = query.filter(aktif=True)
    elif status_filter == 'nonaktif':
        query = query.filter(aktif=False)
    if request.user.role == 'admin_branch':
        query = query.filter(guru__branch=request.user.branch)
        
    query = query.select_related('guru', 'sekolah').order_by('hari', 'jam_mulai')

    teacher_load_map = {}
    for jadwal in query:
        teacher_id = jadwal.guru_id
        if teacher_id not in teacher_load_map:
            teacher_load_map[teacher_id] = {
                'teacher': jadwal.guru,
                'total_jam_mengajar': Decimal('0.00'),
                'total_load_mengajar': Decimal('0.00'),
                'total_load_perjalanan': Decimal('0.00'),
                'total_load': Decimal('0.00'),
                'jumlah_jadwal': 0,
                'total_pertemuan': 0,
                'total_kunjungan_sekolah': 0,
            }

        teacher_load_map[teacher_id]['total_jam_mengajar'] += jadwal.durasi_jam_mengajar
        teacher_load_map[teacher_id]['total_load_mengajar'] += jadwal.load_mengajar
        teacher_load_map[teacher_id]['total_load_perjalanan'] += jadwal.load_perjalanan
        teacher_load_map[teacher_id]['total_load'] += jadwal.nilai_load
        teacher_load_map[teacher_id]['jumlah_jadwal'] += 1
        teacher_load_map[teacher_id]['total_pertemuan'] += jadwal.pertemuan_per_minggu
        teacher_load_map[teacher_id]['total_kunjungan_sekolah'] += jadwal.kali_ke_sekolah_per_minggu

    teacher_loads = sorted(
        teacher_load_map.values(),
        key=lambda item: item['total_load'],
        reverse=True
    )
    paginator = Paginator(query, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    sekolah_branches = list(Sekolah.objects.values_list('branch', flat=True).distinct())
    user_branches = list(CustomUser.objects.exclude(branch__isnull=True).exclude(branch='').values_list('branch', flat=True).distinct())
    all_branches = sorted(list(set(sekolah_branches + user_branches)))
    if not all_branches:
        all_branches = ['BSD', 'Bintaro', 'Gading Serpong', 'Ciputat']
    all_tipes = list(JadwalKelas.objects.values_list('tipe', flat=True).distinct().order_by('tipe'))
    
    context = {
        'jadwal_list': page_obj,
        'page_obj': page_obj,
        'search_query': search,
        'branch_filter': branch_filter,
        'all_branches': all_branches,
        'tipe_filter': tipe_filter,
        'all_tipes': all_tipes,
        'teacher_loads': teacher_loads,
        'status_filter': status_filter,
        'hari_filter': hari_filter,
        'hari_choices': JadwalKelas.HARI_CHOICES,
        'show_all': show_all,
    }
    return render(request, 'scheduling/jadwal_list.html', context)
@login_required
@role_required(['admin_op'])
def jadwal_add(request):
    if request.method == 'POST':
        form = JadwalKelasForm(request.POST, user=request.user)
        if form.is_valid():
            jadwal = form.save()
            catat_log(request.user, 'tambah_jadwal', f'Berhasil menambahkan jadwal {jadwal.nama_kelas}')
            
            messages.success(request, f"Jadwal '{jadwal.nama_kelas}' berhasil ditambahkan.")
            return redirect('jadwal_list')
        else:
            messages.error(request, "Gagal menambahkan jadwal. Periksa kembali input Anda.")
    else:
        form = JadwalKelasForm(user=request.user)
        
    context = {
        'form': form,
        'title': 'Tambah Jadwal Kelas'
    }
    return render(request, 'scheduling/jadwal_form.html', context)
@login_required
@role_required(['admin_op', 'admin_branch'])
def jadwal_edit(request, pk):
    jadwal = get_object_or_404(JadwalKelas, pk=pk)
    if request.user.role == 'admin_branch' and jadwal.guru.branch != request.user.branch:
        messages.error(request, "Anda tidak memiliki wewenang untuk mengedit jadwal di cabang lain!")
        return redirect('jadwal_list')
        
    if request.method == 'POST':
        form = JadwalKelasForm(request.POST, instance=jadwal, user=request.user)
        if form.is_valid():
            form.save()
            catat_log(request.user, 'edit_jadwal', f'Berhasil mengubah jadwal ID {jadwal.id} ({jadwal.nama_kelas})')
            
            messages.success(request, f"Jadwal '{jadwal.nama_kelas}' berhasil diperbarui.")
            return redirect('jadwal_list')
        else:
            messages.error(request, "Gagal mengedit jadwal. Periksa kembali input Anda.")
    else:
        form = JadwalKelasForm(instance=jadwal, user=request.user)
        
    context = {
        'form': form,
        'title': 'Edit Jadwal Kelas',
        'is_edit': True,
        'jadwal': jadwal
    }
    return render(request, 'scheduling/jadwal_form.html', context)
@login_required
@role_required(['admin_op', 'admin_branch'])
def jadwal_delete(request, pk):
    jadwal = get_object_or_404(JadwalKelas, pk=pk)
    if request.user.role == 'admin_branch' and jadwal.guru.branch != request.user.branch:
        messages.error(request, "Anda tidak memiliki wewenang untuk menghapus jadwal di cabang lain!")
        return redirect('jadwal_list')
        
    if request.method == 'POST':
        nama_kelas = jadwal.nama_kelas
        jadwal.delete()
        catat_log(request.user, 'hapus_jadwal', f'Menghapus jadwal kelas: {nama_kelas}')
        
        messages.success(request, f"Jadwal kelas '{nama_kelas}' berhasil dihapus.")
        return redirect('jadwal_list')
    return redirect('jadwal_list')
@login_required
def request_list(request):
    user = request.user
    role = user.role
    if user.is_superuser or role in ['admin_op', 'admin_hr']:
        requests_qs = RequestJadwal.objects.all().order_by('-dibuat_at')
    elif role == 'admin_branch':
        requests_qs = RequestJadwal.objects.filter(pengaju__branch=user.branch).order_by('-dibuat_at')
    else:
        requests_qs = RequestJadwal.objects.filter(pengaju=user).order_by('-dibuat_at')
        
    form = RequestJadwalForm(user=user)
    if request.method == 'POST':
        if role not in ['teacher', 'admin_branch']:
            messages.error(request, "Anda tidak memiliki wewenang untuk membuat request jadwal baru!")
            return redirect('request_list')
            
        form = RequestJadwalForm(request.POST, user=user)
        if form.is_valid():
            new_req = form.save(commit=False)
            new_req.pengaju = user
            new_req.status = 'pending'
            if role == 'teacher':
                new_req.guru = user
            new_req.save()
            catat_log(user, 'buat_request', f'Berhasil mengajukan request jadwal ID {new_req.id}')
            
            messages.success(request, "Pengajuan jadwal Anda berhasil dikirim dan sedang menunggu keputusan admin operasional.")
            return redirect('request_list')
        else:
            messages.error(request, "Gagal mengajukan request. Periksa kembali input Anda.")
    paginator = Paginator(requests_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
            
    context = {
        'requests': page_obj,
        'page_obj': page_obj,
        'form': form,
        'role': role
    }
    return render(request, 'scheduling/request_list.html', context)
@login_required
@role_required(['admin_op'])
def request_approve(request, pk):
    req = get_object_or_404(RequestJadwal, pk=pk)
    if req.status != 'pending':
        messages.warning(request, f"Pengajuan #{req.id} sudah pernah diproses sebelumnya.")
        return redirect('request_list')
        
    req.status = 'approved'
    req.diproses_oleh = request.user
    req.diproses_at = timezone.now()
    try:
        jadwal = req.apply_to_schedule()
    except Exception as exc:
        messages.error(request, f"Gagal menerapkan request ke jadwal: {exc}")
        return redirect('request_list')
    req.save()
    catat_log(request.user, 'approve_request', f'Menyetujui request ID {req.id} milik {req.pengaju.username}; jadwal ID {jadwal.id}')
    
    messages.success(request, f"Pengajuan #{req.id} dari '{req.pengaju.nama_lengkap or req.pengaju.username}' berhasil disetujui.")
    return redirect('request_list')
@login_required
@role_required(['admin_op'])
def request_reject(request, pk):
    req = get_object_or_404(RequestJadwal, pk=pk)
    if req.status != 'pending':
        messages.warning(request, f"Pengajuan #{req.id} sudah pernah diproses sebelumnya.")
        return redirect('request_list')
        
    req.status = 'rejected'
    req.diproses_oleh = request.user
    req.diproses_at = timezone.now()
    req.save()
    catat_log(request.user, 'reject_request', f'Menolak request ID {req.id} milik {req.pengaju.username}')
    
    messages.success(request, f"Pengajuan #{req.id} dari '{req.pengaju.nama_lengkap or req.pengaju.username}' telah ditolak.")
    return redirect('request_list')
@login_required
def sekolah_list(request):
    sekolah_qs = Sekolah.objects.all().order_by('branch', 'nama')
    q = request.GET.get('q', '')
    if q:
        sekolah_qs = sekolah_qs.filter(
            Q(nama__icontains=q) |
            Q(branch__icontains=q)
        )
    paginator = Paginator(sekolah_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {
        'sekolah_list': page_obj,
        'page_obj': page_obj,
        'search_query': q
    }
    return render(request, 'scheduling/sekolah_list.html', context)
@login_required
@role_required(['admin_op', 'admin_branch', 'admin_hr'])
def sekolah_add(request):
    if request.method == 'POST':
        form = SekolahForm(request.POST)
        if form.is_valid():
            sekolah = form.save()
            catat_log(request.user, 'tambah_sekolah', f'Berhasil menambahkan sekolah/mitra {sekolah.nama}')
            messages.success(request, f"Sekolah/Mitra '{sekolah.nama}' berhasil ditambahkan.")
            return redirect('sekolah_list')
        else:
            messages.error(request, "Gagal menambahkan sekolah/mitra. Periksa kembali input Anda.")
    else:
        form = SekolahForm()
        
    context = {
        'form': form,
        'title': 'Tambah Sekolah / Mitra Baru'
    }
    return render(request, 'scheduling/sekolah_form.html', context)
@login_required
@role_required(['admin_op', 'admin_branch', 'admin_hr'])
def sekolah_edit(request, pk):
    sekolah = get_object_or_404(Sekolah, pk=pk)
    
    if request.method == 'POST':
        form = SekolahForm(request.POST, instance=sekolah)
        if form.is_valid():
            form.save()
            catat_log(request.user, 'edit_sekolah', f'Berhasil mengubah sekolah/mitra ID {sekolah.id} ({sekolah.nama})')
            messages.success(request, f"Data sekolah/mitra '{sekolah.nama}' berhasil diperbarui.")
            return redirect('sekolah_list')
        else:
            messages.error(request, "Gagal mengedit data. Periksa kembali input Anda.")
    else:
        form = SekolahForm(instance=sekolah)
        
    context = {
        'form': form,
        'title': f"Edit Sekolah: {sekolah.nama}",
        'is_edit': True,
        'sekolah': sekolah
    }
    return render(request, 'scheduling/sekolah_form.html', context)
@login_required
@role_required(['admin_op', 'admin_branch', 'admin_hr'])
def sekolah_delete(request, pk):
    sekolah = get_object_or_404(Sekolah, pk=pk)
    
    if request.method == 'POST':
        nama = sekolah.nama
        sekolah.delete()
        catat_log(request.user, 'hapus_sekolah', f'Menghapus sekolah/mitra: {nama}')
        messages.success(request, f"Sekolah/Mitra '{nama}' berhasil dihapus.")
        return redirect('sekolah_list')
        
    return redirect('sekolah_list')
