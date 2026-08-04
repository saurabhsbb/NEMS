from django.conf import settings
from django.db import models
from django.utils import timezone
from academics.models import (
    Department,
    AcademicYear,
    Programme,
    Curriculum,
    Subject,
)
from .validators import validate_pdf

class Faculty(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
    )

    employee_id = models.CharField(
        max_length=20,
        unique=True,
    )

    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
    )

    designation = models.CharField(
        max_length=100,
    )

    mobile_number = models.CharField(
        max_length=10,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:

        ordering = [
            "employee_id",
        ]

    def __str__(self):

        return (
            f"{self.employee_id} - "
            f"{self.user.get_full_name()}"
        )

class FacultySubjectAssignment(models.Model):

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
    )

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.PROTECT,
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
    )

    faculty = models.ForeignKey(
        Faculty,
        on_delete=models.PROTECT,
    )

    question_paper_evaluation_minutes = models.FileField(
        upload_to="question_paper_minutes/",
        validators=[
            validate_pdf,
        ],
        null=True,
        blank=True,
    )

    question_paper_confidentiality_declaration_accepted = models.BooleanField(
        default=False,
    )

    submitted_on = models.DateTimeField(
        null=True,
        blank=True,
    )

    assigned_on = models.DateTimeField(
        default=timezone.now,
    )

    is_active = models.BooleanField(
        default=True,
    )

    selected_question_paper_set = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
    )

    class Meta:

        ordering = (
            "curriculum",
            "subject",
        )

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "academic_year",
                    "subject",
                ],
                name="unique_subject_assignment",
            )
        ]

    def __str__(self):

        return (
            f"{self.subject} -> "
            f"{self.faculty}"
        )

class QuestionPaper(models.Model):

    SET_CHOICES = (
        (1, "Set 1"),
        (2, "Set 2"),
        (3, "Set 3"),
    )

    faculty_subject_assignment = models.ForeignKey(
        FacultySubjectAssignment,
        on_delete=models.PROTECT,
    )

    question_paper_set = models.PositiveSmallIntegerField(
        choices=SET_CHOICES,
    )

    question_paper_file = models.FileField(
        upload_to="question_papers/",
        validators=[
            validate_pdf,
        ],
    )

    uploaded_on = models.DateTimeField(
        auto_now_add=True,
    )

    class Meta:

        ordering = (
            "faculty_subject_assignment",
            "question_paper_set",
        )

        unique_together = (
            "faculty_subject_assignment",
            "question_paper_set",
        )

    def __str__(self):

        return (
            f"{self.faculty_subject_assignment} "
            f"- Set {self.question_paper_set}"
        )
