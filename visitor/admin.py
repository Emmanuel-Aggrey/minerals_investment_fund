from django.contrib import admin
from .models import Staff, Visitor
from core.admin import ModelAdmin


@admin.register(Staff)
class StaffAdmin(ModelAdmin):
    list_display = ('staff_id', 'name', 'department', 'user', 'location')
    list_filter = ('department',)
    search_fields = (
        'staff_id',
        'first_name',
        'last_name',
        'user__first_name',
        'user__last_name',
        'user__email',
    )


@admin.register(Visitor)
class VisitorAdmin(ModelAdmin):
    list_display = (
        'reference_number',
        'full_name',
        'person_visited_name',
        'staff_to_visit',
        'department',
        'purpose',
        'entry_time',
        'exit_time',
        'registered_by',
    )
    list_filter = ('purpose', 'department', 'consent_given', 'visit_date')
    search_fields = (
        'reference_number',
        'full_name',
        'phone',
        'person_to_visit',
        'staff_to_visit__first_name',
        'staff_to_visit__last_name',
        'staff_to_visit__user__first_name',
        'staff_to_visit__user__last_name',
        'staff_to_visit__user__email',
    )
    readonly_fields = ('reference_number', 'visit_date',
                       'purge_date', 'created_at')
