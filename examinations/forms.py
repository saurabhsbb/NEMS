from django import forms

from .models import (
    ExaminationType,
    Examination,
    ExaminationSemester,
    AssessmentWindow,
)

class ExaminationTypeForm(forms.ModelForm):

    class Meta:
        model = ExaminationType

        fields = [
            "code",
            "name",
            "is_active",
        ]

class ExaminationForm(forms.ModelForm):

    class Meta:

        model = Examination

        fields = [
            "examination_code",
            "examination_name",
            "examination_type",
            "academic_year",
            "registration_start_date",
            "registration_end_date",
            "status",
            "is_active",
            "remarks",
        ]

        widgets = {
            "registration_start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "registration_end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }

class ExaminationSemesterForm(forms.ModelForm):

    SEMESTER_CHOICES = [
        (1, "Semester I"),
        (2, "Semester II"),
        (3, "Semester III"),
        (4, "Semester IV"),
        (5, "Semester V"),
        (6, "Semester VI"),
    ]

    semester = forms.ChoiceField(
        choices=SEMESTER_CHOICES,
    )

    class Meta:

        model = ExaminationSemester

        fields = [
            "examination",
            "semester",
        ]

class AssessmentWindowForm(forms.ModelForm):

    class Meta:

        model = AssessmentWindow

        fields = [
            "examination",
            "assessment_type",
            "start_date",
            "end_date",
        ]

        widgets = {
            "start_date": forms.DateInput(
                attrs={"type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"type": "date"}
            ),
        }
