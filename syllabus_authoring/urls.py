"""
URL configuration for syllabus_authoring project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from syllabus import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_syllabus, name='create_syllabus'),
    path('edit/<int:syllabus_id>/', views.edit_syllabus, name='edit_syllabus'),
    path('delete/<int:syllabus_id>/', views.delete_syllabus, name='delete_syllabus'),
    
    path('approve/<int:syllabus_id>/', views.process_approval, name='process_approval'),
    path('pdf/<int:syllabus_id>/', views.export_pdf, name='export_pdf'),
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html', next_page='/'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    
    # AJAX endpoints
    path('module/delete/<int:module_id>/', views.delete_module, name='delete_module'),
    path('module/restore/<int:module_id>/', views.restore_module, name='restore_module'),
    path('module/permanent_delete/<int:module_id>/', views.permanent_delete_module, name='permanent_delete_module'),
]
