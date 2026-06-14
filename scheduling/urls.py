from django.urls import path
from . import views
from django.http import HttpResponse
def placeholder_view(request, *args, **kwargs):
    return HttpResponse("<h1>Halaman Operasional</h1><p>Halaman ini akan diaktifkan sepenuhnya pada Sesi berikutnya.</p><p><a href='/scheduling/schedule/'>Kembali ke Kalender Grid</a></p>")
urlpatterns = [
    path('schedule/', views.schedule_view, name='schedule_view'),
    path('list/', views.jadwal_list, name='jadwal_list'),
    path('add/', views.jadwal_add, name='jadwal_add'),
    path('edit/<int:pk>/', views.jadwal_edit, name='jadwal_edit'),
    path('delete/<int:pk>/', views.jadwal_delete, name='jadwal_delete'),
    path('requests/', views.request_list, name='request_list'),
    path('requests/<int:pk>/approve/', views.request_approve, name='request_approve'),
    path('requests/<int:pk>/reject/', views.request_reject, name='request_reject'),
    path('sekolah/', views.sekolah_list, name='sekolah_list'),
    path('sekolah/add/', views.sekolah_add, name='sekolah_add'),
    path('sekolah/<int:pk>/edit/', views.sekolah_edit, name='sekolah_edit'),
    path('sekolah/<int:pk>/delete/', views.sekolah_delete, name='sekolah_delete'),
]
