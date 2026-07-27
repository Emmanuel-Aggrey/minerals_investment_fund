from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
# from import_export.admin import ExportActionMixin
# from import_export.admin import ImportExportModelAdmin
from core.admin import ModelAdmin
from . import models
from django.contrib import admin, messages
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html
from django.urls import reverse

from django.contrib.auth.forms import AdminPasswordChangeForm


class CustomAdminPasswordChangeForm(AdminPasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("usable_password", None)


class CustomUserAdmin(UserAdmin, ModelAdmin):

    def password_change_link(self, obj):
        url = reverse("admin:accounts_user_change_password", args=[obj.pk])
        return format_html('<a href="{}" style="color:#C9A84C;">Change password</a>', url)

    password_change_link.short_description = "Password"

    model = models.User
    actions = ["change_password_action"]
    exclude = ("groups", "user_permissions")
    list_display = (
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
        "last_login",
        "last_active",
        "password_change_link",
    )
    readonly_fields = ("last_login", "date_joined",
                       "last_active", "deleted_at", "password_change_link")

    search_fields = ("email", "first_name", "last_name")
    password_change_link.short_description = "Password"
    ordering = ("email",)
    filter_horizontal = ("roles",)
    list_filter = [
        "last_active",
        "last_login",
        "is_staff",
        "roles",
    ]
    fieldsets = (
        (None, {"fields": ("email", "password_change_link")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "roles",
                ),
            },
        ),
        (
            _("Important dates"),
            {"fields": ("last_login", "date_joined",
                        "last_active", "deleted_at")},
        ),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2"),
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        custom = [
            path(
                "<pk>/change-password/",
                self.admin_site.admin_view(self.change_password_view),
                name="accounts_user_change_password",
            ),
        ]
        return custom + urls

    def change_password_view(self, request, pk):
        from django.shortcuts import get_object_or_404
        user = get_object_or_404(models.User, pk=pk)
        if request.method == "POST":
            form = CustomAdminPasswordChangeForm(user, request.POST)
            if form.is_valid():
                form.save()
                self.message_user(
                    request, f"Password changed for {user.email}.", messages.SUCCESS)
                return redirect(reverse("admin:accounts_user_changelist"))
        else:
            form = CustomAdminPasswordChangeForm(user)
        return render(request, "admin/change_password_action.html", {
            "form": form,
            "user": user,
            "opts": self.model._meta,
            "title": f"Change password for {user.full_name}",
        })


admin.site.register(models.User, CustomUserAdmin)

admin.site.register(models.Department, ModelAdmin)


@admin.register(models.Role)
class RoleAdmin(ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False
