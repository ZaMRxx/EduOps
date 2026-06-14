
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0002_jadwalkelas_tanggal_spesifik_jadwalkelas_tipe_repeat'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jadwalkelas',
            name='tipe',
            field=models.CharField(default='Regular', max_length=50, verbose_name='Tipe Jadwal'),
        ),
    ]
