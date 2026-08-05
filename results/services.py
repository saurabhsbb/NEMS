from decimal import Decimal

from .models import (
    StudentAcademicResult,
    SemesterResult,
    CombinedResult,
)

def calculate_sgpa(
    student,
    examination,
    semester,
):
    """
    Calculate and store Semester Result.
    """

    academic_results = (
        StudentAcademicResult.objects.filter(
            student=student,
            examination=examination,
            subject__semester=semester,
        ).select_related("subject")
    )

    registered_credits = Decimal("0")

    earned_credits = Decimal("0")

    weighted_grade_points = Decimal("0")

    semester_result = "PASS"

    for result in academic_results:

        credits = result.subject.credits

        registered_credits += credits

        weighted_grade_points += (
            credits * result.grade_point
        )

        if result.result_status == "PASS":

            earned_credits += credits

        else:

            semester_result = "FAIL"

    if registered_credits > 0:

        sgpa = (
            weighted_grade_points
            / registered_credits
        )

    else:

        sgpa = Decimal("0.00")

    SemesterResult.objects.update_or_create(

        student=student,

        examination=examination,

        semester=semester,

        defaults={

            "registered_credits": registered_credits,

            "earned_credits": earned_credits,

            "sgpa": sgpa,

            "result_status": semester_result,

        },
    )

def calculate_cgpa(
    student,
    examination,
):
    """
    Calculate and store Combined Result.
    """

    current_semester = SemesterResult.objects.get(
        student=student,
        examination=examination,
    ).semester

    semester_results = (
        SemesterResult.objects.filter(
            student=student,
            semester__lte=current_semester,
        ).order_by("semester")
    )

    registered_credits = Decimal("0")

    earned_credits = Decimal("0")

    weighted_sgpa = Decimal("0")

    result_status = "PASS"

    for semester_result in semester_results:

        registered_credits += (
            semester_result.registered_credits
        )

        earned_credits += (
            semester_result.earned_credits
        )

        weighted_sgpa += (

            semester_result.sgpa

            *

            semester_result.earned_credits

        )

        if semester_result.result_status == "FAIL":

            result_status = "FAIL"

    if registered_credits > 0:

        cgpa = (
            weighted_sgpa
            /
            earned_credits
        )

    else:

        cgpa = Decimal("0.00")

    CombinedResult.objects.update_or_create(

        student=student,

        examination=examination,

        defaults={

            "registered_credits": registered_credits,

            "earned_credits": earned_credits,

            "cgpa": cgpa,

            "result_status": result_status,

        },
    )
