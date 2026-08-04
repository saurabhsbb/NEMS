from django.db import models
from django.core.exceptions import ValidationError

from accounts.models import User
from academics.models import (
    Programme,
    ProgrammeEntryType,
    AdmissionCategory,
)

ADMISSION_STATUS = [
    ("PENDING", "Pending"),
    ("CONFIRMED", "Confirmed"),
]

class Student(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    roll_number = models.CharField(
        max_length=20,
        unique=True,
        blank=True,
        null=True
    )

    student_name = models.CharField(max_length=200)

    father_name = models.CharField(max_length=200)

    mother_name = models.CharField(max_length=200)

    aadhaar_number = models.CharField(
        max_length=12,
        unique=True
    )

    mobile_number = models.CharField(max_length=10)

    parent_mobile_number = models.CharField(max_length=10)

    email = models.EmailField(
        blank=True,
        null=True,
    )

    date_of_birth = models.DateField()
    
    GENDER_CHOICES = [
        ("MALE", "Male"),
        ("FEMALE", "Female"),
        ("OTHER", "Other"),
    ]

    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        blank=True,
        null=True,
    )

    blood_group = models.CharField(max_length=5)

    programme = models.ForeignKey(
        Programme,
        on_delete=models.PROTECT
    )

    programme_entry_type = models.ForeignKey(
        ProgrammeEntryType,
        on_delete=models.PROTECT
    )

    admission_category = models.ForeignKey(
        AdmissionCategory,
        on_delete=models.PROTECT
    )

    admission_academic_year = models.PositiveSmallIntegerField()

    remarks = models.TextField(
        blank=True
    )

    documents_verified = models.BooleanField(
        default=False
    )

    ADMISSION_STATUS = [
        ("PENDING", "Pending"),
        ("CONFIRMED", "Confirmed"),
    ]

    admission_status = models.CharField(
        max_length=20,
        choices=ADMISSION_STATUS,
        default="PENDING",
    )

    is_active = models.BooleanField(
        default=True
    )

    class Meta:
        ordering = ["roll_number"]

    def clean(self):
        super().clean()

        if self.admission_status == "CONFIRMED" and not self.documents_verified:
            raise ValidationError({
                "documents_verified": "Documents must be verified before admission can be confirmed."
            })

    def __str__(self):
        return self.student_name
