from django.core.exceptions import ValidationError


def validate_pdf(file):

    if not file.name.lower().endswith(".pdf"):

        raise ValidationError(
            "Only PDF files are allowed."
        )
