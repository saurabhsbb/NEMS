from django.conf import settings
from django.db import models

from examinations.models import Examination
from academics.models import Subject


class ExaminationSubjectSchedule(models.Model):

    examination = models.ForeignKey(
        Examination,
        on_delete=models.PROTECT,
        related_name="subject_schedules",
    )

    subject = models.ForeignKey(
        Subject,
        on_delete=models.PROTECT,
        related_name="examination_schedules",
    )

    exam_date = models.DateField()

    start_time = models.TimeField()

    end_time = models.TimeField()

    class Meta:

        ordering = [
            "examination",
            "exam_date",
            "start_time",
            "subject__display_order",
        ]

        constraints = [
            models.UniqueConstraint(
                fields=[
                    "examination",
                    "subject",
                ],
                name="unique_examination_subject_schedule",
            ),
        ]

    def __str__(self):

        return (
            f"{self.examination.examination_code} - "
            f"{self.subject.subject_code}"
        )


class HallTicketPublication(models.Model):

    examination = models.OneToOneField(
        Examination,
        on_delete=models.PROTECT,
        related_name="hall_ticket_publication",
    )

    is_published = models.BooleanField(
        default=False,
    )

    published_on = models.DateTimeField(
        null=True,
        blank=True,
    )

    published_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="published_hall_tickets",
    )

    def __str__(self):

        return (
            f"{self.examination.examination_code} - "
            f"{'Published' if self.is_published else 'Not Published'}"
        )
