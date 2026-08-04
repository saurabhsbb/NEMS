from admissions.models import Student
from examinations.models import Examination
from django.conf import settings
from django.db import models
from registration.models import ExaminationRegistration
from academics.models import Subject
from evaluation.models import FacultySubjectAssignment

WORKFLOW_STATUS_CHOICES = [
    ("DRAFT", "Draft"),
    ("SUBMITTED", "Submitted"),
    ("RETURNED", "Returned"),
    ("APPROVED", "Approved"),
]

RESULT_STATUS_CHOICES = [
    ("PASS", "Pass"),
    ("FAIL", "Fail"),
]

RESULT_SOURCE_CHOICES = [
    ("HISTORICAL", "Historical Import"),
    ("LIVE", "Live Result"),
]

class ResultEntry(models.Model):

    examination_registration = models.ForeignKey(
        ExaminationRegistration,
        on_delete=models.PROTECT,
        related_name="result_entries",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
    )

    faculty_assignment = models.ForeignKey(
        FacultySubjectAssignment,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    workflow_status = models.CharField(
        max_length=15,
        choices=WORKFLOW_STATUS_CHOICES,
        default="DRAFT",
    )

    workflow_remarks = models.TextField(
        blank=True,
    )

    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Marks entered by Faculty

    class_test_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    attendance_assignment_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    theory_external_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    practical_internal_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    practical_external_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    # Calculated by ERP

    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    grade = models.CharField(
        max_length=2,
        blank=True,
    )

    grade_point = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    result_status = models.CharField(
        max_length=20,
        blank=True,
    )

    is_latest = models.BooleanField(
        default=True,
    )

    is_published = models.BooleanField(
        default=False,
    )

    published_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="published_results",
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = [
            "examination_registration",
            "subject",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "examination_registration",
                    "subject",
                ],
                name="unique_result_entry",
            ),
        ]

        
    def __str__(self):

        return (
            f"{self.examination_registration} - "
            f"{self.subject.subject_code}"
        )

class StudentAcademicResult(models.Model):

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="academic_results",
    )

    examination = models.ForeignKey(
        Examination,
        on_delete=models.PROTECT,
        related_name="academic_results",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="academic_results",
    )

    # Marks

    class_test_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    attendance_assignment_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    theory_external_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    practical_internal_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    practical_external_marks = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
    )

    percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
    )

    grade = models.CharField(
        max_length=2,
    )

    grade_point = models.PositiveSmallIntegerField()

    result_status = models.CharField(
        max_length=10,
        choices=RESULT_STATUS_CHOICES,
    )

    source = models.CharField(
        max_length=15,
        choices=RESULT_SOURCE_CHOICES,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
    )

    updated_on = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "student",
            "subject",
            "-created_on",
        ]

    def __str__(self):

        return (
            f"{self.student.roll_number} - "
            f"{self.subject.subject_code} - "
            f"{self.grade}"
        )

class SemesterResult(models.Model):

    RESULT_STATUS_CHOICES = [
        ("PASS", "Pass"),
        ("FAIL", "Fail"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="semester_results",
    )

    examination = models.ForeignKey(
        Examination,
        on_delete=models.PROTECT,
        related_name="semester_results",
    )

    semester = models.PositiveSmallIntegerField()

    registered_credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    earned_credits = models.DecimalField(
        max_digits=5,
        decimal_places=2,
    )

    sgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
    )

    result_status = models.CharField(
        max_length=10,
        choices=RESULT_STATUS_CHOICES,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
    )

    updated_on = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "student",
            "semester",
        ]

        unique_together = (
            "student",
            "examination",
            "semester",
        )

    def __str__(self):

        return (
            f"{self.student.roll_number} - "
            f"Sem {self.semester} - "
            f"{self.sgpa}"
        )

class CombinedResult(models.Model):

    RESULT_STATUS_CHOICES = [
        ("PASS", "Pass"),
        ("FAIL", "Fail"),
    ]

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
        related_name="combined_results",
    )

    examination = models.ForeignKey(
        Examination,
        on_delete=models.PROTECT,
        related_name="combined_results",
    )

    registered_credits = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    earned_credits = models.DecimalField(
        max_digits=6,
        decimal_places=2,
    )

    cgpa = models.DecimalField(
        max_digits=4,
        decimal_places=2,
    )

    result_status = models.CharField(
        max_length=10,
        choices=RESULT_STATUS_CHOICES,
    )

    created_on = models.DateTimeField(
        auto_now_add=True,
    )

    updated_on = models.DateTimeField(
        auto_now=True,
    )

    class Meta:

        ordering = [
            "student",
        ]

        unique_together = (
            "student",
            "examination",
        )

    def __str__(self):

        return (
            f"{self.student.roll_number} - "
            f"{self.cgpa}"
        )

class ResultPublication(models.Model):

    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
    )

    semester = models.PositiveSmallIntegerField()

    is_published = models.BooleanField(
        default=False,
    )

    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
    )

    published_on = models.DateTimeField(
        null=True,
        blank=True,
    )

    class Meta:

        ordering = [
            "examination",
            "semester",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "examination",
                    "semester",
                ],

                name="unique_result_publication",

            )

        ]

    def __str__(self):

        return (
            f"{self.examination} - Semester {self.semester}"
        )
