import random
from django.utils import timezone
from .models import QuestionPaper


def submit_question_papers(
    assignment,
    set1,
    set2,
    set3,
    minutes,
    declaration,
):
    """
    Submit all confidential question papers
    """

    if assignment.selected_question_paper_set:
        raise ValueError(
            "Question paper has already been selected by the COE. "
            "Further uploads or modifications are not allowed."
    )

    if not set1:
        raise ValueError(
            "Please upload Question Paper Set 1."
        )

    if not set2:
        raise ValueError(
            "Please upload Question Paper Set 2."
        )

    if not set3:
        raise ValueError(
            "Please upload Question Paper Set 3."
        )

    if not minutes:
        raise ValueError(
            "Please upload Question Paper Evaluation Committee Minutes."
        )

    if not declaration:
        raise ValueError(
            "Please accept the confidentiality declaration."
        )

    QuestionPaper.objects.update_or_create(
        faculty_subject_assignment=assignment,
        question_paper_set=1,
        defaults={
            "question_paper_file": set1,
        },
    )

    QuestionPaper.objects.update_or_create(
        faculty_subject_assignment=assignment,
        question_paper_set=2,
        defaults={
            "question_paper_file": set2,
        },
    )

    QuestionPaper.objects.update_or_create(
        faculty_subject_assignment=assignment,
        question_paper_set=3,
        defaults={
            "question_paper_file": set3,
        },
    )

    assignment.question_paper_evaluation_minutes = minutes
    assignment.question_paper_confidentiality_declaration = declaration
    assignment.submitted_on = timezone.now()

    assignment.save()

def generate_question_paper(
    assignment,
):
    """
    Randomly select one question paper.
    This operation can be performed only once.
    """

    if assignment.selected_question_paper_set:

        return assignment

    assignment.selected_question_paper_set = random.choice(
        [1, 2, 3]
    )

    assignment.save()

    return assignment
