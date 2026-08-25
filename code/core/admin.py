from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Assignment,
    AuditLog,
    ChecklistCompletion,
    ChecklistItem,
    Company,
    Grade,
    PlacementRound,
    ReminderLog,
    Submission,
    User,
)


@admin.register(User)
class DeadlineDeskUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (("DeadlineDesk", {"fields": ("role", "roll_number")}),)
    add_fieldsets = UserAdmin.add_fieldsets + (("DeadlineDesk", {"fields": ("role", "roll_number")}),)
    list_display = ("username", "email", "role", "roll_number", "is_staff")


admin.site.register(Company)
admin.site.register(PlacementRound)
admin.site.register(ChecklistItem)
admin.site.register(ChecklistCompletion)
admin.site.register(ReminderLog)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Grade)
admin.site.register(AuditLog)
