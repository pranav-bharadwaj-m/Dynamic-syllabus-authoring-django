from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = (
    ('DRAFT', 'Draft'),
    ('FACULTY_APPROVED', '✅ Faculty Approved'),
    ('BOS_APPROVED', '✅ BOS Approved'),
    ('HOD_APPROVED', '✅ HOD Approved'),
    ('REJECTED', '❌ Rejected / Revision Required'),
)

SEMESTER_CHOICES = [
    ('I', 'I'), ('II', 'II'), ('III', 'III'), ('IV', 'IV'),
    ('V', 'V'), ('VI', 'VI'), ('VII', 'VII'), ('VIII', 'VIII'),
]

COURSE_TYPE_CHOICES = [
    ('PCC', 'PCC'), ('IPCC', 'IPCC'), ('PCCL', 'PCCL'), ('PEC', 'PEC'),
    ('OEC', 'OEC'), ('ETC', 'ETC'), ('AEC', 'AEC'),
    ('PRJ', 'PRJ'), ('HSMC', 'HSMC'), ('NCMC', 'NCMC'),
]

SEE_TYPE_CHOICES = [
    ('Theory', 'Theory'),
    ('Practical', 'Practical'),
]


class Syllabus(models.Model):
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    credits = models.IntegerField(default=3)
    semester = models.CharField(max_length=5, choices=SEMESTER_CHOICES, default='VI')
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='ETC')
    see_type = models.CharField(max_length=20, choices=SEE_TYPE_CHOICES, default='Theory')

    # Teaching Hours/Week broken into L:T:P:O
    lec_hours = models.IntegerField(default=3, verbose_name='L')
    tut_hours = models.IntegerField(default=0, verbose_name='T')
    prac_hours = models.IntegerField(default=0, verbose_name='P')
    other_hours = models.CharField(max_length=5, default='@', verbose_name='O')

    total_hours = models.IntegerField(default=40)
    cie_marks = models.IntegerField(default=50)
    total_marks = models.IntegerField(default=100)
    exam_hours = models.IntegerField(default=3)

    # Course content sections (user-authored)
    objectives = models.TextField(blank=True, verbose_name='Course Objectives')
    teaching_learning = models.TextField(blank=True, verbose_name='Teaching-Learning Process')

    # Resources
    textbooks = models.TextField(blank=True, help_text='List primary textbooks')
    reference_books = models.TextField(blank=True, help_text='List reference materials')

    # Workflow
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')

    # CO-PO mapping
    copo_matrix = models.JSONField(default=dict, blank=True)

    @property
    def teaching_hours_display(self):
        return f"{self.lec_hours}:{self.tut_hours}:{self.prac_hours}:{self.other_hours}"

    def __str__(self):
        return f"{self.course_code} - {self.title} ({self.get_status_display()})"


class Module(models.Model):
    syllabus = models.ForeignKey(Syllabus, related_name='modules', on_delete=models.CASCADE)
    title = models.CharField(max_length=200, verbose_name='Module Title')
    teaching_hours = models.IntegerField(default=0)
    course_objectives = models.TextField(blank=True)
    content = models.TextField(blank=True, verbose_name='Content & Details')
    hands_on = models.TextField(blank=True, verbose_name='Hands-on / Self-Learning')
    rbt_levels = models.CharField(max_length=100, blank=True, help_text='e.g., L1, L2, L3')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class ApprovalLog(models.Model):
    syllabus = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='approval_logs')
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action = models.CharField(max_length=100)
    comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.syllabus.course_code} - {self.action} at {self.timestamp}"