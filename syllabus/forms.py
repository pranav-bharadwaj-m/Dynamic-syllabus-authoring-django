from django import forms
from django.forms import inlineformset_factory
from .models import Syllabus, Module, SEMESTER_CHOICES, COURSE_TYPE_CHOICES, SEE_TYPE_CHOICES


class SyllabusForm(forms.ModelForm):
    class Meta:
        model = Syllabus
        fields = [
            'course_code', 'title', 'credits', 'semester', 'course_type',
            'see_type', 'lec_hours', 'tut_hours', 'prac_hours', 'other_hours',
            'total_hours', 'cie_marks', 'total_marks', 'exam_hours',
            'objectives', 'teaching_learning',
            'textbooks', 'reference_books', 'copo_matrix',
        ]
        widgets = {
            'course_code': forms.TextInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'credits': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'semester': forms.Select(attrs={'class': 'form-select'}),
            'course_type': forms.Select(attrs={'class': 'form-select'}),
            'see_type': forms.Select(attrs={'class': 'form-select'}),
            'lec_hours': forms.NumberInput(attrs={'class': 'form-control text-center', 'min': 0, 'placeholder': '0'}),
            'tut_hours': forms.NumberInput(attrs={'class': 'form-control text-center', 'min': 0, 'placeholder': '0'}),
            'prac_hours': forms.NumberInput(attrs={'class': 'form-control text-center', 'min': 0, 'placeholder': '0'}),
            'other_hours': forms.TextInput(attrs={'class': 'form-control text-center', 'placeholder': '@', 'maxlength': 5}),
            'total_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cie_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'exam_hours': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'objectives': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 5,
                'placeholder': 'This course will enable students to:\n1. ...\n2. ...',
            }),
            'teaching_learning': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 6,
                'placeholder': 'Describe teaching-learning strategies...',
            }),
            'textbooks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'reference_books': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'copo_matrix': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'JSON format'}),
        }


ModuleFormSet = inlineformset_factory(
    Syllabus,
    Module,
    fields=['title', 'teaching_hours', 'course_objectives', 'content', 'hands_on', 'rbt_levels'],
    extra=1,
    can_delete=True,
    widgets={
        'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Module 1: Introduction'}),
        'teaching_hours': forms.NumberInput(attrs={'class': 'form-control'}),
        'course_objectives': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        'hands_on': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        'rbt_levels': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. L1, L2'}),
    }
)