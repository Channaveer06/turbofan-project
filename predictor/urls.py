from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    path('upload/', views.upload_view, name='upload'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('api/predict/', views.api_predict, name='api_predict'),
    path('download/', views.download_report, name='download_report'),

    path('logs/', views.logs_view, name='logs'),

    # 🔥 LOG VIEW
    path('view-log/<int:index>/', views.view_log, name='view_log'),

   

    # 🔥 AUTH SYSTEM
    path('signup/', views.signup_request, name='signup'),
    path('approve/<int:id>/', views.approve_user, name='approve_user'),
    path('reject/<int:id>/', views.reject_user, name='reject_user'),

    # 🔥 ADMIN PANEL
    path('admin-panel/', views.admin_panel, name='admin_panel'),
    path('delete-user/<int:id>/', views.delete_user, name='delete_user'),  # ✅ ADD THIS
]