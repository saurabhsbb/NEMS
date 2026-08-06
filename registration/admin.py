from django.contrib import admin
from .workflows import (
    open_registration,
    close_registration,
    approve_registration,
    reject_registration,
)
from .models import (
    SemesterRegistrationWindow,
    SemesterRegistration,
    ExaminationRegistration,
)

from .models import (
    SemesterRegistrationWindow,
    SemesterRegistration,
    ExaminationRegistration,
    BacklogRegistration,
    BacklogRegistrationSubject,
)

admin.site.register(BacklogRegistration)
admin.site.register(BacklogRegistrationSubject)
@admin.register(SemesterRegistrationWindow)
class SemesterRegistrationWindowAdmin(admin.ModelAdmin):

    actions = (
        "open_registration_action",
        "close_registration_action",
    )

    fields = (
        "academic_year",
        "programme",
        "registration_cycle",
        "registration_start_date",
        "registration_end_date",
        "remarks",
    )

    list_display = (
        "academic_year",
        "programme",
        "registration_cycle",
        "registration_start_date",
        "registration_end_date",
        "registration_status",
    )

    list_filter = (
        "academic_year",
        "programme",
        "registration_status",
    )

    search_fields = (
        "academic_year",
    )

    @admin.action(description="Open Registration")
    def open_registration_action(
        self,
        request,
        queryset,
    ):

        for window in queryset:
            open_registration(window)


    @admin.action(description="Close Registration")
    def close_registration_action(
        self,
        request,
        queryset,
    ):

        for window in queryset:
            close_registration(window)


@admin.register(SemesterRegistration)
class SemesterRegistrationAdmin(admin.ModelAdmin):
    
    actions = (
    "approve_registration_action",
    "reject_registration_action",
    )

    list_display = (
        "student",
        "semester",
        "registration_status",
        "approved_by",
        "approved_on",
        "registration_date",
    )

    list_filter = (
        "registration_window",
        "semester",
        "registration_status",
    )

    search_fields = (
        "student__roll_number",
        "student__student_name",
        "student__aadhaar_number",
    )

    ordering = (
        "semester",
        "student__roll_number",
    )

    readonly_fields = (
        "student",
        "semester",
        "curriculum",
        "registration_window",
        "registration_date",
    )

    @admin.action(description="Approve Registration")
    def approve_registration_action(
        self,
        request,
        queryset,
    ):

        for registration in queryset:

            approve_registration(
                registration,
                request.user,
            )

    @admin.action(description="Reject Registration")
    def reject_registration_action(
        self,
        request,
        queryset,
    ):

        for registration in queryset:

            reject_registration(
                registration,
            )

@admin.register(ExaminationRegistration)
class ExaminationRegistrationAdmin(admin.ModelAdmin):

    list_display = (
        "student",
        "examination",
        "registration_status",
        "registration_date",
    )

    list_filter = (
        "examination",
        "registration_status",
    )

    search_fields = (
        "student__roll_number",
        "student__student_name",
    )

    ordering = (
        "-registration_date",
    )

    readonly_fields = (
        "registration_date",
    )
