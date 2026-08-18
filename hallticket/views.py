from datetime import date, time

from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.db import transaction

from academics.models import Subject
from examinations.models import Examination
from registration.models import ExaminationRegistration

from .models import (
    ExaminationSubjectSchedule,
    HallTicketPublication,
)


@login_required
def hall_ticket_examinations(request):

    examinations = Examination.objects.filter(
        examination_type__code__in=["REG", "BLG"],
        is_active=True,
    ).order_by(
        "-academic_year",
        "examination_code",
    )

    return render(
        request,
        "hallticket/coe_examinations.html",
        {
            "examinations": examinations,
        },
    )


@login_required
def hall_ticket_schedule(request, examination_id):

    examination = get_object_or_404(
        Examination,
        pk=examination_id,
        examination_type__code__in=["REG", "BLG"],
        is_active=True,
    )

    publication = HallTicketPublication.objects.filter(
        examination=examination,
    ).first()

    # Once Hall Tickets are published, the schedule is locked.
    if request.method == "POST" and publication and publication.is_published:

        messages.error(
            request,
            "Hall Tickets have already been published. "
            "The examination schedule cannot be modified.",
        )

        return redirect(
            "hall_ticket_schedule",
            examination_id=examination.id,
        )

    subjects = Subject.objects.none()

    # ---------------------------------------------------------
    # REGULAR EXAMINATION SUBJECTS
    # ---------------------------------------------------------

    if examination.examination_type.code == "REG":

        registrations = (
            ExaminationRegistration.objects.filter(
                examination=examination,
                registration_status="APPROVED",
            )
            .select_related(
                "semester_registration",
            )
            .prefetch_related(
                "semester_registration__elective_selections__subject",
            )
        )

        subject_ids = set()

        for registration in registrations:

            semester_registration = (
                registration.semester_registration
            )

            registered_subjects = Subject.objects.filter(
                curriculum=semester_registration.curriculum,
                semester=semester_registration.semester,
                is_active=True,
                is_elective=False,
            )

            for subject in registered_subjects:
                subject_ids.add(subject.id)

            for selection in (
                semester_registration.elective_selections.all()
            ):
                subject_ids.add(selection.subject_id)

        subjects = Subject.objects.filter(
            id__in=subject_ids,
            is_active=True,
        ).order_by(
            "semester",
            "display_order",
        )

    # ---------------------------------------------------------
    # BACKLOG EXAMINATION SUBJECTS
    # ---------------------------------------------------------

    elif examination.examination_type.code == "BLG":

        subjects = Subject.objects.filter(
            backlogregistrationsubject__backlog_registration__examination=examination,
            backlogregistrationsubject__backlog_registration__registration_status="APPROVED",
            is_active=True,
        ).distinct().order_by(
            "semester",
            "display_order",
        )

    # ---------------------------------------------------------
    # SAVE / VALIDATE EXAMINATION SUBJECT SCHEDULE
    # ---------------------------------------------------------

    if request.method == "POST":

        errors = []
        proposed_schedules = []

        # -----------------------------------------------------
        # Examination status validation
        # -----------------------------------------------------

        if examination.status != "REGISTRATION_CLOSED":

            errors.append(
                "Hall Ticket scheduling is allowed only after "
                "examination registration is closed."
            )

        # -----------------------------------------------------
        # Validate every subject
        # -----------------------------------------------------

        for subject in subjects:

            exam_date = request.POST.get(
                f"exam_date_{subject.id}",
                "",
            ).strip()

            start_time = request.POST.get(
                f"start_time_{subject.id}",
                "",
            ).strip()

            end_time = request.POST.get(
                f"end_time_{subject.id}",
                "",
            ).strip()

            # -------------------------------------------------
            # Required fields
            # -------------------------------------------------

            if not exam_date:

                errors.append(
                    f"{subject.subject_code} - "
                    f"{subject.subject_name}: Exam date is required."
                )

                continue

            if not start_time:

                errors.append(
                    f"{subject.subject_code} - "
                    f"{subject.subject_name}: Start time is required."
                )

                continue

            if not end_time:

                errors.append(
                    f"{subject.subject_code} - "
                    f"{subject.subject_name}: End time is required."
                )

                continue

            # -------------------------------------------------
            # Date validation
            # -------------------------------------------------

            try:

                parsed_date = date.fromisoformat(
                    exam_date
                )

            except ValueError:

                errors.append(
                    f"{subject.subject_code} - "
                    f"{subject.subject_name}: Invalid examination date."
                )

                continue

            # -------------------------------------------------
            # Time validation
            # -------------------------------------------------

            try:

                parsed_start_time = time.fromisoformat(
                    start_time
                )

                parsed_end_time = time.fromisoformat(
                    end_time
                )

            except ValueError:

                errors.append(
                    f"{subject.subject_code} - "
                    f"{subject.subject_name}: Invalid examination time."
                )

                continue

            # -------------------------------------------------
            # Start / End time validation
            # -------------------------------------------------

            if parsed_end_time <= parsed_start_time:

                errors.append(
                    f"{subject.subject_code} - "
                    f"{subject.subject_name}: End time must be "
                    f"later than start time."
                )

                continue

            proposed_schedules.append(
                {
                    "subject": subject,
                    "exam_date": parsed_date,
                    "start_time": parsed_start_time,
                    "end_time": parsed_end_time,
                }
            )

        # -----------------------------------------------------
        # Check overlapping subjects
        # -----------------------------------------------------

        proposed_schedules.sort(
            key=lambda item: (
                item["exam_date"],
                item["start_time"],
            )
        )

        for index in range(
            len(proposed_schedules)
        ):

            current = proposed_schedules[index]

            for previous in proposed_schedules[:index]:

                if (
                    previous["exam_date"]
                    != current["exam_date"]
                ):
                    continue

                if (
                    current["start_time"]
                    < previous["end_time"]
                    and
                    current["end_time"]
                    > previous["start_time"]
                ):

                    errors.append(
                        f"Schedule conflict: "
                        f"{previous['subject'].subject_code} "
                        f"({previous['subject'].subject_name}) "
                        f"overlaps with "
                        f"{current['subject'].subject_code} "
                        f"({current['subject'].subject_name}) "
                        f"on {current['exam_date']}."
                    )

        # -----------------------------------------------------
        # If validation failed, save NOTHING
        # -----------------------------------------------------

        if errors:

            for error in errors:

                messages.error(
                    request,
                    error,
                )

        else:

            # -------------------------------------------------
            # Atomic database update
            # -------------------------------------------------

            with transaction.atomic():

                for item in proposed_schedules:

                    ExaminationSubjectSchedule.objects.update_or_create(

                        examination=examination,

                        subject=item["subject"],

                        defaults={
                            "exam_date": item["exam_date"],
                            "start_time": item["start_time"],
                            "end_time": item["end_time"],
                        },
                    )

            messages.success(
                request,
                "Examination schedule validated and saved successfully.",
            )

            return redirect(
                "hall_ticket_schedule",
                examination_id=examination.id,
            )

    # ---------------------------------------------------------
    # LOAD EXISTING SCHEDULES
    # ---------------------------------------------------------

    schedules = ExaminationSubjectSchedule.objects.filter(
        examination=examination,
        subject__in=subjects,
    ).select_related(
        "subject",
    )

    schedule_map = {
        schedule.subject_id: schedule
        for schedule in schedules
    }

    for subject in subjects:

        subject.schedule = schedule_map.get(
            subject.id
        )

    publication = HallTicketPublication.objects.filter(
        examination=examination,
    ).first()

    if (
        request.method == "POST"
        and publication
        and publication.is_published
    ):

        messages.error(
            request,
            "Hall Tickets have already been published. "
            "The examination schedule cannot be modified.",
        )

        return redirect(
            "hall_ticket_schedule",
            examination_id=examination.id,
        )

    return render(
        request,
        "hallticket/coe_schedule.html",
        {
            "examination": examination,
            "subjects": subjects,
            "schedule_map": schedule_map,
            "publication": publication,
        },
    )

