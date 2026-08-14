from decimal import Decimal
from examinations.models import ExaminationSemester
from results.models import StudentAcademicResult
from .models import (
    StudentAcademicResult,
    SemesterResult,
    CombinedResult,
)

def get_live_attempt_number(
    student,
    subject,
    examination,
):
    """
    Return the attempt number for a LIVE result.

    If a LIVE result for the same student, subject, and
    examination already exists, reuse its attempt number.

    Otherwise, create the next attempt number after the
    student's existing history for that subject.
    """

    existing_live_result = (
        StudentAcademicResult.objects.filter(
            student=student,
            subject=subject,
            examination=examination,
            source="LIVE",
        )
        .order_by("-attempt_number")
        .first()
    )

    if existing_live_result:
        return existing_live_result.attempt_number

    latest_result = (
        StudentAcademicResult.objects.filter(
            student=student,
            subject=subject,
        )
        .order_by("-attempt_number")
        .first()
    )

    if latest_result:
        return latest_result.attempt_number + 1

    return 0

def calculate_sgpa(
    student,
    examination,
    semester,
):
    """
    Calculate and store Semester Result
    using the effective/latest attempt for
    each subject in the semester.
    """

    academic_results = get_effective_results(
        student=student,
        semester=semester,
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

            "registered_credits":
                registered_credits,

            "earned_credits":
                earned_credits,

            "sgpa":
                sgpa,

            "result_status":
                semester_result,

        },
    )


def calculate_cgpa(
    student,
    examination,
):
    """
    Calculate and store Combined Result
    using the effective/latest attempt for
    each subject.

    Failed subjects contribute:

        0 grade points to the numerator

        their full credits to the denominator

    Historical attempts superseded by a later
    attempt are not included.
    """

    effective_results = get_effective_results(
        student=student,
    )

    registered_credits = Decimal("0")

    earned_credits = Decimal("0")

    weighted_grade_points = Decimal("0")

    result_status = "PASS"

    for result in effective_results:

        credits = result.subject.credits

        registered_credits += credits

        weighted_grade_points += (
            credits * result.grade_point
        )

        if result.result_status == "PASS":

            earned_credits += credits

        else:

            result_status = "FAIL"

    if registered_credits > 0:

        cgpa = (
            weighted_grade_points
            / registered_credits
        )

    else:

        cgpa = Decimal("0.00")

    CombinedResult.objects.update_or_create(

        student=student,

        examination=examination,

        defaults={

            "registered_credits":
                registered_credits,

            "earned_credits":
                earned_credits,

            "cgpa":
                cgpa,

            "result_status":
                result_status,

        },
    )

def get_backlog_subjects(
    student,
    examination,
):

    mapped_semesters = list(

        ExaminationSemester.objects.filter(
            examination=examination,
        ).values_list(
            "semester",
            flat=True,
        )

    )

    academic_results = (

        StudentAcademicResult.objects.filter(
            student=student,
            subject__semester__in=mapped_semesters,
        )
        .select_related("subject")
        .order_by(
            "subject_id",
            "-created_on",
        )

    )

    latest_results = {}

    for result in academic_results:

        if result.subject_id not in latest_results:

            latest_results[result.subject_id] = result

    failed_subjects = []

    for result in latest_results.values():

        if result.result_status == "FAIL":

            failed_subjects.append(result.subject)

    print("--------------------------------")
    print("Failed Subjects")
    for subject in failed_subjects:
        print(subject.subject_code, subject.subject_name)
    print("--------------------------------")

    return failed_subjects

def calculate_backlog_result(entry):
    """
    Calculate total marks, percentage, grade, grade point,
    and result status for a backlog result entry.
    """

    subject = entry.subject

    theory_internal = (
        (entry.class_test_marks or 0)
        + (entry.attendance_assignment_marks or 0)
    )

    total_marks = (
        theory_internal
        + (entry.theory_external_marks or 0)
        + (entry.practical_internal_marks or 0)
        + (entry.practical_external_marks or 0)
    )

    maximum_marks = (
        subject.theory_internal_max
        + subject.theory_external_max
        + subject.practical_internal_max
        + subject.practical_external_max
    )

    if maximum_marks > 0:
        percentage = (
            total_marks * 100
        ) / maximum_marks
    else:
        percentage = 0

    grade = ""
    grade_point = None
    result_status = ""

    # Overall percentage rule
    if percentage < 40:

        grade = "FF"
        grade_point = 0
        result_status = "FAIL"

    else:

        component_failed = False

        # Theory subjects
        if subject.subject_type in [
            "THEORY",
            "THEORY_PRACTICAL",
        ]:

            if theory_internal < subject.theory_internal_min:
                component_failed = True

            if (
                (entry.theory_external_marks or 0)
                < subject.theory_external_min
            ):
                component_failed = True

        # Practical subjects
        if subject.subject_type in [
            "PRACTICAL",
            "THEORY_PRACTICAL",
        ]:

            if (
                (entry.practical_internal_marks or 0)
                < subject.practical_internal_min
            ):
                component_failed = True

            if (
                (entry.practical_external_marks or 0)
                < subject.practical_external_min
            ):
                component_failed = True

        if component_failed:

            grade = "FF"
            grade_point = 0
            result_status = "FAIL"

        else:

            if percentage >= 85:
                grade = "A+"
                grade_point = 10

            elif percentage >= 75:
                grade = "A"
                grade_point = 9

            elif percentage >= 65:
                grade = "B+"
                grade_point = 8

            elif percentage >= 55:
                grade = "B"
                grade_point = 7

            elif percentage >= 45:
                grade = "C"
                grade_point = 6

            else:
                grade = "D"
                grade_point = 5

            result_status = "PASS"

    entry.total_marks = total_marks
    entry.percentage = percentage
    entry.grade = grade
    entry.grade_point = grade_point
    entry.result_status = result_status

    entry.save(
        update_fields=[
            "total_marks",
            "percentage",
            "grade",
            "grade_point",
            "result_status",
            "updated_on",
        ]
    )

    return entry

def get_effective_results(
    student,
    semester=None,
):
    """
    Return the latest attempt for each subject for a student.

    All historical and live attempts remain stored in the database.
    Only the highest attempt_number for each subject is returned
    as the effective result.
    """

    queryset = StudentAcademicResult.objects.filter(
        student=student,
    ).select_related(
        "subject",
        "examination",
    )

    if semester is not None:

        queryset = queryset.filter(
            subject__semester=semester,
        )

    effective_results = {}

    for result in queryset.order_by(
        "subject_id",
        "-attempt_number",
    ):

        if result.subject_id not in effective_results:

            effective_results[result.subject_id] = result

    return list(
        effective_results.values()
    )
