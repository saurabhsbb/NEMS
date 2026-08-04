from django.contrib import admin
from .workflows import confirm_admission
from .models import Student
from django.urls import path
from .views import import_students_view

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    
    fields = (
        "student_name",
        "father_name",
        "mother_name",
        "aadhaar_number",
        "mobile_number",
        "parent_mobile_number",
	"email",              # NEW
        "date_of_birth",
	"gender",             # NEW
        "blood_group",
        "programme",
        "programme_entry_type",
        "admission_category",
        "admission_academic_year",
        "remarks",
        "documents_verified",
    )

    list_display = (
        "student_name",
        "roll_number",
        "programme",
        "admission_academic_year",
        "documents_verified",
        "admission_status",
        "is_active",
    )

    list_display_links = (
        "student_name",
    )

    search_fields = (
        "roll_number",
        "student_name",
        "aadhaar_number",
    )

    list_filter = (
        "programme",
        "admission_academic_year",
        "documents_verified",
        "is_active",
    )

    actions = [
        "confirm_admission_action",
    ]

    def get_urls(self):
        urls = super().get_urls()

        custom_urls = [
            path(
                "import-students/",
                self.admin_site.admin_view(import_students_view),
                name="student-import",
            ),
	]

        return custom_urls + urls

    @admin.action(description="Confirm Admission")
    def confirm_admission_action(self, request, queryset):
        for student in queryset:
            confirm_admission(student)
