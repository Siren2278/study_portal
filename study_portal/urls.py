from django.contrib import admin
from django.urls import path, include
from dashboard import views as dash_views
from dashboard import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('register/', dash_views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='dashboard/login.html'), name='login'),
    path('profile/', dash_views.profile, name='profile'),
    path('logout/', views.custom_logout, name='logout'),
]
