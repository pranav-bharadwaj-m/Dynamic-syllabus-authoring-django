import json, base64, os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.conf import settings
from weasyprint import HTML
from .models import Syllabus, Module, LabExperiment, RBT_CHOICES
from .forms import SyllabusForm, ModuleFormSet, LabExperimentFormSet


def _logo_b64(filename):
    path = os.path.join(settings.BASE_DIR, filename)
    try:
        with open(path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode()
        ext = filename.rsplit('.', 1)[-1].lower()
        mime = 'image/webp' if ext == 'webp' else f'image/{ext}'
        return f"data:{mime};base64,{b64}"
    except FileNotFoundError:
        return ''


def edit_syllabus(request):
    """Always edit the single syllabus record (pk=1). PDF is always at /pdf/1/."""
    syllabus, _ = Syllabus.objects.get_or_create(pk=1)
    active_modules_qs  = Module.objects.filter(syllabus=syllabus, is_deleted=False)
    main_lab_qs        = LabExperiment.objects.filter(syllabus=syllabus, is_additional=False)
    add_lab_qs         = LabExperiment.objects.filter(syllabus=syllabus, is_additional=True)

    if request.method == 'POST':
        form         = SyllabusForm(request.POST, instance=syllabus)
        module_fs    = ModuleFormSet(request.POST, instance=syllabus, queryset=active_modules_qs, prefix='modules')
        main_lab_fs  = LabExperimentFormSet(request.POST, instance=syllabus, queryset=main_lab_qs, prefix='labmain')
        add_lab_fs   = LabExperimentFormSet(request.POST, instance=syllabus, queryset=add_lab_qs,  prefix='labadd')

        if form.is_valid():
            syllabus = form.save(commit=False)

            # Parse hidden-JSON textbooks
            try:
                syllabus.textbooks_json       = json.loads(request.POST.get('textbooks_json', '[]'))
            except Exception:
                syllabus.textbooks_json = []
            try:
                syllabus.reference_books_json = json.loads(request.POST.get('reference_books_json', '[]'))
            except Exception:
                syllabus.reference_books_json = []
            syllabus.save()

            # Modules
            if module_fs.is_valid():
                mods = module_fs.save(commit=False)
                for mod in mods:
                    mod.syllabus = syllabus
                    # rbt_levels comes as JSON string from hidden input
                    rbt_raw = request.POST.get(f'rbt_json_{mod.pk}', '[]')
                    try:
                        mod.rbt_levels = json.loads(rbt_raw)
                    except Exception:
                        mod.rbt_levels = []
                    mod.save()
                for obj in module_fs.deleted_objects:
                    obj.delete()

            # Lab experiments (main)
            if main_lab_fs.is_valid():
                for exp in main_lab_fs.save(commit=False):
                    exp.syllabus     = syllabus
                    exp.is_additional = False
                    exp.save()
                for obj in main_lab_fs.deleted_objects:
                    obj.delete()

            # Lab experiments (additional)
            if add_lab_fs.is_valid():
                for exp in add_lab_fs.save(commit=False):
                    exp.syllabus      = syllabus
                    exp.is_additional = True
                    exp.save()
                for obj in add_lab_fs.deleted_objects:
                    obj.delete()

        return redirect('edit_syllabus')

    # GET
    form        = SyllabusForm(instance=syllabus)
    module_fs   = ModuleFormSet(instance=syllabus, queryset=active_modules_qs, prefix='modules')
    main_lab_fs = LabExperimentFormSet(instance=syllabus, queryset=main_lab_qs, prefix='labmain')
    add_lab_fs  = LabExperimentFormSet(instance=syllabus, queryset=add_lab_qs,  prefix='labadd')

    return render(request, 'syllabus/form.html', {
        'form': form, 'formset': module_fs,
        'main_lab_fs': main_lab_fs, 'add_lab_fs': add_lab_fs,
        'syllabus': syllabus, 'rbt_choices': RBT_CHOICES,
        'textbooks_json_str': json.dumps(syllabus.textbooks_json or []),
        'reference_books_json_str': json.dumps(syllabus.reference_books_json or []),
    })


def export_pdf(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    context = {
        'syllabus':    syllabus,
        'sjbit_logo':  _logo_b64('sjbit-new-logo.webp'),
        'naac_logo':   _logo_b64('NAAC-Logo-250x250-1.webp'),
        'main_exps':   syllabus.lab_experiments.filter(is_additional=False),
        'add_exps':    syllabus.lab_experiments.filter(is_additional=True),
        'active_modules': syllabus.modules.filter(is_deleted=False),
    }
    html_string = render_to_string('syllabus/pdf_template.html', context)
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="syllabus_{syllabus.course_code}.pdf"'
    return response


# ── AJAX Module endpoints ────────────────────────────────────────────────────
@require_POST
def delete_module(request, module_id):
    m = get_object_or_404(Module, id=module_id)
    m.is_deleted = True; m.save()
    return JsonResponse({'ok': True})

@require_POST
def restore_module(request, module_id):
    m = get_object_or_404(Module, id=module_id)
    m.is_deleted = False; m.save()
    return JsonResponse({'ok': True})

@require_POST
def permanent_delete_module(request, module_id):
    get_object_or_404(Module, id=module_id).delete()
    return JsonResponse({'ok': True})