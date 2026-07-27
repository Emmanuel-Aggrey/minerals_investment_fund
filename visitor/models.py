import re

from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from accounts.models import Department, User


class Staff(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, null=True, blank=True)
    staff_id = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)

    @property
    def name(self):

        if self.user:
            return self.user.full_name or self.user.email
        return f"{self.first_name} {self.last_name}".strip() or self.staff_id

    def __str__(self):
        return f"{self.name} - Staff"


class Visitor(models.Model):
    PURPOSE_CHOICES = [
        ('Meeting', 'Meeting'),
        ('Official Business', 'Official Business'),
        ('Delivery', 'Delivery'),
        ('Interview', 'Interview'),
        ('Contractor Work', 'Contractor Work'),
        ('Enquiry', 'Enquiry'),
        ('Other', 'Other'),
    ]

    DURATION_CHOICES = [
        ('Under 30 min', 'Under 30 min'),
        ('30–60 min', '30–60 min'),
        ('1–2 hours', '1–2 hours'),
        ('Half day', 'Half day'),
        ('Full day', 'Full day'),
    ]

    DEPARTMENT_CHOICES = [
        ('Executive Office', 'Executive Office'),
        ('Finance & Accounts', 'Finance & Accounts'),
        ('Legal & Compliance', 'Legal & Compliance'),
        ('Investment & Portfolio', 'Investment & Portfolio'),
        ('Operations', 'Operations'),
        ('Human Resources', 'Human Resources'),
        ('IT & Technology', 'IT & Technology'),
        ('Communications & PR', 'Communications & PR'),
        ('Internal Audit', 'Internal Audit'),
        ('Procurement', 'Procurement'),
        ('Other', 'Other'),
    ]

    reference_number = models.CharField(
        max_length=30, unique=True, null=True, blank=True
    )
    registered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='registered_visitors',
    )
    full_name = models.CharField(max_length=120)
    phone = models.CharField(max_length=25)
    email = models.EmailField(blank=True, null=True)
    person_to_visit = models.CharField(max_length=120, blank=True)
    staff_to_visit = models.ForeignKey(
        Staff,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    purpose = models.CharField(max_length=60, choices=PURPOSE_CHOICES)
    expected_duration = models.CharField(
        max_length=30, choices=DURATION_CHOICES, blank=True
    )
    notes = models.TextField(blank=True, max_length=255)
    consent_given = models.BooleanField(default=False)
    entry_time = models.DateTimeField(default=timezone.now)
    exit_time = models.DateTimeField(null=True, blank=True)
    visit_date = models.DateField()
    purge_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        super().clean()
        has_staff = bool(self.staff_to_visit_id)
        has_manual_person = bool((self.person_to_visit or '').strip())
        if has_staff and has_manual_person:
            raise ValidationError(
                'Choose a staff member or enter a person to visit, not both.'
            )
        if not has_staff and not has_manual_person:
            raise ValidationError(
                'Choose a staff member or enter a person to visit.'
            )

    def save(self, *args, **kwargs):
        if self.staff_to_visit and self.staff_to_visit.department_id:
            self.department = self.staff_to_visit.department

        if not self.visit_date:
            self.visit_date = (
                self.entry_time.date()
                if self.entry_time
                else timezone.now().date()
            )

        if not self.purge_date:
            from datetime import timedelta
            self.purge_date = self.visit_date + timedelta(days=30)

        if not self.reference_number:
            visit_stamp = self.visit_date.strftime('%Y%m%d')
            prefix = f'MIIF-{visit_stamp}-'
            last_reference = Visitor.objects.filter(
                reference_number__startswith=prefix
            ).order_by('-reference_number').values_list(
                'reference_number', flat=True
            ).first()
            last_number = 0
            if last_reference:
                match = re.search(r'-(\d+)$', last_reference)
                if match:
                    last_number = int(match.group(1))

            while True:
                last_number += 1
                candidate = f'{prefix}{last_number:04d}'
                if not Visitor.objects.filter(reference_number=candidate).exists():
                    self.reference_number = candidate
                    break

        super().save(*args, **kwargs)

    @property
    def duration(self):
        if self.exit_time and self.entry_time:
            delta = self.exit_time - self.entry_time
            total = int(delta.total_seconds())
            h, m = divmod(total // 60, 60)
            return f"{h}h {m}m" if h else f"{m}m"
        return None

    @property
    def person_visited_name(self):
        return self.staff_to_visit.name if self.staff_to_visit else self.person_to_visit

    @property
    def department_name(self):
        return self.department.name if self.department else 'N/A'

    class Meta:
        ordering = ['-entry_time']

    def __str__(self):
        return f"{self.reference_number} — {self.full_name}"
