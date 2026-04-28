from django.contrib import admin
from django.utils.html import format_html
from .models import Syllabus, Module, ApprovalLog

@admin.register(Syllabus)
class SyllabusAdmin(admin.ModelAdmin):
    list_display = ('course_code', 'title', 'status', 'created_by', 'pdf_link')
    list_filter = ('status', 'course_type')
    search_fields = ('course_code', 'title')
    readonly_fields = ('created_by',)

    def pdf_link(self, obj):
        return format_html('<a href="/pdf/{}/" target="_blank" style="background:#4f46e5;color:white;padding:5px 10px;border-radius:4px;text-decoration:none;">📄 View PDF</a>', obj.id)
    pdf_link.short_description = "Syllabus PDF"

    # Push status and remarks to the top of the admin panel for easy access
    def get_fields(self, request, obj=None):
        fields = list(super().get_fields(request, obj))
        if 'status' in fields: fields.remove('status')
        if 'latest_remark' in fields: fields.remove('latest_remark')
        return ['status', 'latest_remark'] + fields

admin.site.register(Module)