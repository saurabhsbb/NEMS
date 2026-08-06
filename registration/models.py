from academics.models import Subject
from django.db import models
from django.conf import settings
from academics.models import (
    Programme,
    AcademicYear,
    RegistrationCycle,
    Curriculum,
)
from admissions.models import Student


REGISTRATION_STATUS = [
    ("SUBMITTED", "Submitted"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
    ("CANCELLED", "Cancelled"),
]

REGISTRATION_WINDOW_STATUS = [
    ("OPEN", "Open"),
    ("CLOSED", "Closed"),
]


class SemesterRegistrationWindow(models.Model):

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
    )

    programme = models.ForeignKey(
        "academics.Programme",
        on_delete=models.PROTECT,
    )

    registration_cycle = models.ForeignKey(
        RegistrationCycle,
        on_delete=models.PROTECT,
    )

    registration_start_date = models.DateField()

    registration_end_date = models.DateField()

    registration_status = models.CharField(
        max_length=10,
        choices=REGISTRATION_WINDOW_STATUS,
        default="CLOSED",
    )

    remarks = models.TextField(
        blank=True
    )

    class Meta:
        ordering = [
            "-academic_year",
            "programme",
            "registration_cycle",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "academic_year",
                    "programme",
                    "registration_cycle",
                ],
                name="unique_registration_window",
            )
        ]

    def __str__(self):
        return (
            f"{self.academic_year} - "
            f"{self.programme} - "
            f"Semester {self.registration_cycle}"
        )

class SemesterRegistration(models.Model):

    registration_window = models.ForeignKey(
        SemesterRegistrationWindow,
        on_delete=models.PROTECT,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
    )

    semester = models.PositiveSmallIntegerField()

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.PROTECT,
    )

    registration_date = models.DateTimeField(
        auto_now_add=True
    )

    registration_status = models.CharField(
        max_length=20,
        choices=REGISTRATION_STATUS,
        default="SUBMITTED",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_semester_registrations",
    )

    approved_on = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True
    )

    class Meta:
        ordering = [
            "student",
            "semester",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "registration_window",
                    "student",
                ],
                name="unique_student_registration",
            )
        ]

    def __str__(self):
        return (
            f"{self.student} - Semester {self.semester}"
        )

EXAMINATION_REGISTRATION_STATUS = [
    ("SUBMITTED", "Submitted"),
    ("APPROVED", "Approved"),
    ("REJECTED", "Rejected"),
    ("CANCELLED", "Cancelled"),
]


class ExaminationRegistration(models.Model):

    examination = models.ForeignKey(
        "examinations.Examination",
        on_delete=models.PROTECT,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
    )

    semester_registration = models.ForeignKey(
        SemesterRegistration,
        on_delete=models.PROTECT,
        related_name="exam_registrations",
    )

    registration_date = models.DateTimeField(
        auto_now_add=True
    )

    registration_status = models.CharField(
        max_length=20,
        choices=EXAMINATION_REGISTRATION_STATUS,
        default="SUBMITTED",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_exam_registrations",
    )

    approved_on = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "-registration_date",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "examination",
                    "student",
                ],
                name="unique_exam_registration",
            )
        ]

    def __str__(self):
        return (
            f"{self.student} - {self.examination}"
        )

class BacklogRegistration(models.Model):

    BACKLOG_REGISTRATION_STATUS = [

        ("SUBMITTED", "Submitted"),

        ("APPROVED", "Approved"),

        ("REJECTED", "Rejected"),

    ]

    examination = models.ForeignKey(
        "examinations.Examination",
        on_delete=models.PROTECT,
    )

    student = models.ForeignKey(
        Student,
        on_delete=models.PROTECT,
    )

    registration_date = models.DateTimeField(
        auto_now_add=True,
    )

    registration_status = models.CharField(
        max_length=20,
        choices=BACKLOG_REGISTRATION_STATUS,
        default="SUBMITTED",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_backlog_registrations",
    )

    approved_on = models.DateTimeField(
        null=True,
        blank=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:

        ordering = [
            "-registration_date",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "examination",
                    "student",
                ],

                name="unique_backlog_registration",

            )

        ]

    def __str__(self):

        return (
            f"{self.student} - {self.examination}"
        )

class BacklogRegistrationSubject(models.Model):

    backlog_registration = models.ForeignKey(
        BacklogRegistration,
        on_delete=models.CASCADE,
        related_name="subjects",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
    )

    class Meta:

        ordering = [
            "subject",
        ]

        constraints = [

            models.UniqueConstraint(

                fields=[
                    "backlog_registration",
                    "subject",
                ],

                name="unique_backlog_subject",

            )

        ]

    def __str__(self):

        return (
            f"{self.backlog_registration.student.roll_number} - "
            f"{self.subject.subject_code}"
        )

