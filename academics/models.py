from django.db import models
from django.core.exceptions import ValidationError


SUBJECT_TYPES = [
    ("THEORY", "Theory"),
    ("PRACTICAL", "Practical"),
    ("THEORY_PRACTICAL", "Theory + Practical"),
]

class Department(models.Model):

    department_code = models.CharField(
        max_length=20,
        unique=True,
    )

    department_name = models.CharField(
        max_length=200,
        unique=True,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:

        ordering = [
            "department_name",
        ]

    def __str__(self):

        return self.department_name

class Programme(models.Model):
    programme_code = models.CharField(max_length=20, unique=True)
    programme_name = models.CharField(max_length=200, unique=True)
    department = models.ForeignKey(
        Department,
        on_delete=models.PROTECT,
        
        
    )
    duration_in_semesters = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["programme_name"]

    def __str__(self):
        return self.programme_name

class AcademicYear(models.Model):

    academic_year = models.CharField(
        max_length=9,
        unique=True,
    )

    display_order = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "display_order",
        ]

    def __str__(self):
        return self.academic_year

class RegistrationCycle(models.Model):

    cycle_code = models.CharField(
        max_length=10,
        unique=True,
    )

    cycle_name = models.CharField(
        max_length=20,
        unique=True,
    )

    display_order = models.PositiveIntegerField(
        default=1,
    )

    is_active = models.BooleanField(
        default=True,
    )

    class Meta:
        ordering = [
            "display_order",
        ]

    def __str__(self):
        return self.cycle_name

class ProgrammeEntryType(models.Model):
    entry_type_code = models.CharField(max_length=20, unique=True)
    entry_type_name = models.CharField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["entry_type_name"]

    def __str__(self):
        return self.entry_type_name

class AdmissionCategory(models.Model):
    category_code = models.CharField(max_length=20, unique=True)
    category_name = models.CharField(max_length=100, unique=True)

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["category_name"]

    def __str__(self):
        return self.category_name

class Curriculum(models.Model):
    curriculum_code = models.CharField(max_length=20, unique=True)
    curriculum_name = models.CharField(max_length=100)

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT
    )

    total_semesters = models.PositiveSmallIntegerField()

    applicable_from_academic_year = models.PositiveSmallIntegerField()


    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["curriculum_name"]

    def __str__(self):
        return f"{self.curriculum_name} ({self.programme.programme_name})"

class Subject(models.Model):
    subject_code = models.CharField(max_length=20, unique=True)
    subject_name = models.CharField(max_length=200)

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.PROTECT
    )

    semester = models.PositiveSmallIntegerField()

    display_order = models.PositiveSmallIntegerField()

    subject_type = models.CharField(
    max_length=20,
    choices=SUBJECT_TYPES
    )
    
    credits = models.DecimalField(
        max_digits=4,
        decimal_places=1
    )

    is_elective = models.BooleanField(default=False)

    elective_group = models.ForeignKey(
        "ElectiveGroup",
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    theory_internal_max = models.PositiveSmallIntegerField(default=0)

    class_test_max = models.PositiveSmallIntegerField(
        default=20
    )

    attendance_assignment_max = models.PositiveSmallIntegerField(
        default=10
    )

    theory_internal_min = models.PositiveSmallIntegerField(default=0)

    theory_external_max = models.PositiveSmallIntegerField(default=0)

    theory_external_min = models.PositiveSmallIntegerField(default=0)

    practical_internal_max = models.PositiveSmallIntegerField(default=0)

    practical_internal_min = models.PositiveSmallIntegerField(default=0)

    practical_external_max = models.PositiveSmallIntegerField(default=0)

    practical_external_min = models.PositiveSmallIntegerField(default=0)

    

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["semester", "display_order"]

    def clean(self):
        super().clean()

        if self.is_elective and self.elective_group is None:
            raise ValidationError({
                "elective_group": "Elective Group is mandatory for elective subjects."
            })

        if not self.is_elective and self.elective_group is not None:
            raise ValidationError({
                "elective_group": "Elective Group must be blank for non-elective subjects."
            })

        if self.subject_type in ["THEORY", "THEORY_PRACTICAL"]:

            if (
                self.class_test_max
                + self.attendance_assignment_max
                != self.theory_internal_max
            ):
                raise ValidationError({
                    "class_test_max":
                        "Class Test + Attendance & Assignment must equal Theory Internal Maximum."
                })

    def __str__(self):
        return f"{self.subject_code} - {self.subject_name}"

class ElectiveGroup(models.Model):
    group_code = models.CharField(max_length=20, unique=True)
    group_name = models.CharField(max_length=100)

    curriculum = models.ForeignKey(
        Curriculum,
        on_delete=models.PROTECT
    )

    semester = models.PositiveSmallIntegerField()

    subjects_to_choose = models.PositiveSmallIntegerField()

    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["semester", "group_name"]

    def __str__(self):
        return self.group_name
