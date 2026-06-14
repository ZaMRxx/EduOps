from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
import datetime
from accounts.models import CustomUser
from scheduling.models import Sekolah, JadwalKelas, RequestJadwal

@login_required
def dashboard_view(request):
    user = request.user
    role = user.role
    from django.utils import timezone
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
    q_repeatable = Q(
        tipe_repeat='weekly',
        hari=hari_ini_nama
    )
    q_repeatable &= (Q(tanggal_mulai_efektif__isnull=True) | Q(tanggal_mulai_efektif__lte=today_date))
    q_repeatable &= (Q(tanggal_selesai__isnull=True) | Q(tanggal_selesai__gte=today_date))
    q_one_time = Q(
        tipe_repeat='one_time',
        tanggal_spesifik=today_date
    )
    jadwal_hari_ini_base = JadwalKelas.objects.filter(
        Q(aktif=True) & (q_repeatable | q_one_time)
    )
    stats = []
    todo_list = []
    pending_requests = []
    search_query = request.GET.get('q', '').strip()
    
    if user.is_superuser or role in ['admin_op', 'admin_hr']:
        total_guru = CustomUser.objects.filter(role='teacher').count()
        total_sekolah = Sekolah.objects.count()
        total_jadwal = JadwalKelas.objects.filter(aktif=True).count()
        total_request_pending = RequestJadwal.objects.filter(status='pending').count()
        
        stats = [
            {'title': 'Total Guru (Teacher)', 'value': total_guru, 'icon': 'bi-people-fill', 'bg_class': 'bg-primary-subtle text-primary', 'url_name': 'user_list'},
            {'title': 'Total Sekolah / Mitra', 'value': total_sekolah, 'icon': 'bi-building', 'bg_class': 'bg-success-subtle text-success', 'url_name': 'sekolah_list'},
            {'title': 'Total Jadwal Aktif', 'value': total_jadwal, 'icon': 'bi-calendar-week', 'bg_class': 'bg-info-subtle text-info', 'url_name': 'jadwal_list'},
            {'title': 'Request Pending', 'value': total_request_pending, 'icon': 'bi-envelope-exclamation', 'bg_class': 'bg-warning-subtle text-warning', 'url_name': 'request_list'}
        ]
        todo_list = jadwal_hari_ini_base.order_by('jam_mulai')
        pending_requests = RequestJadwal.objects.filter(status='pending').order_by('-dibuat_at')[:5]
        
    elif role == 'admin_branch':
        branch_name = user.branch or 'BSD'
        total_guru = CustomUser.objects.filter(role='teacher', branch=branch_name).count()
        total_sekolah = Sekolah.objects.filter(branch=branch_name).count()
        total_jadwal = JadwalKelas.objects.filter(
            Q(aktif=True) & (Q(sekolah__branch=branch_name) | Q(guru__branch=branch_name))
        ).distinct().count()
        total_request_pending = RequestJadwal.objects.filter(status='pending', pengaju__branch=branch_name).count()
        
        stats = [
            {'title': f'Guru Cabang ({branch_name})', 'value': total_guru, 'icon': 'bi-people-fill', 'bg_class': 'bg-primary-subtle text-primary', 'url_name': 'schedule_view'},
            {'title': 'Sekolah Cabang', 'value': total_sekolah, 'icon': 'bi-building', 'bg_class': 'bg-success-subtle text-success', 'url_name': 'sekolah_list'},
            {'title': 'Jadwal Aktif Cabang', 'value': total_jadwal, 'icon': 'bi-calendar-week', 'bg_class': 'bg-info-subtle text-info', 'url_name': 'jadwal_list'},
            {'title': 'Request Pending Cabang', 'value': total_request_pending, 'icon': 'bi-envelope-exclamation', 'bg_class': 'bg-warning-subtle text-warning', 'url_name': 'request_list'}
        ]
        todo_list = jadwal_hari_ini_base.filter(
            Q(sekolah__branch=branch_name) | Q(guru__branch=branch_name)
        ).distinct().order_by('jam_mulai')
        pending_requests = RequestJadwal.objects.filter(
            status='pending', 
            pengaju__branch=branch_name
        ).order_by('-dibuat_at')[:5]
        
    elif role == 'teacher':
        total_jadwal = JadwalKelas.objects.filter(aktif=True, guru=user).count()
        jadwal_hari_ini_count = jadwal_hari_ini_base.filter(guru=user).count()
        total_request_saya = RequestJadwal.objects.filter(pengaju=user).count()
        request_pending_saya = RequestJadwal.objects.filter(pengaju=user, status='pending').count()
        
        stats = [
            {'title': 'Jadwal Hari Ini', 'value': jadwal_hari_ini_count, 'icon': 'bi-calendar2-check-fill', 'bg_class': 'bg-primary-subtle text-primary', 'url_name': 'schedule_view'},
            {'title': 'Total Jadwal Mingguan', 'value': total_jadwal, 'icon': 'bi-calendar-week', 'bg_class': 'bg-success-subtle text-success', 'url_name': 'schedule_view'},
            {'title': 'Total Request Saya', 'value': total_request_saya, 'icon': 'bi-envelope-paper', 'bg_class': 'bg-info-subtle text-info', 'url_name': 'request_list'},
            {'title': 'Request Pending Saya', 'value': request_pending_saya, 'icon': 'bi-hourglass-split', 'bg_class': 'bg-warning-subtle text-warning', 'url_name': 'request_list'}
        ]
        todo_list = jadwal_hari_ini_base.filter(guru=user).order_by('jam_mulai')
        pending_requests = RequestJadwal.objects.filter(pengaju=user).order_by('-dibuat_at')[:5]

    if search_query:
        todo_list = todo_list.filter(
            Q(nama_kelas__icontains=search_query) |
            Q(guru__nama_lengkap__icontains=search_query) |
            Q(guru__username__icontains=search_query) |
            Q(sekolah__nama__icontains=search_query) |
            Q(sekolah__branch__icontains=search_query)
        )

    todo_list = todo_list.select_related('guru', 'sekolah')
    paginator = Paginator(todo_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'stats': stats,
        'todo_list': page_obj,
        'page_obj': page_obj,
        'pending_requests': pending_requests,
        'today_date': today_date,
        'hari_ini_nama': hari_ini_nama,
        'role': role,
        'search_query': search_query,
    }
    
    return render(request, 'dashboard/dashboard.html', context)
