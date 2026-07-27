import uuid
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError


class UserQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def inactive(self):
        return self.filter(is_active=False)

    def staff(self):
        return self.filter(is_staff=True)

    def superusers(self):
        return self.filter(is_superuser=True)

    def registration_completed(self):
        return self.filter(is_registration_completed=True)

    def registration_not_completed(self):
        return self.filter(is_registration_completed=False)

    def source(self, source):
        return self.filter(source=source)

    def filter_by_date(self, before=None, after=None):
        if before and after:
            return self.filter(date_joined__range=[after, before])

        if before:
            return self.filter(date_joined__lte=before)

        if after:
            return self.filter(date_joined__gte=after)

        return self


class Department(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Role(models.Model):
    VIEW_DASHBOARD = 'Can view Dashboard'
    REGISTER_VISIT = 'Register attendance/visit'
    VIEW_REPORTS = 'View Reports'
    ADMIN = 'Admin'

    ROLE_CHOICES = (
        (VIEW_DASHBOARD, VIEW_DASHBOARD),
        (REGISTER_VISIT, REGISTER_VISIT),
        (VIEW_REPORTS, VIEW_REPORTS),
        (ADMIN, ADMIN),
    )

    name = models.CharField(max_length=80, unique=True, choices=ROLE_CHOICES)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_("The Email must be set"))
        if not password:
            raise ValueError(_("The Password must be set"))
        extra_fields.setdefault("is_active", False)
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))
        if extra_fields.get("is_superuser") is not True:
            raise ValueError(_("Superuser must have is_superuser=True."))
        return self.create_user(email, password, **extra_fields)

    def get_or_create(self, defaults=None, **kwargs):
        if "email" in kwargs:
            email = kwargs.pop("email").lower()
            try:
                return self.get(email__iexact=email), False
            except self.model.DoesNotExist:
                kwargs["email"] = email
                if defaults:
                    kwargs.update(defaults)
                return self.create(**kwargs), True
            except self.model.MultipleObjectsReturned:
                return self.filter(email__iexact=email).first(), False
        return super().get_or_create(defaults=defaults, **kwargs)


class User(AbstractUser):

    objects: UserManager

    class Gender:
        MALE = "Male"
        FEMALE = "Female"
        OTHER = "Other"

        CHOICES = (
            (MALE, _("Male")),
            (FEMALE, _("Female")),
            (OTHER, _("Other")),
        )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = None
    email = models.EmailField(_("user email"), max_length=254, unique=True)
    mobile = models.CharField(_("mobile number"), max_length=20, blank=True)
    extension = models.CharField(
        max_length=5, null=True, blank=True, default=""
    )
    is_registration_completed = models.BooleanField(default=False)
    gender = models.CharField(
        max_length=10, choices=Gender.CHOICES, default=Gender.OTHER
    )

    profile_picture = models.ImageField(
        upload_to="profile_pictures", blank=True, null=True
    )
    deleted_at = models.DateTimeField(null=True, blank=True)

    last_active = models.DateTimeField(null=True, blank=True)

    department = models.ForeignKey(
        Department, on_delete=models.SET_NULL, null=True, blank=True)
    roles = models.ManyToManyField(Role, blank=True, related_name='users')

    objects = UserManager()
    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    def default_email(self):
        return f"{self.mobile}@default.com"

    def default_mobile(self):
        return ""

    def clean(self):
        if not self.email:
            raise ValidationError({"email": "Email is required"})

        return super().clean()

    def save(self, *args, **kwargs):
        self.clean()

        return super().save(*args, **kwargs)

    @property
    def full_name(self):
        return (
            f"{self.first_name} {self.last_name}"
            if self.first_name or self.last_name
            else self.email or self.username
        )

    def has_app_role(self, role_name):
        if self.is_superuser:
            return True
        if not hasattr(self, '_app_role_names'):
            self._app_role_names = set(
                self.roles.values_list('name', flat=True)
            )
        return role_name in self._app_role_names or Role.ADMIN in self._app_role_names

    @property
    def can_view_dashboard(self):
        return self.has_app_role(Role.VIEW_DASHBOARD)

    @property
    def can_register_visit(self):
        return self.has_app_role(Role.REGISTER_VISIT)

    @property
    def can_view_reports(self):
        return self.has_app_role(Role.VIEW_REPORTS)

    @property
    def can_access_admin(self):
        return self.is_superuser or self.roles.filter(name=Role.ADMIN).exists()
