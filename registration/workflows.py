from .models import SemesterRegistrationWindow
from django.utils import timezone

def open_registration(window):
    """
    Open Semester Registration
    """

    if window.registration_status == "OPEN":
        return

    window.registration_status = "OPEN"
    window.save()


def close_registration(window):
    """
    Close Semester Registration
    """

    if window.registration_status == "CLOSED":
        return

    window.registration_status = "CLOSED"
    window.save()

def approve_registration(
    registration,
    approved_by,
):
    """
    Approve Semester Registration.
    """

    if registration.registration_status == "APPROVED":
        return

    registration.registration_status = "APPROVED"
    registration.approved_by = approved_by
    registration.approved_on = timezone.now()

    registration.save()

def reject_registration(
    registration,
):
    """
    Reject Semester Registration.
    """

    if registration.registration_status == "REJECTED":
        return

    registration.registration_status = "REJECTED"

    registration.save()
