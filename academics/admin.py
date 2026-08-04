from django.contrib import admin
from .models import Department
from .models import (
    Programme,
    ProgrammeEntryType,
    Curriculum,
    Subject,
    ElectiveGroup,
    AdmissionCategory,
    AcademicYear,
    RegistrationCycle,
)


@admin.register(Programme)
class ProgrammeAdmin(admin.ModelAdmin):
    list_display = (
        "programme_code",
        "programme_name",
        "department",
        "duration_in_semesters",
        "is_active",
    )


@admin.register(ProgrammeEntryType)
class ProgrammeEntryTypeAdmin(admin.ModelAdmin):
    list_display = (
        "entry_type_code",
        "entry_type_name",
        "is_active",
    )


@admin.register(Curriculum)
class CurriculumAdmin(admin.ModelAdmin):
    list_display = (
        "curriculum_name",
        "programme",
        "applicable_from_academic_year",
        "is_active",
    )


@admin.register(ElectiveGroup)
class ElectiveGroupAdmin(admin.ModelAdmin):
    list_display = (
        "group_code",
        "group_name",
        "curriculum",
        "semester",
        "subjects_to_choose",
        "is_active",
    )


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):

    list_display = (
        "subject_code",
        "subject_name",
        "curriculum",
        "semester",
        "subject_type",
        "credits",
        "theory_internal_max",
        "class_test_max",
        "attendance_assignment_max",
        "theory_external_max",
        "practical_internal_max",
        "practical_external_max",
        "is_active",
    )

    list_filter = (
        "curriculum",
        "semester",
        "subject_type",
        "is_active",
    )

    search_fields = (
        "subject_code",
        "subject_name",
    )

@admin.register(AdmissionCategory)
class AdmissionCategoryAdmin(admin.ModelAdmin):
    list_display = (
        "category_code",
        "category_name",
        "is_active",
    )

@admin.register(AcademicYear)
class AcademicYearAdmin(admin.ModelAdmin):

    list_display = (
        "academic_year",
        "display_order",
        "is_active",
    )


@admin.register(RegistrationCycle)
class RegistrationCycleAdmin(admin.ModelAdmin):

    list_display = (
        "cycle_code",
        "cycle_name",
        "display_order",
        "is_active",
    )

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):

    list_display = (
        "department_code",
        "department_name",
        "is_active",
    )

    list_filter = (
        "is_active",
    )

    search_fields = (
        "department_code",
        "department_name",
    )