@login_required
def hall_ticket_publish(request, examination_id):

    if request.method != "POST":
        return redirect(
            "hall_ticket_schedule",
            examination_id=examination_id,
        )

    examination = get_object_or_404(
        Examination,
        pk=examination_id,
        examination_type__code__in=["REG", "BLG"],
        is_active=True,
    )

    # ---------------------------------------------------------
    # Registration must be closed
    # ---------------------------------------------------------

    if examination.status != "REGISTRATION_CLOSED":

        messages.error(
            request,
            "Hall Tickets can be published only after "
            "examination registration is closed.",
        )

        return redirect(
            "hall_ticket_schedule",
            examination_id=examination.id,
        )

    # ---------------------------------------------------------
    # Prevent re-publication
    # ---------------------------------------------------------

    publication = HallTicketPublication.objects.filter(
        examination=examination,
    ).first()

    if publication and publication.is_published:

        messages.warning(
            request,
            "Hall Tickets for this examination "
            "have already been published.",
        )

        return redirect(
            "hall_ticket_schedule",
            examination_id=examination.id,
        )

    # ---------------------------------------------------------
    # Determine applicable subjects
    # ---------------------------------------------------------

    subjects = Subject.objects.none()

    if examination.examination_type.code == "REG":

        registrations = (
            ExaminationRegistration.objects.filter(
                examination=examination,
                registration_status="APPROVED",
            )
            .select_related(
                "semester_registration",
            )
            .prefetch_related(
                "semester_registration__elective_selections__subject",
            )
        )

        subject_ids = set()

        for registration in registrations:

            semester_registration = (
                registration.semester_registration
            )

            registered_subjects = Subject.objects.filter(
                curriculum=semester_registration.curriculum,
                semester=semester_registration.semester,
                is_active=True,
                is_elective=False,
            )

            for subject in registered_subjects:
                subject_ids.add(subject.id)

            for selection in (
                semester_registration.elective_selections.all()
            ):
                subject_ids.add(selection.subject_id)

        subjects = Subject.objects.filter(
            id__in=subject_ids,
            is_active=True,
        )

    elif examination.examination_type.code == "BLG":

        subjects = Subject.objects.filter(
            backlogregistrationsubject__backlog_registration__examination=examination,
            backlogregistrationsubject__backlog_registration__registration_status="APPROVED",
            is_active=True,
        ).distinct()

    # ---------------------------------------------------------
    # At least one subject must exist
    # ---------------------------------------------------------

    subject_ids = set(
        subjects.values_list(
            "id",
            flat=True,
        )
    )

    if not subject_ids:

        messages.error(
            request,
            "Hall Tickets cannot be published because "
            "no approved examination subjects were found.",
        )

        return redirect(
            "hall_ticket_schedule",
            examination_id=examination.id,
        )

    # ---------------------------------------------------------
    # Get SAVED schedules from database
    # ---------------------------------------------------------

    schedules = list(
        ExaminationSubjectSchedule.objects.filter(
            examination=examination,
            subject_id__in=subject_ids,
        ).select_related(
            "subject",
        )
    )

    scheduled_subject_ids = {
        schedule.subject_id
        for schedule in schedules
    }

    # ---------------------------------------------------------
    # Every subject must have a saved schedule
    # ---------------------------------------------------------

    missing_subject_ids = (
        subject_ids - scheduled_subject_ids
    )

    if missing_subject_ids:

        missing_subjects = Subject.objects.filter(
            id__in=missing_subject_ids,
        ).order_by(
            "semester",
            "display_order",
        )

        for subject in missing_subjects:

            messages.error(
                request,
                f"{subject.subject_code} - "
                f"{subject.subject_name}: "
                f"Schedule is missing.",
            )

        messages.error(
            request,
            "Hall Tickets cannot be published until "
            "all applicable subjects are scheduled.",
        )

        return redirect(
            "hall_ticket_schedule",
            examination_id=examination.id,
        )

    # ---------------------------------------------------------
    # Validate SAVED schedules
    # ---------------------------------------------------------

    errors = []

    for schedule in schedules:

        if not schedule.exam_date:
            errors.append(
                f"{schedule.subject.subject_code} - "
                f"{schedule.subject.subject_name}: "
                f"Exam date is missing."
            )

        if not schedule.start_time:
            errors.append(
                f"{schedule.subject.subject_code} - "
                f"{schedule.subject.subject_name}: "
                f"Start time is missing."
            )

        if not schedule.end_time:
            errors.append(
                f"{schedule.subject.subject_code} - "
                f"{schedule.subject.subject_name}: "
                f"End time is missing."
            )

        if (
            schedule.start_time
            and schedule.end_time
            and schedule.end_time <= schedule.start_time
        ):
            errors.append(
                f"{schedule.subject.subject_code} - "
                f"{schedule.subject.subject_name}: "
                f"End time must be later than start time."
            )

    # ---------------------------------------------------------
    # Check overlapping SAVED schedules
    # ---------------------------------------------------------

    schedules.sort(
        key=lambda schedule: (
            schedule.exam_date,
            schedule.start_time,
        )
    )

    for index in range(len(schedules)):

        current = schedules[index]

        for previous in schedules[:index]:

            if previous.exam_date != current.exam_date:
                continue

            if (
                current.start_time < previous.end_time
                and current.end_time > previous.start_time
            ):

                errors.append(
                    "Schedule conflict: "
                    f"{previous.subject.subject_code} "
                    f"({previous.subject.subject_name}) "
                    "overlaps with "
                    f"{current.subject.subject_code} "
                    f"({current.subject.subject_name}) "
                    f"on {current.exam_date}."
                )

    # ---------------------------------------------------------
    # Do not publish if saved schedule is invalid
    # ---------------------------------------------------------

    if errors:

        for error in errors:
            messages.error(
                request,
                error,
            )

        messages.error(
            request,
            "Hall Tickets cannot be published because "
            "the saved examination schedule is invalid.",
        )

        return redirect(
            "hall_ticket_schedule",
            examination_id=examination.id,
        )

    # ---------------------------------------------------------
    # Publish
    # ---------------------------------------------------------

    from django.utils import timezone

    publication, created = (
        HallTicketPublication.objects.get_or_create(
            examination=examination,
        )
    )

    publication.is_published = True
    publication.published_on = timezone.now()
    publication.published_by = request.user

    publication.save()

    messages.success(
        request,
        "Hall Tickets published successfully.",
    )

    return redirect(
        "hall_ticket_schedule",
        examination_id=examination.id,
    )
