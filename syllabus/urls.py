from django.urls import path
from . import views

urlpatterns = [
    path('', views.edit_syllabus, name='edit_syllabus'),
    path('pdf/<int:syllabus_id>/', views.export_pdf, name='export_pdf'),
    path('module/delete/<int:module_id>/',           views.delete_module,           name='delete_module'),
    path('module/restore/<int:module_id>/',          views.restore_module,          name='restore_module'),
    path('module/permanent-delete/<int:module_id>/', views.permanent_delete_module, name='permanent_delete_module'),
]