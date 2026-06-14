from django import forms
from .models import JadwalKelas, Sekolah, RequestJadwal
from accounts.models import CustomUser

class JadwalKelasForm(forms.ModelForm):
    class Meta:
        model = JadwalKelas
        fields = [
            'guru', 'sekolah', 'nama_kelas', 'hari', 'jam_mulai', 'jam_selesai',
            'pertemuan_per_minggu', 'jam_berangkat_pulang', 'kali_ke_sekolah_per_minggu',
            'mode', 'tipe', 'kegiatan', 'tipe_repeat', 'tanggal_spesifik',
            'tanggal_mulai_efektif', 'tanggal_selesai', 'aktif'
        ]
        widgets = {
            'nama_kelas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Kelas'}),
            'guru': forms.Select(attrs={'class': 'form-select'}),
            'sekolah': forms.Select(attrs={'class': 'form-select'}),
            'hari': forms.Select(attrs={'class': 'form-select'}),
            'jam_mulai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'jam_selesai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'pertemuan_per_minggu': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'step': 1}),
            'jam_berangkat_pulang': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01', 'placeholder': 'Contoh: 0.83'}),
            'kali_ke_sekolah_per_minggu': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'tipe': forms.TextInput(attrs={'class': 'form-control', 'list': 'tipe-choices', 'placeholder': 'Masukkan/Pilih Tipe Jadwal (e.g. Regular, Event, Trial)'}),
            'kegiatan': forms.Select(attrs={'class': 'form-select'}),
            'tipe_repeat': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipe_repeat'}),
            'tanggal_spesifik': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_tanggal_spesifik'}),
            'tanggal_mulai_efektif': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_tanggal_mulai_efektif'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_tanggal_selesai'}),
            'aktif': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user is not None:
            if user.role == 'admin_branch':
                self.fields['guru'].queryset = CustomUser.objects.filter(role='teacher', branch=user.branch)
                self.fields['sekolah'].queryset = Sekolah.objects.filter(branch=user.branch)
            else:
                self.fields['guru'].queryset = CustomUser.objects.filter(role='teacher')
    def clean(self):
        cleaned_data = super().clean()
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        tipe_repeat = cleaned_data.get('tipe_repeat')
        tanggal_spesifik = cleaned_data.get('tanggal_spesifik')
        pertemuan_per_minggu = cleaned_data.get('pertemuan_per_minggu')
        jam_berangkat_pulang = cleaned_data.get('jam_berangkat_pulang')
        kali_ke_sekolah_per_minggu = cleaned_data.get('kali_ke_sekolah_per_minggu')
        
        if jam_mulai and jam_selesai and jam_mulai >= jam_selesai:
            raise forms.ValidationError("Waktu mulai kelas harus lebih awal daripada waktu selesai kelas!")
            
        if tipe_repeat == 'one_time' and not tanggal_spesifik:
            self.add_error('tanggal_spesifik', "Tanggal spesifik wajib diisi jika memilih tipe perulangan Sekali Saja (One-Time).")

        if pertemuan_per_minggu is not None and pertemuan_per_minggu < 1:
            self.add_error('pertemuan_per_minggu', "Pertemuan per minggu minimal 1.")

        if jam_berangkat_pulang is not None and jam_berangkat_pulang < 0:
            self.add_error('jam_berangkat_pulang', "Total jam berangkat dan pulang tidak boleh negatif.")

        if kali_ke_sekolah_per_minggu is not None and kali_ke_sekolah_per_minggu < 0:
            self.add_error('kali_ke_sekolah_per_minggu', "Kali per minggu ke sekolah tidak boleh negatif.")
            
        return cleaned_data

