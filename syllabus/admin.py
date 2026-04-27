from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Syllabus, Module, ApprovalLog

admin.site.register(Syllabus)
admin.site.register(Module)
admin.site.register(ApprovalLog)