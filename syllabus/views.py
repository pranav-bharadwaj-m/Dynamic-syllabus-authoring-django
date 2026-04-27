from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
from .models import Syllabus, Module
from .forms import SyllabusForm, ModuleFormSet
import base64, os


def _logo_data_uri(filename):
    """Read a file from BASE_DIR and return a base64 data URI for WeasyPrint."""
    path = os.path.join(settings.BASE_DIR, filename)
    try:
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('utf-8')
        ext = filename.rsplit('.', 1)[-1].lower()
        mime = 'image/webp' if ext == 'webp' else f'image/{ext}'
        return f"data:{mime};base64,{b64}"
    except FileNotFoundError:
        return ''


def create_syllabus(request):
    if request.method == 'POST':
        form = SyllabusForm(request.POST)
        formset = ModuleFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            syllabus = form.save()
            modules = formset.save(commit=False)
            for module in modules:
                module.syllabus = syllabus
                module.save()
            for obj in formset.deleted_objects:
                obj.delete()
            return redirect('create_syllabus')
    else:
        form = SyllabusForm()
        formset = ModuleFormSet()

    return render(request, 'syllabus/form.html', {'form': form, 'formset': formset})


def export_pdf(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    context = {
        'syllabus': syllabus,
        'sjbit_logo': _logo_data_uri('sjbit-new-logo.webp'),
        'naac_logo':  _logo_data_uri('NAAC-Logo-250x250-1.webp'),
    }
    html_string = render_to_string('syllabus/pdf_template.html', context)
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="syllabus_{syllabus.course_code}.pdf"'
    return response


# ── AJAX Module deletion endpoints ──────────────────────────────────────────

@require_POST
def delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    module.is_deleted = True
    module.save()
    return JsonResponse({'ok': True})


@require_POST
def restore_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    module.is_deleted = False
    module.save()
    return JsonResponse({'ok': True})


@require_POST
def permanent_delete_module(request, module_id):
    module = get_object_or_404(Module, id=module_id)
    module.delete()
    return JsonResponse({'ok': True})