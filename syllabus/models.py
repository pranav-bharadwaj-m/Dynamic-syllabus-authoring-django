from django.db import models
from django.contrib.auth.models import User

STATUS_CHOICES = (
    ('DRAFT', 'Draft'), 
    ('PENDING_HOD', '⏳ Pending HOD Approval'),
    ('PENDING_ADMIN', '⏳ Pending Admin Approval'), 
    ('APPROVED', '✅ Go ahead with implementation'),
    ('REJECTED_BY_HOD', '❌ Rejected by HOD'),
    ('REJECTED_BY_ADMIN', '❌ Rejected by Admin'),
)
SEMESTER_CHOICES = [('I','I'),('II','II'),('III','III'),('IV','IV'),('V','V'),('VI','VI'),('VII','VII'),('VIII','VIII')]
COURSE_TYPE_CHOICES = [('PCC','PCC'),('IPCC','IPCC'),('PCCL','PCCL'),('PEC','PEC'),('OEC','OEC'),('ETC','ETC'),('AEC','AEC'),('PRJ','PRJ'),('HSMC','HSMC'),('NCMC','NCMC')]
SEE_TYPE_CHOICES = [('Theory','Theory'),('Practical','Practical')]
CONTENT_TYPE_CHOICES = [('theory_only','Only Theory'),('theory_with_lab','Theory with Lab'),('lab_only','Only Lab')]
RBT_CHOICES = [('L1','L1: Remembering'),('L2','L2: Understanding'),('L3','L3: Applying'),('L4','L4: Analyzing'),('L5','L5: Evaluating'),('L6','L6: Creating')]
RBT_DISPLAY = {'L1':'Remembering','L2':'Understanding','L3':'Applying','L4':'Analyzing','L5':'Evaluating','L6':'Creating'}


class Syllabus(models.Model):
    course_code       = models.CharField(max_length=20, unique=True, default = "")
    title             = models.CharField(max_length=200, default="")
    credits           = models.IntegerField(default=0)
    semester          = models.CharField(max_length=5, choices=SEMESTER_CHOICES, default='I')
    course_type       = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='PCC')
    see_type          = models.CharField(max_length=20, choices=SEE_TYPE_CHOICES, default='Theory')
    content_type      = models.CharField(max_length=20, choices=CONTENT_TYPE_CHOICES, default='theory_only')

    lec_hours   = models.IntegerField(default=0)
    tut_hours   = models.IntegerField(default=0)
    prac_hours  = models.IntegerField(default=0)
    other_hours = models.CharField(max_length=5, default=0)
    total_hours = models.IntegerField(default=0)
    lab_slots   = models.CharField(max_length=50, blank=True, default='')
    cie_marks   = models.IntegerField(default=0)
    see_marks   = models.IntegerField(default=0)
    total_marks = models.IntegerField(default=0)
    exam_hours  = models.IntegerField(default=0)

    objectives        = models.TextField(blank=True)
    teaching_learning = models.TextField(blank=True)
    co_description    = models.TextField(default="", blank=True)
    
    # Lab-only course-level fields
    lab_description   = models.TextField(blank=True)
    lab_prerequisites = models.TextField(blank=True)
    lab_self_learning = models.TextField(blank=True)

    # --- Assessment Details ---
    assessment_general_rules = models.TextField(blank=True)
    assessment_cie           = models.TextField(blank=True)
    assessment_see           = models.TextField(blank=True)

    # Structured textbooks stored as JSON lists
    # Each entry: {sl_no, title, author, edition_year, publisher}
    textbooks_json       = models.JSONField(default=list, blank=True)
    reference_books_json = models.JSONField(default=list, blank=True)

    # --- Web Links & Activities ---
    weblinks_custom         = models.TextField(blank=True)
    weblinks_json           = models.JSONField(default=list, blank=True)
    activity_based_learning = models.TextField(blank=True)

    created_by  = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    status      = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    copo_matrix = models.JSONField(default=dict, blank=True)
    latest_remark = models.TextField(blank=True, help_text="Reason for rejection or approval comments.")

    @property
    def teaching_hours_display(self):
        return f"{self.lec_hours}:{self.tut_hours}:{self.prac_hours}:{self.other_hours}"

    def __str__(self):
        return f"{self.course_code} - {self.title}"


class Module(models.Model):
    syllabus       = models.ForeignKey(Syllabus, related_name='modules', on_delete=models.CASCADE)
    module_number  = models.PositiveIntegerField(default=1)
    title          = models.CharField(max_length=200)
    teaching_hours = models.IntegerField(default=0)
    content        = models.TextField(blank=True)   # description (required for theory)
    has_hands_on   = models.BooleanField(default=False)
    hands_on       = models.TextField(blank=True)
    tb_number      = models.CharField(max_length=10, blank=True)
    tb_chapter     = models.CharField(max_length=100, blank=True)
    tb_section     = models.CharField(max_length=200, blank=True)
    self_learning  = models.TextField(blank=True)
    prerequisites  = models.TextField(blank=True)
    rbt_levels     = models.JSONField(default=list, blank=True)  # e.g. ["L1","L2"]
    course_objectives = models.TextField(blank=True)  # kept for compat
    is_deleted     = models.BooleanField(default=False)

    class Meta:
        ordering = ['module_number', 'id']

    @property
    def rbt_display(self):
        return ', '.join(f"{l} \u2013 {RBT_DISPLAY.get(l, l)}" for l in (self.rbt_levels or []))

    def __str__(self):
        return self.title


class LabExperiment(models.Model):
    syllabus     = models.ForeignKey(Syllabus, related_name='lab_experiments', on_delete=models.CASCADE)
    sl_no        = models.PositiveIntegerField()
    title        = models.TextField()
    is_additional = models.BooleanField(default=False)

    class Meta:
        ordering = ['is_additional', 'sl_no']

    def __str__(self):
        return f"{self.sl_no}. {self.title}"


class ApprovalLog(models.Model):
    syllabus  = models.ForeignKey(Syllabus, on_delete=models.CASCADE, related_name='approval_logs')
    actor     = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    action    = models.CharField(max_length=100)
    comments  = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.syllabus.course_code} - {self.action}"
    
class CourseOutcome(models.Model):
    syllabus = models.ForeignKey(Syllabus, related_name='course_outcomes', on_delete=models.CASCADE)
    sl_no = models.PositiveIntegerField(default=1)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['sl_no']

    def __str__(self):
        return f"CO{self.sl_no}"