class RequestJadwalForm(forms.ModelForm):
    class Meta:
        model = RequestJadwal
        fields = [
            'request_type', 'target_jadwal', 'guru', 'sekolah', 'nama_kelas', 'hari',
            'jam_mulai', 'jam_selesai', 'pertemuan_per_minggu', 'jam_berangkat_pulang',
            'kali_ke_sekolah_per_minggu', 'mode', 'tipe', 'kegiatan', 'tipe_repeat',
            'tanggal_spesifik', 'tanggal_mulai_efektif', 'tanggal_selesai', 'detail'
        ]
        widgets = {
            'request_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_request_type'}),
            'target_jadwal': forms.Select(attrs={'class': 'form-select', 'id': 'id_target_jadwal'}),
            'guru': forms.Select(attrs={'class': 'form-select'}),
            'sekolah': forms.Select(attrs={'class': 'form-select'}),
            'nama_kelas': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Kelas'}),
            'hari': forms.Select(attrs={'class': 'form-select'}),
            'jam_mulai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'jam_selesai': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'pertemuan_per_minggu': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'step': 1}),
            'jam_berangkat_pulang': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': '0.01'}),
            'kali_ke_sekolah_per_minggu': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'step': 1}),
            'mode': forms.Select(attrs={'class': 'form-select'}),
            'tipe': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Regular, Ekskul, Trial, dll.'}),
            'kegiatan': forms.Select(attrs={'class': 'form-select'}),
            'tipe_repeat': forms.Select(attrs={'class': 'form-select', 'id': 'id_tipe_repeat'}),
            'tanggal_spesifik': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_tanggal_spesifik'}),
            'tanggal_mulai_efektif': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_tanggal_mulai_efektif'}),
            'tanggal_selesai': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'id': 'id_tanggal_selesai'}),
            'detail': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Tambahkan alasan/keterangan perubahan jadwal.'
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['target_jadwal'].required = False
        self.fields['sekolah'].required = False
        self.fields['tanggal_spesifik'].required = False
        self.fields['tanggal_mulai_efektif'].required = False
        self.fields['tanggal_selesai'].required = False

        if user is not None:
            if user.role == 'teacher':
                self.fields['guru'].queryset = CustomUser.objects.filter(pk=user.pk)
                self.fields['guru'].initial = user
                self.fields['target_jadwal'].queryset = JadwalKelas.objects.filter(guru=user, aktif=True)
            elif user.role == 'admin_branch':
                self.fields['guru'].queryset = CustomUser.objects.filter(role='teacher', branch=user.branch)
                self.fields['sekolah'].queryset = Sekolah.objects.filter(branch=user.branch)
                self.fields['target_jadwal'].queryset = JadwalKelas.objects.filter(guru__branch=user.branch, aktif=True)
            else:
                self.fields['guru'].queryset = CustomUser.objects.filter(role='teacher')
                self.fields['target_jadwal'].queryset = JadwalKelas.objects.filter(aktif=True)

    def clean(self):
        cleaned_data = super().clean()
        request_type = cleaned_data.get('request_type')
        target_jadwal = cleaned_data.get('target_jadwal')
        guru = cleaned_data.get('guru')
        nama_kelas = cleaned_data.get('nama_kelas')
        hari = cleaned_data.get('hari')
        jam_mulai = cleaned_data.get('jam_mulai')
        jam_selesai = cleaned_data.get('jam_selesai')
        tipe_repeat = cleaned_data.get('tipe_repeat')
        tanggal_spesifik = cleaned_data.get('tanggal_spesifik')

        if request_type == 'edit' and not target_jadwal:
            self.add_error('target_jadwal', "Pilih jadwal yang ingin diubah.")

        if not guru:
            self.add_error('guru', "Pilih guru/teacher untuk jadwal ini.")

        if not nama_kelas:
            self.add_error('nama_kelas', "Nama kelas wajib diisi.")

        if not hari:
            self.add_error('hari', "Hari kelas wajib dipilih.")

        if not jam_mulai:
            self.add_error('jam_mulai', "Jam mulai wajib diisi.")

        if not jam_selesai:
            self.add_error('jam_selesai', "Jam selesai wajib diisi.")

        if jam_mulai and jam_selesai and jam_mulai >= jam_selesai:
            raise forms.ValidationError("Waktu mulai kelas harus lebih awal daripada waktu selesai kelas!")

        if tipe_repeat == 'one_time' and not tanggal_spesifik:
            self.add_error('tanggal_spesifik', "Tanggal spesifik wajib diisi untuk jadwal sekali saja.")

        return cleaned_data

class SekolahForm(forms.ModelForm):
    class Meta:
        model = Sekolah
        fields = ['nama', 'branch', 'tipe']
        widgets = {
            'nama': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Nama Sekolah'}),
            'branch': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Masukkan Cabang (misal: BSD, Bintaro, Bandung)'}),
            'tipe': forms.Select(attrs={'class': 'form-select'}),
        }
