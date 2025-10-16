from django.db import models
from django.forms import ValidationError
from django.utils import timezone
from users.models import User

class BaseApplication(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    date_filed = models.DateTimeField(default=timezone.now)

    class Meta:
        abstract = True

class PeriodModel(models.Model):
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)

    class Meta:
        abstract = True
        ordering = ['-start_date']

class YesNoField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('max_length', 3)
        kwargs.setdefault('choices', [('Yes', 'Yes'), ('No', 'No')])
        kwargs.setdefault('default', 'No')
        kwargs.setdefault('blank', True)
        super().__init__(*args, **kwargs)

class DraftModel(models.Model):
    status = models.CharField(
        max_length=20,
        choices = [
            ("draft", "Draft"),
            ("submitted", "Submitted"),
            ("submitted_unpaid", "Submitted (Unpaid)"),
            ("submitted_paid", "Submitted (Paid)"),
            ("approved", "Approved"),
        ],
        default="draft"
    )

    class Meta:
        abstract = True

    @property
    def model_name(self):
        return self._meta.model_name

    @property
    def model_verbose_name(self):
        return self._meta.verbose_name

    def get_str_display(self, base_display: str) -> str:
        if self.status == "draft":
            return f"{base_display} (Draft)"
        return base_display

    def required_for_display(self):
        """
        Return a list of field names that must be filled for a meaningful draft,
        but only include fields that actually exist on this model.
        Override in child models if needed.
        """
        potential_fields = ["promo_title", "name", "name_of_business", "first_name", "last_name"]
        # Only keep fields that exist on this model
        model_fields = [f.name for f in self._meta.get_fields() if isinstance(f, models.Field)]
        return [f for f in potential_fields if f in model_fields]

    def clean(self):
        """Enforce required fields only if submitted."""
        super().clean()
        if self.status == "submitted":
            required_fields = [
                field.name
                for field in self._meta.get_fields()
                if isinstance(field, models.Field)
                and not field.blank
                and not field.null
                and field.name not in ("id", "status")
            ]

            errors = {}
            for field_name in required_fields:
                value = getattr(self, field_name, None)
                if value in (None, "", []):
                    errors[field_name] = "This field is required."
            if errors:
                raise ValidationError(errors)


    def prepare_for_draft(self):
        """Fill other required fields with placeholders to bypass NOT NULL."""
        for field in self._meta.get_fields():
            if (
                isinstance(field, models.Field)
                and not field.blank
                and not field.null
                and field.name not in ("id", "status")
            ):
                value = getattr(self, field.name)
                if value in (None, "", []) and field.name not in self.required_for_display():
                    if isinstance(field, models.CharField) or isinstance(field, models.TextField):
                        setattr(self, field.name, "")
                    elif isinstance(field, models.IntegerField):
                        setattr(self, field.name, 0)
                    elif isinstance(field, models.BooleanField):
                        setattr(self, field.name, False)
                    elif isinstance(field, models.DateField):
                        setattr(self, field.name, timezone.now().date())
                    elif isinstance(field, models.ForeignKey):
                        continue  # skip FK
                    else:
                        setattr(self, field.name, None)

    def save(self, *args, **kwargs):
        if self.status == "draft":
            self.clean()           # ensure display fields are filled
            self.prepare_for_draft()  # bypass other required fields
        elif self.status == "submitted":
            self.full_clean()  # normal validation

        super().save(*args, **kwargs)