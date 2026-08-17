from django.db.models import Q
from examinations.models import (
    Examination,
    ExaminationSemester,
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.contrib import messages
from academics.models import (
    Subject,
    ElectiveGroup,
)
from academics.models import Subject
from .models import (
    SemesterRegistration,
    SemesterRegistrationWindow,
    ExaminationRegistration,
    StudentElectiveSelection,
)

from .services import (
    register_student,
    approve_registration,
    reject_registration,
    approve_exam_registration,
    reject_exam_registration,
)
from admissions.models import Student

@login_required
def semester_registration(request):

    student = Student.objects.get(
        user=request.user
    )

    registration_window = (
        SemesterRegistrationWindow.objects.filter(
            programme=student.programme,
            registration_status="OPEN",
        ).first()
    )

    existing_registration = None

    if registration_window:

        existing_registration = (
            SemesterRegistration.objects.filter(
                registration_window=registration_window,
                student=student,
            ).first()
        )

    semester_choices = []

    if (
        registration_window
        and
        existing_registration is None
    ):

        if (
            registration_window.registration_cycle.cycle_code
            == "ODD"
        ):

            semester_choices = [1, 3, 5]

        else:

            semester_choices = [2, 4, 6]

    return render(
        request,
        "accounts/semester_registration.html",
        {
            "student": student,
            "registration_window": registration_window,
            "semester_choices": semester_choices,
            "existing_registration": existing_registration,
        },
    )


@login_required
def review_registration(request):

    if request.method != "POST":
        return redirect("semester_registration")

    semester = int(
        request.POST.get("semester")
    )

    student = Student.objects.get(
        user=request.user
    )

    registration_window = (
        SemesterRegistrationWindow.objects.filter(
            programme=student.programme,
            registration_status="OPEN",
        ).first()
    )

    if registration_window is None:
        messages.error(
            request,
            "No registration window is currently open."
        )

        return redirect("semester_registration")

    from academics.models import Curriculum

    curriculum = Curriculum.objects.get(
        programme=student.programme,
        is_active=True,
    )

    elective_groups = (
        ElectiveGroup.objects.filter(
            curriculum=curriculum,
            semester=semester,
            is_active=True,
        )
        .prefetch_related("subject_set")
        .order_by("id")
    )

    for group in elective_groups:

        group.available_subjects = (
            group.subject_set.filter(
                is_active=True,
                is_elective=True,
            )
            .order_by("display_order")
        )

    return render(
        request,
        "accounts/review_registration.html",
        {
            "student": student,
            "semester": semester,
            "registration_window": registration_window,
            "elective_groups": elective_groups,
        },
    )

@login_required
def submit_registration(request):

    if request.method != "POST":
        return redirect("semester_registration")

    student = Student.objects.get(
        user=request.user
    )

    semester = int(
        request.POST.get("semester")
    )

    elective_selections = {}

    for key, value in request.POST.items():

        if key.startswith("elective_group_"):

            group_id = int(
                key.replace("elective_group_", "")
            )

            subject_id = int(value)

            elective_selections[group_id] = subject_id

    try:

        register_student(
            student,
            semester,
            elective_selections=elective_selections,
        )

    except ValueError as e:

        messages.error(
            request,
            str(e)
        )

        return redirect(
            "semester_registration"
        )

    return render(
        request,
        "accounts/registration_success.html",
    )

@login_required
def depm_pending_registrations(request):

    registrations = SemesterRegistration.objects.filter(
        registration_status="SUBMITTED"
    ).select_related("student")

    context = {
        "registrations": registrations,
    }

    return render(
        request,
        "registration/depm/pending_registrations.html",
        context,
    )

@login_required
def depm_review_registration(request, registration_id):

    registration = SemesterRegistration.objects.select_related(
        "student",
        "student__programme",
        "student__programme_entry_type",
        "student__admission_category",
        "registration_window",
        "registration_window__registration_cycle",
    ).get(
        pk=registration_id
    )

    if request.method == "POST":

        action = request.POST.get("action")
        remarks = request.POST.get("remarks", "").strip()

        if action == "approve":

            approve_registration(
                registration=registration,
                approved_by=request.user,
                remarks=remarks,
            )

            messages.success(
                request,
                "Semester registration approved successfully."
            )

        elif action == "reject":

            reject_registration(
                registration=registration,
                approved_by=request.user,
                remarks=remarks,
            )

            messages.error(
                request,
                "Semester registration rejected successfully."
            )

        return redirect("depm_pending_registrations")

    entry_code = registration.student.programme_entry_type.entry_type_code

    show_no_previous_history = (
        (entry_code == "REG" and registration.semester == 1)
        or
        (entry_code == "LAT" and registration.semester == 3)
    )

    context = {
        "registration": registration,
        "show_no_previous_history": show_no_previous_history,
    }

    return render(
        request,
        "registration/depm/review_registration.html",
        context,
    )

@login_required
def examination_registration(request):

    student = Student.objects.get(
        user=request.user
    )

    semester_registration = (
        SemesterRegistration.objects.filter(
            student=student,
            registration_status="APPROVED",
        )
        .order_by("-registration_date")
        .first()
    )

    if semester_registration is None:

        return render(
            request,
            "registration/examination_registration.html",
            {
                "student": student,
                "semester_registration": None,
            },
        )

    examination = (
        Examination.objects.filter(
            examination_type__code="REG",
            status="REGISTRATION_OPEN",
        )
        .first()
    )

    eligible = False

    existing_registration = None

    if examination:

        eligible = ExaminationSemester.objects.filter(
            examination=examination,
            semester=semester_registration.semester,
        ).exists()

        existing_registration = ExaminationRegistration.objects.filter(
            examination=examination,
            student=student,
        ).first()

    subjects = Subject.objects.none()

    if eligible:

        selected_elective_subject_ids = (
            StudentElectiveSelection.objects.filter(
                semester_registration=semester_registration,
            ).values_list(
                "subject_id",
                flat=True,
            )
        )

        subjects = Subject.objects.filter(
            curriculum=semester_registration.curriculum,
            semester=semester_registration.semester,
            is_active=True,
        ).filter(
            Q(is_elective=False)
            |
            Q(
                is_elective=True,
                id__in=selected_elective_subject_ids,
            )
        ).order_by(
            "display_order"
        )

    context = {
        "student": student,
        "semester_registration": semester_registration,
        "examination": examination,
        "eligible": eligible,
        "subjects": subjects,
        "existing_registration": existing_registration,
    }

    if (
        request.method == "POST"
        and examination
        and eligible
    ):

        existing_registration = ExaminationRegistration.objects.filter(
            examination=examination,
            student=student,
        ).first()

        if existing_registration:

            if existing_registration.registration_status in [
                "REJECTED",
                "CANCELLED",
            ]:

                existing_registration.semester_registration = semester_registration

                existing_registration.registration_status = "SUBMITTED"

                existing_registration.approved_by = None

                existing_registration.approved_on = None

                existing_registration.remarks = ""

                existing_registration.save()

                messages.success(
                    request,
                    "Examination registration submitted again successfully."
                )

        else:

            ExaminationRegistration.objects.create(
                examination=examination,
                student=student,
                semester_registration=semester_registration,
            )

            messages.success(
                request,
                "Examination registration submitted successfully."
            )

        return redirect(
            "student_dashboard"
        )

    return render(
        request,
        "registration/examination_registration.html",
        context,
    )

@login_required
def coe_pending_exam_registrations(request):

    registrations = ExaminationRegistration.objects.filter(
        registration_status="SUBMITTED"
    ).select_related(
        "student",
        "examination",
        "semester_registration",
    )

    context = {
        "registrations": registrations,
    }

    return render(
        request,
        "registration/coe/pending_exam_registrations.html",
        context,
    )

@login_required
def coe_review_exam_registration(request, registration_id):

    registration = ExaminationRegistration.objects.select_related(
        "student",
        "student__programme",
        "examination",
        "semester_registration",
    ).get(
        pk=registration_id
    )

    if request.method == "POST":

        action = request.POST.get("action")

        remarks = request.POST.get(
            "remarks",
            "",
        ).strip()

        if action == "approve":

            approve_exam_registration(
                registration=registration,
                approved_by=request.user,
                remarks=remarks,
            )

            messages.success(
                request,
                "Examination registration approved successfully."
            )

        elif action == "reject":

            reject_exam_registration(
                registration=registration,
                approved_by=request.user,
                remarks=remarks,
            )

            messages.error(
                request,
                "Examination registration rejected successfully."
            )

        return redirect(
            "coe_pending_exam_registrations"
        )

    subjects = Subject.objects.filter(
        curriculum=registration.semester_registration.curriculum,
        semester=registration.semester_registration.semester,
        is_active=True,
    ).order_by(
        "display_order"
    )

    context = {
        "registration": registration,
        "subjects": subjects,
    }

    return render(
        request,
        "registration/coe/review_exam_registration.html",
        context,
    )
