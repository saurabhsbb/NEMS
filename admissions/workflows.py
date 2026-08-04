from accounts.models import User, Role
from admissions.models import Student


def confirm_admission(student):
    """
    Confirm Student Admission
    """

    if student.admission_status == "CONFIRMED":
        return

    year = student.admission_academic_year
    programme_code = student.programme.programme_code

    # Get confirmed students of the same programme and entry type
    confirmed_students = Student.objects.filter(
        admission_academic_year=year,
        programme=student.programme,
        programme_entry_type=student.programme_entry_type,
        admission_status="CONFIRMED",
    )

    # Extract existing roll number sequence
    numbers = []

    for s in confirmed_students:
        if s.roll_number:
            try:
                numbers.append(int(s.roll_number.split("/")[-1]))
            except (ValueError, IndexError):
                pass

    # Generate roll number only if it doesn't already exist
    if not student.roll_number:

        if student.programme_entry_type.entry_type_code == "LAT":
            next_number = max(numbers) + 1 if numbers else 72
        else:
            next_number = max(numbers) + 1 if numbers else 1

        student.roll_number = f"{year}/{programme_code}/{next_number:02d}"

    student.admission_status = "CONFIRMED"

    student_role = Role.objects.get(role_code="STUDENT")

    if student.user:
        # User already exists (Excel import)
        student.user.role = student_role
        student.user.save()
    else:
        # Manual admission
        user = User.objects.create_user(
            username=student.roll_number,
            password=student.date_of_birth.strftime("%d%m%Y"),
            first_name=student.student_name,
            role=student_role,
        )
        student.user = user

    student.save()
