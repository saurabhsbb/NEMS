from django.utils import timezone
from django.db import transaction
from academics.models import (
    Curriculum,
    ElectiveGroup,
    Subject,
)
from .models import (
    SemesterRegistration,
    SemesterRegistrationWindow,
    StudentElectiveSelection,
)

@transaction.atomic
def register_student(
    student,
    semester,
    elective_selections=None,
):
    """
    Register a student for a semester and save
    the student's elective selections.

    elective_selections must be a dictionary:

        {
            elective_group_id: subject_id,
        }

    For semesters without elective groups, the dictionary
    may be empty or None.
    """

    if student.admission_status != "CONFIRMED":
        raise ValueError(
            "Admission is not confirmed."
        )

    registration_window = (
        SemesterRegistrationWindow.objects.get(
            programme=student.programme,
            registration_status="OPEN",
        )
    )

    if SemesterRegistration.objects.filter(
        registration_window=registration_window,
        student=student,
    ).exists():

        raise ValueError(
            "Student is already registered for this semester."
        )

    curriculum = Curriculum.objects.get(
        programme=student.programme,
        is_active=True,
    )

    elective_selections = elective_selections or {}

    elective_groups = list(
        ElectiveGroup.objects.filter(
            curriculum=curriculum,
            semester=semester,
            is_active=True,
        )
    )

    expected_group_ids = {
        group.id
        for group in elective_groups
    }

    submitted_group_ids = {
        int(group_id)
        for group_id in elective_selections.keys()
    }

    if submitted_group_ids != expected_group_ids:

        raise ValueError(
            "Please select a subject for every required elective group."
        )

    validated_selections = []

    for group in elective_groups:

        subject_id = elective_selections.get(
            group.id
        )

        if subject_id is None:
            raise ValueError(
                f"Please select a subject for {group.group_name}."
            )

        subject = Subject.objects.filter(
            id=subject_id,
            curriculum=curriculum,
            semester=semester,
            elective_group=group,
            is_elective=True,
            is_active=True,
        ).first()

        if subject is None:
            raise ValueError(
                "Invalid elective subject selected."
            )

        validated_selections.append(
            (
                group,
                subject,
            )
        )

    registration = SemesterRegistration.objects.create(
        student=student,
        semester=semester,
        curriculum=curriculum,
        registration_window=registration_window,
        registration_date=timezone.now(),
        registration_status="SUBMITTED",
    )

    for group, subject in validated_selections:

        StudentElectiveSelection.objects.create(
            semester_registration=registration,
            elective_group=group,
            subject=subject,
        )

    return registration

def approve_registration(
    registration,
    approved_by,
    remarks,
):
    """
    Approve a semester registration.
    """

    registration.registration_status = "APPROVED"
    registration.approved_by = approved_by
    registration.approved_on = timezone.now()
    registration.remarks = remarks

    registration.save()

    return registration


def reject_registration(
    registration,
    approved_by,
    remarks,
):
    """
    Reject a semester registration.
    """

    registration.registration_status = "REJECTED"
    registration.approved_by = approved_by
    registration.approved_on = timezone.now()
    registration.remarks = remarks

    registration.save()

    return registration

def approve_exam_registration(
    registration,
    approved_by,
    remarks,
):

    registration.registration_status = "APPROVED"

    registration.approved_by = approved_by

    registration.approved_on = timezone.now()

    registration.remarks = remarks

    registration.save()


def reject_exam_registration(
    registration,
    approved_by,
    remarks,
):

    registration.registration_status = "REJECTED"

    registration.approved_by = approved_by

    registration.approved_on = timezone.now()

    registration.remarks = remarks

    registration.save()
