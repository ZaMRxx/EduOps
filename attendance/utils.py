from django.contrib.auth.models import AnonymousUser
from .models import LogAktivitas

def catat_log(user, aksi, detail=''):
    """
    Mencatat log aktivitas pengguna ke database.
    Jika user tidak terotentikasi (misalnya AnonymousUser) atau None,
    maka field user akan diisi None.
    """
    db_user = None
    if user and hasattr(user, 'is_authenticated') and user.is_authenticated:
        if not isinstance(user, AnonymousUser):
            db_user = user
            
    LogAktivitas.objects.create(
        user=db_user,
        aksi=aksi,
        detail=detail
    )
