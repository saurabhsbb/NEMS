from django.contrib import admin
from .models import (
    Faculty,
    FacultySubjectAssignment,
    QuestionPaper,
)

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):

    list_display = (
        "employee_id",
        "user",
        "department",
        "designation",
        "is_active",
    )

    list_filter = (
        "department",
        "designation",
        "is_active",
    )

    search_fields = (
        "employee_id",
        "user__first_name",
        "user__last_name",
        "user__username",
    )

@admin.register(FacultySubjectAssignment)
class FacultySubjectAssignmentAdmin(admin.ModelAdmin):

    list_display = (
        "academic_year",
        "curriculum",
        "subject",
        "faculty",
        "assigned_on",
        "is_active",
    )

    list_filter = (
        "academic_year",
        "curriculum",
        "is_active",
    )

    search_fields = (
        "subject__subject_name",
        "subject__subject_code",
        "faculty__employee_id",
        "faculty__user__first_name",
        "faculty__user__last_name",
    )

    readonly_fields = (
        "submitted_on",
    )

@admin.register(QuestionPaper)
class QuestionPaperAdmin(admin.ModelAdmin):

    list_display = (
        "faculty_subject_assignment",
        "question_paper_set",
        "uploaded_on",
    )

    list_filter = (
        "question_paper_set",
    )
