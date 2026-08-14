from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.exceptions import ValidationError


class Role(models.Model):
    role_code = models.CharField(max_length=10, unique=True)
    role_name = models.CharField(max_length=100, unique=True)
    display_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["display_order"]

    def __str__(self):
        return self.role_name

    def delete(self, *args, **kwargs):
        if self.user_set.exists():
            raise ValidationError(
                "This role is assigned to one or more users and cannot be deleted."
            )

        super().delete(*args, **kwargs)

class User(AbstractUser):
    """
    Custom User Model
    """

    role = models.ForeignKey(
        Role,
        on_delete=models.PROTECT,
        null=True,
        blank=True
    )

    def __str__(self):
        return self.username

    
