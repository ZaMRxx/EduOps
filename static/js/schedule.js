
document.addEventListener('DOMContentLoaded', function() {
    renderJadwalGrid();
});
function renderJadwalGrid() {
    const dataTag = document.getElementById('jadwal-data');
    if (!dataTag) return;

    try {
        const jadwalData = JSON.parse(dataTag.textContent);
        for (const teacherId in jadwalData) {
            const teacherObj = jadwalData[teacherId];
            const gridBody = document.getElementById(`grid-body-${teacherId}`);
            
            if (!gridBody) continue;
            gridBody.innerHTML = '';
            
            const listJadwal = teacherObj.jadwal || [];
            listJadwal.forEach(jadwal => {
                const card = createJadwalCard(jadwal, teacherObj.warna);
                gridBody.appendChild(card);
            });
        }
    } catch (error) {
        console.error("Gagal mengurai data jadwal JSON:", error);
    }
}
function hitungPosisi(jam_mulai, jam_selesai) {
    const JAM_MULAI_GRID = 7;
    const TINGGI_PER_JAM = 60;
    const [h1, m1] = jam_mulai.split(':').map(Number);
    const [h2, m2] = jam_selesai.split(':').map(Number);
    const menitDariAwal = (h1 - JAM_MULAI_GRID) * 60 + m1;
    const durasiMenit = (h2 - JAM_MULAI_GRID) * 60 + m2 - menitDariAwal;
    return {
        top: (menitDariAwal / 60) * TINGGI_PER_JAM,
        height: (durasiMenit / 60) * TINGGI_PER_JAM
    };
}
function createJadwalCard(jadwal, warnaTeacher) {
    const { top, height } = hitungPosisi(jadwal.jam_mulai, jadwal.jam_selesai);
    const card = document.createElement('div');
    card.className = 'jadwal-card';
    if (jadwal.sudah_absen) {
        card.classList.add('jadwal-card-done');
        card.title = 'Absensi untuk kelas ini sudah selesai';
    }
    card.style.top = `${top}px`;
    card.style.height = `${height}px`;
    if (height <= 60) {
        card.classList.add('short-card');
    }
    if (height <= 90) {
        card.classList.add('compact-card');
    }
    if (jadwal.sudah_absen) {
        card.style.backgroundColor = '#e5e7eb';
        card.style.borderLeft = '4px solid #6b7280';
    } else {
        card.style.backgroundColor = softenColor(warnaTeacher, 68);
        card.style.borderLeft = `4px solid ${darkenColor(warnaTeacher, -30)}`;
    }
    card.addEventListener('click', function() {
        window.location.href = `/scheduling/edit/${jadwal.id}/`;
    });
    const modeBadgeClass = jadwal.mode === 'online' ? 'bg-primary text-white' : 'bg-secondary text-white';
    const modeText = jadwal.mode === 'online' ? 'Online' : 'Offline';
    const compactModeText = modeText;
    let kegiatanBadgeClass = 'bg-secondary text-white';
    let namaKegiatanClean = 'Lainnya';
    let compactKegiatanText = 'Lainnya';
    if (jadwal.kegiatan === 'mengajar') {
        kegiatanBadgeClass = 'bg-success text-white';
        namaKegiatanClean = 'Utama';
        compactKegiatanText = 'Utama';
    } else if (jadwal.kegiatan === 'asistensi') {
        kegiatanBadgeClass = 'bg-warning text-dark';
        namaKegiatanClean = 'Asisten';
        compactKegiatanText = 'Asisten';
    }
    const repeatBadgeClass = jadwal.tipe_repeat === 'one_time' ? 'bg-danger-subtle text-danger border border-danger-subtle' : 'bg-teal-light text-teal';
    const repeatText = jadwal.tipe_repeat === 'one_time' ? 'Sekali Saja' : 'Mingguan';
    const compactRepeatText = repeatText;
    const tipeLabelRaw = jadwal.tipe || 'Reguler';
    const tipeLabel = tipeLabelRaw.toLowerCase() === 'regular' ? 'Reguler' : tipeLabelRaw;
    const compactTipeLabel = tipeLabel;
    const doneBadge = jadwal.sudah_absen
        ? '<span class="badge bg-secondary text-white" data-short-label="Done">Selesai</span>'
        : '';
    card.innerHTML = `
        
        <span class="branch-badge">${jadwal.branch}</span>
        
        
        <div class="time-text fw-semibold">
            <i class="bi bi-clock-history font-xs"></i> ${jadwal.jam_mulai}-${jadwal.jam_selesai}
        </div>
        
        
        <div class="class-name" title="${jadwal.nama_kelas}">
            ${jadwal.nama_kelas}
        </div>
        
        
        <div class="sekolah-name" title="${jadwal.sekolah}">
            <i class="bi bi-building me-1"></i> ${jadwal.sekolah}
        </div>
        
        
        <div class="badges-row">
            <span class="badge-mode badge ${modeBadgeClass}" data-short-label="${compactModeText}">${modeText}</span>
            <span class="badge-activity badge ${kegiatanBadgeClass}" data-short-label="${compactKegiatanText}">${namaKegiatanClean}</span>
            <span class="badge ${repeatBadgeClass}" data-short-label="${compactRepeatText}">${repeatText}</span>
            <span class="badge bg-light text-dark border" data-short-label="${compactTipeLabel}">${tipeLabel}</span>
            ${doneBadge}
        </div>
    `;
    
    return card;
}
function darkenColor(hex, percent) {
    if (!hex || hex[0] !== '#') return '#198754';
    let num = parseInt(hex.slice(1), 16),
        amt = Math.round(2.55 * percent),
        R = (num >> 16) + amt,
        G = (num >> 8 & 0x00FF) + amt,
        B = (num & 0x0000FF) + amt;
    return "#" + (0x1000000 + (R < 255 ? R < 0 ? 0 : R : 255) * 0x10000 + (G < 255 ? G < 0 ? 0 : G : 255) * 0x100 + (B < 255 ? B < 0 ? 0 : B : 255)).toString(16).slice(1);
}

function softenColor(hex, percentToWhite) {
    if (!hex || hex[0] !== '#') return '#d7f2ec';
    const num = parseInt(hex.slice(1), 16);
    const mix = Math.max(0, Math.min(100, percentToWhite)) / 100;
    const r = num >> 16;
    const g = (num >> 8) & 0x00FF;
    const b = num & 0x0000FF;
    const sr = Math.round(r + (255 - r) * mix);
    const sg = Math.round(g + (255 - g) * mix);
    const sb = Math.round(b + (255 - b) * mix);
    return "#" + (0x1000000 + sr * 0x10000 + sg * 0x100 + sb).toString(16).slice(1);
}
