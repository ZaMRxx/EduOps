from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_customuser_foto_profile'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('super_admin', 'Super Admin'), ('admin_op', 'Admin Operasional'), ('admin_hr', 'Admin HR'), ('admin_branch', 'Admin Branch'), ('teacher', 'Teacher')], default='teacher', max_length=20, verbose_name='Peran'),
        ),
    ]
