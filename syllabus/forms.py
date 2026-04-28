from django import forms
from django.forms import inlineformset_factory
from .models import Syllabus, Module, LabExperiment, CourseOutcome
from .models import SEMESTER_CHOICES, COURSE_TYPE_CHOICES, SEE_TYPE_CHOICES, CONTENT_TYPE_CHOICES

class SyllabusForm(forms.ModelForm):
    class Meta:
        model = Syllabus
        fields = [
            'course_code','title','credits','semester','course_type',
            'see_type','content_type',
            'lec_hours','tut_hours','prac_hours','other_hours',
            'total_hours','lab_slots','cie_marks','total_marks','exam_hours',
            'total_hours','cie_marks','see_marks','total_marks','exam_hours',
            'objectives','teaching_learning', 'co_description',
            'lab_description','lab_prerequisites','lab_self_learning',
            'assessment_general_rules', 'assessment_cie', 'assessment_see',
            'weblinks_custom', 'weblinks_json', 'activity_based_learning',
            'copo_matrix',
        ]
        widgets = {
            'course_code':      forms.TextInput(attrs={'class':'form-control','placeholder':'e.g., 23CSE644'}),
            'title':            forms.TextInput(attrs={'class':'form-control','placeholder':'e.g., Computer Networks'}),
            'credits':          forms.NumberInput(attrs={'class':'form-control','min':0}),
            'semester':         forms.Select(attrs={'class':'form-select'}),
            'course_type':      forms.Select(attrs={'class':'form-select'}),
            'see_type':         forms.Select(attrs={'class':'form-select'}),
            'content_type':     forms.RadioSelect(attrs={'class':'form-check-input'}),
            'lec_hours':        forms.NumberInput(attrs={'class':'form-control text-center','min':0}),
            'tut_hours':        forms.NumberInput(attrs={'class':'form-control text-center','min':0}),
            'prac_hours':       forms.NumberInput(attrs={'class':'form-control text-center','min':0}),
            'other_hours':      forms.TextInput(attrs={'class':'form-control text-center','maxlength':5,'placeholder':'@'}),
            'total_hours':      forms.NumberInput(attrs={'class':'form-control','min':0}),
            'lab_slots':        forms.TextInput(attrs={'class':'form-control', 'placeholder':'e.g., 10-12'}),
            'see_marks':        forms.NumberInput(attrs={'class':'form-control','min':0}),
            'cie_marks':        forms.NumberInput(attrs={'class':'form-control','min':0}),
            'total_marks':      forms.NumberInput(attrs={'class':'form-control','min':0}),
            'exam_hours':       forms.NumberInput(attrs={'class':'form-control','min':0}),
            'objectives':       forms.Textarea(attrs={'class':'form-control','rows':4}),
            'teaching_learning':forms.Textarea(attrs={'class':'form-control','rows':5}),
            'co_description':   forms.Textarea(attrs={'class':'form-control','rows':2}), # <--- Added Widget
            'lab_description':  forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Lab course description...'}),
            'lab_prerequisites':forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Prerequisites...'}),
            'assessment_general_rules': forms.Textarea(attrs={'class':'form-control','rows':2}),
            'assessment_cie':           forms.Textarea(attrs={'class':'form-control','rows':2}),
            'assessment_see':           forms.Textarea(attrs={'class':'form-control','rows':2}),
            'weblinks_custom':          forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Any custom instructions...'}),
            'weblinks_json':            forms.HiddenInput(attrs={'id': 'hidden_weblinks_json'}),
            'activity_based_learning':  forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'1. Real world problem solving...'}),
            'lab_self_learning':forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Self-learning topics...'}),
            'copo_matrix': forms.HiddenInput(attrs={'id': 'hidden_copo_matrix'}),
        }

ModuleFormSet = inlineformset_factory(
    Syllabus, Module,
    fields=['module_number','title','teaching_hours','content',
            'has_hands_on','hands_on',
            'tb_number','tb_chapter','tb_section',
            'self_learning','prerequisites','rbt_levels'],
    extra=0, can_delete=True, 
    widgets={
        'module_number':  forms.HiddenInput(attrs={'class':'module-number-input'}), 
        'title':          forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Module 1: Introduction'}),
        'teaching_hours': forms.NumberInput(attrs={'class':'form-control','min':0}),
        'content':        forms.Textarea(attrs={'class':'form-control','rows':4,'placeholder':'Module description (required)'}),
        'has_hands_on':   forms.CheckboxInput(attrs={'class':'form-check-input handson-toggle'}),
        'hands_on':       forms.Textarea(attrs={'class':'form-control','rows':3,'placeholder':'Hands-on activities...'}),
        'tb_number':      forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. 1'}),
        'tb_chapter':     forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. Chapter 2'}),
        'tb_section':     forms.TextInput(attrs={'class':'form-control','placeholder':'e.g. 2.1, 2.3'}),
        'self_learning':  forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Self-learning topics...'}),
        'prerequisites':  forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Prerequisites...'}),
        'rbt_levels':     forms.HiddenInput(),
    }
)

LabExperimentFormSet = inlineformset_factory(
    Syllabus, LabExperiment,
    fields=['sl_no','title','is_additional'],
    extra=0, can_delete=True, 
    widgets={
        'sl_no':         forms.NumberInput(attrs={'class':'form-control text-center','min':1,'style':'width:70px;'}),
        'title':         forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Experiment / program title'}),
        'is_additional': forms.HiddenInput(),
    }
)

# --- NEW FORMSET FOR COURSE OUTCOMES ---
CourseOutcomeFormSet = inlineformset_factory(
    Syllabus, CourseOutcome,
    fields=['sl_no', 'description'],
    extra=0, can_delete=True,
    widgets={
        'sl_no': forms.HiddenInput(attrs={'class': 'co-sl-no'}),
        'description': forms.Textarea(attrs={'class':'form-control','rows':2,'placeholder':'Apply the fundamentals of...'}),
    }
)