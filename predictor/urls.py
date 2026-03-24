from django.urls import path
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),  # 🔥 ADD THIS

    path('upload/', views.upload_view, name='upload'),
    path('dashboard/', views.dashboard_view, name='dashboard'),

    path('api/predict/', views.api_predict, name='api_predict'),
    path('download/', views.download_report, name='download_report'),
]