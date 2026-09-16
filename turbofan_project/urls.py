from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views  # 🔥 ADD THIS

urlpatterns = [
    path('admin/', admin.site.urls),

    # 🔥 YOUR APP
    path('', include('predictor.urls')),

    # 🔐 PASSWORD RESET SYSTEM
    path('reset-password/', auth_views.PasswordResetView.as_view(
        template_name='password_reset.html'
    ), name='password_reset'),

    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(
        template_name='password_reset_sent.html'
    ), name='password_reset_done'),

    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='password_reset_form.html'
    ), name='password_reset_confirm'),

    path('reset-complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='password_reset_done.html'
    ), name='password_reset_complete'),
]