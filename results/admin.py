from .models import ResultPublication
from django.contrib import admin
from .models import ResultEntry
from .models import ResultEntry
from .models import (
    ResultEntry,
    StudentAcademicResult,
    SemesterResult,
    CombinedResult,
)
admin.site.register(ResultPublication)

@admin.register(ResultEntry)
class ResultEntryAdmin(admin.ModelAdmin):

    list_display = (
        "id",
        "examination_registration",
        "subject",
        "workflow_status",
        "result_status",
        "is_published",
        "published_by",
        "published_at",
    )

    readonly_fields = (
        "published_by",
        "published_at",
    )

    list_filter = (
        "workflow_status",
        "result_status",
        "is_published",
        "published_by",
    )

    search_fields = (
        "examination_registration__student__roll_number",
        "subject__subject_name",
    )

@admin.register(StudentAcademicResult)
class StudentAcademicResultAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "subject",
        "examination",
        "grade",
        "grade_point",
        "result_status",
        "source",
    )

    list_filter = (
        "source",
        "result_status",
        "examination",
    )

    search_fields = (
        "student__roll_number",
        "student__full_name",
        "subject__subject_name",
    )

@admin.register(SemesterResult)
class SemesterResultAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "semester",
        "examination",
        "sgpa",
        "result_status",
    )

    list_filter = (
        "semester",
        "examination",
        "result_status",
    )

    search_fields = (
        "student__roll_number",
        "student__first_name",
        "student__last_name",
    )

@admin.register(CombinedResult)
class CombinedResultAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "examination",
        "cgpa",
        "result_status",
    )

    list_filter = (
        "examination",
        "result_status",
    )

    search_fields = (
        "student__roll_number",
        "student__first_name",
        "student__last_name",
    )
