
from decimal import Decimal
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0003_alter_jadwalkelas_tipe'),
    ]

    operations = [
        migrations.AddField(
            model_name='jadwalkelas',
            name='pertemuan_per_minggu',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Pertemuan per Minggu'),
        ),
        migrations.AddField(
            model_name='jadwalkelas',
            name='jam_berangkat_pulang',
            field=models.DecimalField(decimal_places=2, default=Decimal('0.00'), max_digits=5, verbose_name='Total Jam Berangkat dan Pulang'),
        ),
        migrations.AddField(
            model_name='jadwalkelas',
            name='kali_ke_sekolah_per_minggu',
            field=models.PositiveSmallIntegerField(default=1, verbose_name='Kali per Minggu ke Sekolah'),
        ),
    ]
