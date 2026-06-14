from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(
        template_name='accounts/password_reset_form.html',
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
        success_url='/accounts/password-reset/done/',
        extra_context={'hide_sidebar': True}
    ), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html',
        extra_context={'hide_sidebar': True}
    ), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        success_url='/accounts/reset/done/',
        extra_context={'hide_sidebar': True}
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
        extra_context={'hide_sidebar': True}
    ), name='password_reset_complete'),
    path('register/', views.register_teacher, name='register_teacher'),
    path('profile/', views.profile_edit, name='profile_edit'),
    path('users/create/', views.admin_create_user, name='admin_create_user'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:pk>/edit/', views.admin_edit_user, name='admin_edit_user'),
    path('users/<int:pk>/delete/', views.admin_delete_user, name='admin_delete_user'),
]
