from django import forms
from django.contrib.auth.forms import SetPasswordForm
from .models import CustomUser

class TeacherRegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Password'}),
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Konfirmasi Password'}),
        label="Konfirmasi Password"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'nama_lengkap', 'no_wa', 'branch', 'warna_kalender']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Email'}),
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Lengkap'}),
            'no_wa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nomor WhatsApp'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Cabang (misal: BSD, Bintaro)'}),
            'warna_kalender': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'value': '#1D9E75'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Password dan Konfirmasi Password tidak cocok!")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email ini sudah terdaftar.")
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.role = 'teacher'
        if commit:
            user.save()
        return user

class AdminUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Password'}),
        label="Password"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Konfirmasi Password'}),
        label="Konfirmasi Password"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'nama_lengkap', 'no_wa', 'role', 'branch', 'warna_kalender']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Email'}),
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Lengkap'}),
            'no_wa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nomor WhatsApp'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Cabang'}),
            'warna_kalender': forms.TextInput(attrs={'class': 'form-control', 'type': 'color', 'value': '#1D9E75'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role'].choices = [
            choice for choice in self.fields['role'].choices
            if choice[0] != 'super_admin'
        ]
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Password dan Konfirmasi Password tidak cocok!")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email ini sudah terdaftar.")
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user

class AdminUserUpdateForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Password Baru (Kosongkan jika tidak ingin diubah)'}),
        required=False,
        label="Password Baru"
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Konfirmasi Password Baru'}),
        required=False,
        label="Konfirmasi Password Baru"
    )
    
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'nama_lengkap', 'no_wa', 'role', 'branch', 'warna_kalender', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Email'}),
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Lengkap'}),
            'no_wa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nomor WhatsApp'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Cabang'}),
            'warna_kalender': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self.instance, 'role', None) != 'super_admin':
            self.fields['role'].choices = [
                choice for choice in self.fields['role'].choices
                if choice[0] != 'super_admin'
            ]
        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        
        if password or password_confirm:
            if password != password_confirm:
                raise forms.ValidationError("Password baru dan konfirmasinya tidak cocok!")
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Email ini sudah digunakan akun lain.")
        return email
        
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('password')
        if password:
            user.set_password(password)
        if user.role == 'super_admin':
            user.is_staff = True
            user.is_superuser = True
        if commit:
            user.save()
        return user

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['nama_lengkap', 'email', 'no_wa', 'branch', 'warna_kalender', 'foto_profile']
        widgets = {
            'nama_lengkap': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nama lengkap'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'}),
            'no_wa': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nomor WhatsApp'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Cabang'}),
            'warna_kalender': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
            'foto_profile': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if CustomUser.objects.exclude(pk=self.instance.pk).filter(email__iexact=email).exists():
            raise forms.ValidationError("Email ini sudah digunakan akun lain.")
        return email

class EduOpsPasswordChangeForm(SetPasswordForm):
    new_password1 = forms.CharField(
        label="Password Baru",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan password baru'})
    )
    new_password2 = forms.CharField(
        label="Konfirmasi Password Baru",
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ulangi password baru'})
    )
