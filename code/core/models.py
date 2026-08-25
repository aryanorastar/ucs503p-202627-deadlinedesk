from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    class Role(models.TextChoices):
        STUDENT = "student", "Student"
        TA = "ta", "TA / Faculty"
        PLACEMENT_ADMIN = "placement_admin", "Placement Admin"

    role = models.CharField(max_length=24, choices=Role.choices, default=Role.STUDENT)
    roll_number = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username


class Company(models.Model):
    name = models.CharField(max_length=120, unique=True)
    description = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="companies_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "companies"

    def __str__(self):
        return self.name


class PlacementRound(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        OPEN = "open", "Open"
        CLOSED = "closed", "Closed"
        ARCHIVED = "archived", "Archived"

    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name="rounds")
    title = models.CharField(max_length=120)
    opens_at = models.DateTimeField()
    closes_at = models.DateTimeField()
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.DRAFT)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="rounds_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["closes_at"]

    def __str__(self):
        return f"{self.company.name}: {self.title}"

    @property
    def effective_status(self):
        if self.status in {self.Status.DRAFT, self.Status.ARCHIVED}:
            return self.status
        now = timezone.now()
        if now < self.opens_at:
            return self.Status.PUBLISHED
        if now <= self.closes_at:
            return self.Status.OPEN
        return self.Status.CLOSED

    @property
    def effective_status_label(self):
        return dict(self.Status.choices)[self.effective_status]


class ChecklistItem(models.Model):
    placement_round = models.ForeignKey(PlacementRound, on_delete=models.CASCADE, related_name="checklist_items")
    title = models.CharField(max_length=160)
    required = models.BooleanField(default=True)
    position = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["position", "id"]

    def __str__(self):
        return self.title


class ChecklistCompletion(models.Model):
    item = models.ForeignKey(ChecklistItem, on_delete=models.CASCADE, related_name="completions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="checklist_completions")
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["item", "student"], name="unique_student_checklist_completion")
        ]


class ReminderLog(models.Model):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        SENT = "sent", "Sent"

    placement_round = models.ForeignKey(PlacementRound, on_delete=models.CASCADE, related_name="reminders")
    scheduled_for = models.DateTimeField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.SCHEDULED)
    sent_at = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="reminders_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-scheduled_for"]


class Assignment(models.Model):
    class LatePolicy(models.TextChoices):
        REJECT = "reject", "Reject late submissions"
        PENALTY = "penalty", "Accept with penalty"
        GRACE = "grace", "Grace window"

    title = models.CharField(max_length=160)
    description = models.TextField()
    due_at = models.DateTimeField()
    late_policy = models.CharField(max_length=16, choices=LatePolicy.choices)
    grace_minutes = models.PositiveIntegerField(default=0)
    penalty_percent = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="assignments_created")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["due_at"]

    def __str__(self):
        return self.title


class Submission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = "submitted", "Submitted"
        UNDER_REVIEW = "under_review", "Under review"
        GRADED = "graded", "Graded"

    class LateStatus(models.TextChoices):
        ON_TIME = "on_time", "On time"
        GRACE = "grace", "Accepted in grace window"
        PENALTY = "penalty", "Late with penalty"

    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name="submissions")
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="submissions")
    file = models.FileField(upload_to="submissions/%Y/%m/")
    note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(default=timezone.now)
    late_status = models.CharField(max_length=16, choices=LateStatus.choices)
    penalty_percent = models.PositiveSmallIntegerField(default=0)
    similarity_score = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.SUBMITTED)

    class Meta:
        ordering = ["-submitted_at"]
        constraints = [
            models.UniqueConstraint(fields=["assignment", "student"], name="one_submission_per_student_assignment")
        ]

    def __str__(self):
        return f"{self.student} - {self.assignment}"


class Grade(models.Model):
    submission = models.OneToOneField(Submission, on_delete=models.CASCADE, related_name="grade")
    score = models.DecimalField(max_digits=6, decimal_places=2, validators=[MinValueValidator(0)])
    max_score = models.DecimalField(max_digits=6, decimal_places=2, default=100, validators=[MinValueValidator(1)])
    feedback = models.TextField(blank=True)
    graded_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="grades_given")
    graded_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.score}/{self.max_score}"


class AuditLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="audit_events")
    action = models.CharField(max_length=80)
    entity_type = models.CharField(max_length=80)
    entity_id = models.PositiveBigIntegerField()
    detail = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    @property
    def action_label(self):
        return self.action.replace(".", " ").replace("_", " ").title()
