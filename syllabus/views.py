import json, base64, os
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth.decorators import login_required
from weasyprint import HTML
from .models import Syllabus, Module, LabExperiment, CourseOutcome, RBT_CHOICES
from .forms import SyllabusForm, ModuleFormSet, LabExperimentFormSet, CourseOutcomeFormSet
import reversion
from django.contrib.auth.models import Group
from django.contrib import messages

@login_required(login_url='/login/')
def dashboard(request):
    """Role-based routing"""
    if request.user.is_superuser:
        # Force Admin to Django Backend
        return redirect('/admin/syllabus/syllabus/')

    is_hod = request.user.groups.filter(name='HOD').exists()

    if is_hod:
        role = "HOD"
        # HOD only sees syllabi submitted by faculty
        syllabi = Syllabus.objects.filter(status='PENDING_HOD').order_by('-id')
    else:
        role = "Faculty"
        # Faculty sees all their own syllabi
        syllabi = Syllabus.objects.filter(created_by=request.user).order_by('-id')

    return render(request, 'syllabus/dashboard.html', {
        'role': role, 'syllabi': syllabi, 'is_hod': is_hod
    })

@login_required(login_url='/login/')
def create_syllabus(request):
    """Generates a blank syllabus for the faculty member"""
    import random
    temp_code = f"NEW{random.randint(1000,9999)}"
    syllabus = Syllabus.objects.create(
        created_by=request.user, title="Untitled Syllabus", course_code=temp_code
    )
    return redirect('edit_syllabus', syllabus_id=syllabus.id)

@login_required(login_url='/login/')
def delete_syllabus(request, syllabus_id):
    """Allows faculty to delete their own syllabus"""
    syllabus = get_object_or_404(Syllabus, id=syllabus_id, created_by=request.user)
    syllabus.delete()
    return redirect('dashboard')

@login_required(login_url='/login/')
@require_POST
def process_approval(request, syllabus_id):
    """Handles the sequential status tracking and audit logging"""
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    action = request.POST.get('action') 
    comments = request.POST.get('comments', '')

    with reversion.create_revision():
        if action == 'APPROVE':
            syllabus.status = 'PENDING_ADMIN'
            syllabus.latest_remark = "Approved by HOD. Forwarded to Admin."
            
            
        elif action == 'REJECT':
            syllabus.status = 'REJECTED_BY_HOD'
            syllabus.latest_remark = comments

        syllabus.save()
        
        # Log the audit trail
        # from .models import ApprovalLog
        # ApprovalLog.objects.create(
        #     syllabus=syllabus, actor=request.user, action=action, comments=comments
        # )
        reversion.set_user(request.user)
        reversion.set_comment(f"HOD changed status to {syllabus.status}")

    return redirect('dashboard')

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

