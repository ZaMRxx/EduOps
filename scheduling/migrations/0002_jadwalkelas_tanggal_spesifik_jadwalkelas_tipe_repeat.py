
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('scheduling', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='jadwalkelas',
            name='tanggal_spesifik',
            field=models.DateField(blank=True, null=True, verbose_name='Tanggal Spesifik (Untuk Sekali mengajar)'),
        ),
        migrations.AddField(
            model_name='jadwalkelas',
            name='tipe_repeat',
            field=models.CharField(choices=[('weekly', 'Repeatable (Tiap Minggu)'), ('one_time', 'One-Time (Sekali saja)')], default='weekly', max_length=20, verbose_name='Tipe Perulangan'),
        ),
    ]
