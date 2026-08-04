from django.utils import timezone
from django.db import models
from academics.models import AcademicYear
EXAMINATION_STATUS = [

    ("DRAFT", "Draft"),

    ("REGISTRATION_OPEN", "Registration Open"),

    ("REGISTRATION_CLOSED", "Registration Closed"),

    ("MARKS_ENTRY", "Marks Entry"),

    ("RESULT_PROCESSING", "Result Processing"),

    ("RESULT_PUBLISHED", "Result Published"),

    ("CLOSED", "Closed"),

]

class ExaminationType(models.Model):

    code = models.CharField(
        max_length=10,
        unique=True,
    )

    name = models.CharField(
        max_length=100,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "code",
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Examination(models.Model):

    examination_code = models.CharField(
        max_length=30,
        unique=True,
    )

    examination_name = models.CharField(
        max_length=200,
    )

    examination_type = models.ForeignKey(
        ExaminationType,
        on_delete=models.PROTECT,
    )

    academic_year = models.ForeignKey(
        AcademicYear,
        on_delete=models.PROTECT,
    )

    registration_start_date = models.DateField()

    registration_end_date = models.DateField()

    status = models.CharField(
        max_length=30,
        choices=EXAMINATION_STATUS,
        default="DRAFT",
    )

    is_active = models.BooleanField(
        default=True,
    )

    remarks = models.TextField(
        blank=True,
    )

    class Meta:
        ordering = [
            "-academic_year",
            "examination_name",
        ]

    def __str__(self):
        return f"{self.examination_code} - {self.examination_name}"

class ExaminationSemester(models.Model):

    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
    )

    semester = models.PositiveSmallIntegerField()

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
                name="unique_examination_semester",
            ),
        ]

    def __str__(self):

        return (
            f"{self.examination.examination_code} - "
            f"Semester {self.semester}"
        )

ASSESSMENT_TYPE = [
    ("CLASS_TEST", "Class Test"),
    ("ATTENDANCE_ASSIGNMENT", "Attendance & Assignment"),
    ("END_SEMESTER", "End Semester Assessment"),
]


class AssessmentWindow(models.Model):
    @property
    def current_status(self):

        today = timezone.localdate()

        if today < self.start_date:
            return "Not Started"

        if self.start_date <= today <= self.end_date:
            return "Open"

        return "Closed"
    examination = models.ForeignKey(
        Examination,
        on_delete=models.CASCADE,
    )

    assessment_type = models.CharField(
        max_length=30,
        choices=ASSESSMENT_TYPE,
    )

    start_date = models.DateField()

    end_date = models.DateField()

    class Meta:

        ordering = [
            "examination",
            "start_date",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "examination",
                    "assessment_type",
                ],
                name="unique_assessment_window",
            ),
        ]

    def __str__(self):

        return (
            f"{self.examination.examination_code} - "
            f"{self.get_assessment_type_display()}"
        )