@login_required(login_url='/login/')
def edit_syllabus(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    
    if not syllabus.created_by:
        syllabus.created_by = request.user
        syllabus.save()

    if not Module.objects.filter(syllabus=syllabus, is_deleted=False).exists():
        Module.objects.create(syllabus=syllabus, module_number=1, title="")
        
    # Auto-create CO1 if none exist
    if not CourseOutcome.objects.filter(syllabus=syllabus).exists():
        CourseOutcome.objects.create(syllabus=syllabus, sl_no=1, description="")

    active_modules_qs  = Module.objects.filter(syllabus=syllabus, is_deleted=False).order_by('module_number')
    main_lab_qs        = LabExperiment.objects.filter(syllabus=syllabus, is_additional=False)
    add_lab_qs         = LabExperiment.objects.filter(syllabus=syllabus, is_additional=True)
    co_qs              = CourseOutcome.objects.filter(syllabus=syllabus)

    if request.method == 'POST':
        if 'clear_form' in request.POST:
            syllabus.modules.all().delete()
            syllabus.lab_experiments.all().delete()
            syllabus.course_outcomes.all().delete()
            
            syllabus.title = ""
            syllabus.course_code = ""
            syllabus.objectives = ""
            syllabus.teaching_learning = ""
            syllabus.lab_description = ""
            syllabus.lab_prerequisites = ""
            syllabus.lab_self_learning = ""
            syllabus.co_description = ""
            syllabus.assessment_general_rules = ""
            syllabus.assessment_cie = ""
            syllabus.assessment_see = ""

            # Reset all numeric/choice metadata to their defaults
            syllabus.credits = 0
            syllabus.semester = 'I'
            syllabus.course_type = 'PCC'
            syllabus.see_type = 'Theory'
            syllabus.content_type = 'theory_only'
            syllabus.lec_hours = 0
            syllabus.tut_hours = 0
            syllabus.prac_hours = 0
            syllabus.other_hours = 0
            syllabus.total_hours = 0
            syllabus.lab_slots = ""
            syllabus.cie_marks = 0
            syllabus.see_marks = 0
            syllabus.total_marks = 0
            syllabus.exam_hours = 0

            syllabus.weblinks_custom = ""
            syllabus.weblinks_json = []
            syllabus.activity_based_learning = ""

            syllabus.textbooks_json = []
            syllabus.reference_books_json = []
            syllabus.copo_matrix = {}

            syllabus.status = "DRAFT"
            syllabus.save()
            return redirect('edit_syllabus')

        post_data = request.POST.copy()

        # --- INDESTRUCTIBLE POST DATA CLEANUP ---
        post_data = request.POST.copy()
        
        # GLOBAL ZERO STRIPPER: Removes "01" -> "1", "007" -> "7" from ALL inputs globally
        for key, values in post_data.lists():
            cleaned_values = []
            for v in values:
                if isinstance(v, str):
                    v_strip = v.strip()
                    # If it's pure numbers, longer than 1 character, and starts with 0
                    if v_strip.isdigit() and len(v_strip) > 1 and v_strip.startswith('0'):
                        stripped = v_strip.lstrip('0')
                        cleaned_values.append(stripped if stripped else '0')
                        continue
                cleaned_values.append(v)
            post_data.setlist(key, cleaned_values)

        total_modules = int(post_data.get('modules-TOTAL_FORMS', 0))
        for i in range(total_modules):
            title = post_data.get(f'modules-{i}-title', '').strip()
            content = post_data.get(f'modules-{i}-content', '').strip()
            if not title and not content:
                post_data[f'modules-{i}-DELETE'] = 'on'
                post_data[f'modules-{i}-title'] = 'Deleted Ghost Module'
                post_data[f'modules-{i}-teaching_hours'] = '0'
                post_data[f'modules-{i}-module_number'] = '99'
            else:
                if not post_data.get(f'modules-{i}-teaching_hours'):
                    post_data[f'modules-{i}-teaching_hours'] = '0'
                if not post_data.get(f'modules-{i}-module_number'):
                    post_data[f'modules-{i}-module_number'] = str(i+1)
                
                raw_hours = post_data.get(f'modules-{i}-teaching_hours', '0').strip()
                if not raw_hours: raw_hours = '0'
                try:
                    post_data[f'modules-{i}-teaching_hours'] = str(int(raw_hours))
                except ValueError:
                    post_data[f'modules-{i}-teaching_hours'] = '0'

        for key in post_data.keys():
            if 'rbt_levels' in key and post_data[key].strip() == '':
                post_data[key] = '[]'
        if post_data.get('copo_matrix', '').strip() == '':
            post_data['copo_matrix'] = '{}'

        form         = SyllabusForm(post_data, instance=syllabus)
        module_fs    = ModuleFormSet(post_data, instance=syllabus, queryset=active_modules_qs, prefix='modules')
        main_lab_fs  = LabExperimentFormSet(post_data, instance=syllabus, queryset=main_lab_qs, prefix='labmain')
        add_lab_fs   = LabExperimentFormSet(post_data, instance=syllabus, queryset=add_lab_qs,  prefix='labadd')
        co_fs        = CourseOutcomeFormSet(post_data, instance=syllabus, queryset=co_qs, prefix='co')

        if form.is_valid() and module_fs.is_valid() and main_lab_fs.is_valid() and add_lab_fs.is_valid() and co_fs.is_valid():
            with reversion.create_revision():
                if 'send_approval' in request.POST:
                    syllabus.status = 'PENDING_HOD'
                    syllabus.latest_remark = ""

                syllabus = form.save(commit=False)

                try:
                    syllabus.textbooks_json = json.loads(post_data.get('textbooks_json', '[]'))
                except Exception:
                    syllabus.textbooks_json = []
                try:
                    syllabus.reference_books_json = json.loads(post_data.get('reference_books_json', '[]'))
                except Exception:
                    syllabus.reference_books_json = []
                try:
                    syllabus.weblinks_json = json.loads(post_data.get('weblinks_json', '[]'))
                except Exception:
                    syllabus.weblinks_json = []

                syllabus.save()

                mods = module_fs.save(commit=False)
                for mod in mods:
                    mod.syllabus = syllabus
                    mod.save()
                for obj in module_fs.deleted_objects:
                    obj.delete()

                for exp in main_lab_fs.save(commit=False):
                    if not exp.title: continue
                    exp.syllabus = syllabus
                    exp.is_additional = False
                    exp.save()
                for obj in main_lab_fs.deleted_objects:
                    obj.delete()

                for exp in add_lab_fs.save(commit=False):
                    if not exp.title: continue
                    exp.syllabus = syllabus
                    exp.is_additional = True
                    exp.save()
                for obj in add_lab_fs.deleted_objects:
                    obj.delete()
                    
                for co in co_fs.save(commit=False):
                    if not co.description: continue
                    co.syllabus = syllabus
                    co.save()
                for obj in co_fs.deleted_objects:
                    obj.delete()

                reversion.set_user(request.user)
                reversion.set_comment("Faculty edited draft." if 'save_draft' in request.POST else "Submitted for BOS Approval.")
            return redirect('dashboard')
        else:
            print("--- VALIDATION FAILED ---")
            print("Form Errors:", form.errors)
            print("Module Errors:", module_fs.errors)

    else:
        hide_defaults = {}
        if syllabus.course_code.startswith('NEW'):
            hide_defaults['course_code'] = ''
        if syllabus.title == 'Untitled Syllabus':
            hide_defaults['title'] = ''
        form        = SyllabusForm(instance=syllabus, initial=hide_defaults)
        module_fs   = ModuleFormSet(instance=syllabus)
        main_lab_fs = LabExperimentFormSet(instance=syllabus, queryset=syllabus.lab_experiments.filter(is_additional=False), prefix='labmain')
        add_lab_fs  = LabExperimentFormSet(instance=syllabus, queryset=syllabus.lab_experiments.filter(is_additional=True),  prefix='labadd')
        co_fs       = CourseOutcomeFormSet(instance=syllabus, queryset=co_qs, prefix='co')

    return render(request, 'syllabus/form.html', {
        'form': form, 'formset': module_fs,
        'main_lab_fs': main_lab_fs, 'add_lab_fs': add_lab_fs, 'co_fs': co_fs,
        'syllabus': syllabus, 'rbt_choices': RBT_CHOICES,
        'textbooks_json_str': json.dumps(syllabus.textbooks_json or []),
        'reference_books_json_str': json.dumps(syllabus.reference_books_json or []),
        'weblinks_json_str': json.dumps(syllabus.weblinks_json or []),
        'copo_matrix_json': json.dumps(syllabus.copo_matrix or {}),
    })

def export_pdf(request, syllabus_id):
    syllabus = get_object_or_404(Syllabus, id=syllabus_id)
    
    # Pre-calculate the CO-PO matrix rows for the PDF Template
    cols = [str(i) for i in range(1, 13)] + ['S1', 'S2', 'S3']
    copo_rows = []
    for co in syllabus.course_outcomes.all():
        co_num = str(co.sl_no)
        # Pull the values for this specific CO row, defaulting to empty space
        row_data = [syllabus.copo_matrix.get(co_num, {}).get(col, '') for col in cols]
        copo_rows.append({'co_label': f'CO{co_num}', 'data': row_data})

    context = {
        'syllabus':    syllabus,
        'sjbit_logo':  _logo_b64('sjbit-new-logo.webp'),
        'naac_logo':   _logo_b64('NAAC-Logo-250x250-1.webp'),
        'main_exps':   syllabus.lab_experiments.filter(is_additional=False),
        'add_exps':    syllabus.lab_experiments.filter(is_additional=True),
        'active_modules': syllabus.modules.filter(is_deleted=False).order_by('module_number'),
        'copo_rows':   copo_rows, # <--- Passing the processed matrix to the template
    }
    html_string = render_to_string('syllabus/pdf_template.html', context)
    pdf = HTML(string=html_string).write_pdf()
    response = HttpResponse(pdf, content_type='application/pdf')
    
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    response['Content-Disposition'] = f'inline; filename="syllabus_{syllabus.course_code}.pdf"'
    return response

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