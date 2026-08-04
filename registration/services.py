from django.utils import timezone
from academics.models import Curriculum
from .models import (
    SemesterRegistration,
    SemesterRegistrationWindow,
)


def register_student(
    student,
    semester,
):
    """
    Register a student for a semester.
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

    registration = SemesterRegistration.objects.create(
        student=student,
        semester=semester,
        curriculum=curriculum,
        registration_window=registration_window,
        registration_date=timezone.now(),
        registration_status="SUBMITTED",
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
