from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import CustomUser
from .forms import TeacherRegistrationForm, AdminUserCreationForm, AdminUserUpdateForm, ProfileUpdateForm, EduOpsPasswordChangeForm
from django.core.paginator import Paginator
from .decorators import role_required
try:
    from attendance.utils import catat_log
except ImportError:
    def catat_log(user, aksi, detail=''):
        pass
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        email_input = request.POST.get('email', '').strip().lower()
        password_input = request.POST.get('password')
        user = None
        account = CustomUser.objects.filter(email__iexact=email_input, is_active=True).first()
        if account:
            user = authenticate(request, username=account.username, password=password_input)
        
        if user is not None:
            login(request, user)
            catat_log(user, 'login', 'Berhasil login ke sistem')
            messages.success(request, f"Selamat datang kembali, {user.nama_lengkap or user.username}!")
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, "Email atau password salah!")
    return render(request, 'accounts/login.html', {'hide_sidebar': True})
@login_required
def logout_view(request):
    user = request.user
    catat_log(user, 'logout', 'Keluar dari sistem')
    logout(request)
    messages.info(request, "Anda telah berhasil keluar dari sistem.")
    return redirect('login')
def register_teacher(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            catat_log(user, 'register_teacher', f'Guru {user.username} berhasil mendaftar secara mandiri.')
            messages.success(request, f"Akun Guru '{user.username}' berhasil didaftarkan! Silakan masuk.")
            return redirect('login')
        else:
            messages.error(request, "Gagal mendaftar. Silakan periksa kembali data Anda.")
    else:
        form = TeacherRegistrationForm()
        
    context = {
        'form': form,
        'hide_sidebar': True
    }
    return render(request, 'accounts/register.html', context)
@login_required
@role_required(['admin_op'])
def admin_create_user(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            catat_log(request.user, 'admin_create_user', f'Admin membuat akun baru: {user.username} dengan peran {user.get_role_display()}')
            messages.success(request, f"Akun '{user.username}' dengan peran '{user.get_role_display()}' berhasil dibuat.")
            return redirect('dashboard')
        else:
            messages.error(request, "Gagal membuat akun. Silakan periksa kembali data input.")
    else:
        form = AdminUserCreationForm()
        
    context = {
        'form': form,
        'title': 'Buat Akun Pengguna Baru'
    }
    return render(request, 'accounts/admin_create_user.html', context)
@login_required
@role_required(['admin_op', 'admin_hr'])
def user_list(request):
    users_qs = CustomUser.objects.all().order_by('username')
    q = request.GET.get('q', '')
    if q:
        users_qs = users_qs.filter(
            Q(username__icontains=q) |
            Q(nama_lengkap__icontains=q) |
            Q(email__icontains=q) |
            Q(branch__icontains=q)
        )
    paginator = Paginator(users_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
        
    context = {
        'users': page_obj,
        'page_obj': page_obj,
        'search_query': q
    }
    return render(request, 'accounts/user_list.html', context)
@login_required
@role_required(['admin_op'])
def admin_edit_user(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)
    if target_user.is_superuser and not request.user.is_superuser:
        messages.error(request, "Akun superadmin hanya bisa diubah oleh superadmin.")
        return redirect('user_list')
    
    if request.method == 'POST':
        form = AdminUserUpdateForm(request.POST, instance=target_user)
        if form.is_valid():
            form.save()
            catat_log(request.user, 'edit_user', f'Admin mengedit akun user: {target_user.username}')
            messages.success(request, f"Akun '{target_user.username}' berhasil diperbarui.")
            return redirect('user_list')
        else:
            messages.error(request, "Gagal memperbarui akun. Silakan periksa kembali data input.")
    else:
        form = AdminUserUpdateForm(instance=target_user)
        
    context = {
        'form': form,
        'target_user': target_user,
        'title': f"Edit Akun: {target_user.username}"
    }
    return render(request, 'accounts/admin_edit_user.html', context)
@login_required
@role_required(['admin_op'])
def admin_delete_user(request, pk):
    target_user = get_object_or_404(CustomUser, pk=pk)
    if target_user == request.user:
        messages.error(request, "Anda tidak dapat menghapus akun Anda sendiri yang sedang digunakan!")
        return redirect('user_list')
    if target_user.is_superuser:
        messages.error(request, "Akun superadmin tidak boleh dihapus dari panel operasional.")
        return redirect('user_list')
        
    if request.method == 'POST':
        username = target_user.username
        target_user.delete()
        catat_log(request.user, 'hapus_user', f'Admin menghapus akun user: {username}')
        messages.success(request, f"Akun '{username}' berhasil dihapus dari sistem.")
        return redirect('user_list')
        
    return redirect('user_list')

@login_required
def profile_edit(request):
    profile_form = ProfileUpdateForm(instance=request.user)
    password_form = EduOpsPasswordChangeForm(request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'profile':
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                catat_log(request.user, 'edit_profile', 'Memperbarui profil pribadi')
                messages.success(request, "Profil berhasil diperbarui.")
                return redirect('profile_edit')
            messages.error(request, "Gagal memperbarui profil. Periksa kembali data Anda.")

        elif action == 'password':
            password_form = EduOpsPasswordChangeForm(request.user, request.POST)
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                catat_log(request.user, 'reset_password', 'Mengubah password pribadi')
                messages.success(request, "Password berhasil diubah.")
                return redirect('profile_edit')
            messages.error(request, "Gagal mengubah password. Periksa kembali input password.")

    return render(request, 'accounts/profile_edit.html', {
        'profile_form': profile_form,
        'password_form': password_form,
    })
