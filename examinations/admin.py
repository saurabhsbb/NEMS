from django.contrib import admin
from .models import (
    ExaminationType,
    Examination,
    ExaminationSemester,
    AssessmentWindow,
)

@admin.register(AssessmentWindow)
class AssessmentWindowAdmin(admin.ModelAdmin):
    list_display = (
        "examination",
        "assessment_type",
        "start_date",
        "end_date",
    )

    list_filter = (
        "assessment_type",
        "examination",
    )

@admin.register(ExaminationType)
class ExaminationTypeAdmin(admin.ModelAdmin):
    list_display = (
        "code",
        "name",
        "is_active",
    )
    search_fields = (
        "code",
        "name",
    )


@admin.register(Examination)
class ExaminationAdmin(admin.ModelAdmin):
    list_display = (
        "examination_code",
        "examination_name",
        "examination_type",
        "academic_year",
        "registration_start_date",
        "registration_end_date",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "examination_type",
        "is_active",
    )

    search_fields = (
        "examination_code",
        "examination_name",
    )
