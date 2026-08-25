from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.db.models import Count, Q
from django.http import FileResponse, HttpResponseNotAllowed
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .decorators import role_required
from .forms import AssignmentForm, ChecklistItemForm, CompanyForm, GradeForm, PlacementRoundForm, SubmissionForm
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
from .services import evaluate_lateness, similarity_stub


def _audit(actor, action, instance, detail=None):
    AuditLog.objects.create(
        actor=actor,
        action=action,
        entity_type=instance.__class__.__name__,
        entity_id=instance.pk,
        detail=detail or {},
    )


def home(request):
    return redirect("dashboard" if request.user.is_authenticated else "login")


@login_required
def dashboard(request):
    now = timezone.now()
    local_hour = timezone.localtime(now).hour
    greeting = "morning" if local_hour < 12 else "afternoon" if local_hour < 17 else "evening"
    context = {"now": now, "greeting": greeting}
    if request.user.role == User.Role.STUDENT:
        rounds = PlacementRound.objects.exclude(status__in=[PlacementRound.Status.DRAFT, PlacementRound.Status.ARCHIVED])
        context.update(
            open_rounds=[item for item in rounds.select_related("company") if item.effective_status == PlacementRound.Status.OPEN][:4],
            assignments=Assignment.objects.filter(due_at__gte=now).order_by("due_at")[:4],
            recent_submissions=Submission.objects.filter(student=request.user).select_related("assignment")[:4],
        )
    elif request.user.role == User.Role.TA:
        context.update(
            assignments=Assignment.objects.filter(created_by=request.user).annotate(submission_count=Count("submissions"))[:5],
            pending_submissions=Submission.objects.exclude(status=Submission.Status.GRADED).select_related("assignment", "student")[:6],
        )
    else:
        context.update(
            rounds=PlacementRound.objects.select_related("company")[:6],
            scheduled_reminders=ReminderLog.objects.filter(status=ReminderLog.Status.SCHEDULED).select_related("placement_round__company")[:5],
        )
    context["recent_activity"] = AuditLog.objects.select_related("actor")[:6]
    return render(request, "core/dashboard.html", context)


@login_required
def placement_list(request):
    rounds = PlacementRound.objects.select_related("company")
    if request.user.role == User.Role.STUDENT:
        rounds = rounds.exclude(status__in=[PlacementRound.Status.DRAFT, PlacementRound.Status.ARCHIVED])
    return render(request, "core/placement_list.html", {"rounds": rounds, "companies": Company.objects.all()})


@role_required(User.Role.PLACEMENT_ADMIN)
def company_create(request):
    form = CompanyForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        company = form.save(commit=False)
        company.created_by = request.user
        company.save()
        _audit(request.user, "company.created", company)
        messages.success(request, "Company created.")
        return redirect("placement_list")
    return render(request, "core/form.html", {"form": form, "title": "Add company", "submit_label": "Create company"})


@role_required(User.Role.PLACEMENT_ADMIN)
def round_create(request):
    form = PlacementRoundForm(request.POST or None, initial={"company": request.GET.get("company")})
    if request.method == "POST" and form.is_valid():
        placement_round = form.save(commit=False)
        placement_round.created_by = request.user
        placement_round.save()
        _audit(request.user, "round.created", placement_round)
        messages.success(request, "Placement round saved as draft.")
        return redirect("round_detail", pk=placement_round.pk)
    return render(request, "core/form.html", {"form": form, "title": "Create placement round", "submit_label": "Save draft"})


@login_required
def round_detail(request, pk):
    placement_round = get_object_or_404(PlacementRound.objects.select_related("company"), pk=pk)
    if request.user.role == User.Role.STUDENT and placement_round.status in {PlacementRound.Status.DRAFT, PlacementRound.Status.ARCHIVED}:
        raise PermissionDenied

    items = list(placement_round.checklist_items.all())
    completed_ids = set()
    if request.user.role == User.Role.STUDENT:
        completed_ids = set(
            ChecklistCompletion.objects.filter(student=request.user, item__placement_round=placement_round).values_list("item_id", flat=True)
        )
    checklist = [{"item": item, "completed": item.id in completed_ids} for item in items]
    required = [entry for entry in checklist if entry["item"].required]
    ready = bool(required) and all(entry["completed"] for entry in required)
    return render(
        request,
        "core/round_detail.html",
        {"round": placement_round, "checklist": checklist, "ready": ready, "reminders": placement_round.reminders.all()},
    )


@role_required(User.Role.PLACEMENT_ADMIN)
def checklist_create(request, pk):
    placement_round = get_object_or_404(PlacementRound, pk=pk)
    form = ChecklistItemForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        item = form.save(commit=False)
        item.placement_round = placement_round
        item.save()
        _audit(request.user, "checklist.created", item, {"round_id": placement_round.pk})
        messages.success(request, "Checklist item added.")
        return redirect("round_detail", pk=pk)
    return render(request, "core/form.html", {"form": form, "title": "Add checklist item", "submit_label": "Add item"})


@role_required(User.Role.PLACEMENT_ADMIN)
@transaction.atomic
def round_publish(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    placement_round = get_object_or_404(PlacementRound, pk=pk)
    if not placement_round.checklist_items.filter(required=True).exists():
        messages.error(request, "Add at least one required checklist item before publishing.")
        return redirect("round_detail", pk=pk)
    placement_round.status = PlacementRound.Status.PUBLISHED
    placement_round.save(update_fields=["status"])
    reminder_time = placement_round.closes_at - timedelta(hours=24)
    ReminderLog.objects.get_or_create(
        placement_round=placement_round,
        scheduled_for=reminder_time,
        defaults={"created_by": request.user},
    )
    _audit(request.user, "round.published", placement_round, {"reminder_at": reminder_time.isoformat()})
    messages.success(request, "Round published and T-24h reminder logged.")
    return redirect("round_detail", pk=pk)


@role_required(User.Role.STUDENT)
def checklist_toggle(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    item = get_object_or_404(ChecklistItem.objects.select_related("placement_round"), pk=pk)
    completion, created = ChecklistCompletion.objects.get_or_create(item=item, student=request.user)
    if not created:
        completion.delete()
    _audit(request.user, "checklist.completed" if created else "checklist.reopened", item)
    return redirect("round_detail", pk=item.placement_round_id)


@login_required
def assignment_list(request):
    assignments = Assignment.objects.select_related("created_by").annotate(submission_count=Count("submissions"))
    return render(request, "core/assignment_list.html", {"assignments": assignments})


@role_required(User.Role.TA)
def assignment_create(request):
    form = AssignmentForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        assignment = form.save(commit=False)
        assignment.created_by = request.user
        assignment.save()
        _audit(request.user, "assignment.published", assignment)
        messages.success(request, "Assignment published.")
        return redirect("assignment_detail", pk=assignment.pk)
    return render(request, "core/form.html", {"form": form, "title": "Publish assignment", "submit_label": "Publish assignment"})


@login_required
def assignment_detail(request, pk):
    assignment = get_object_or_404(Assignment.objects.select_related("created_by"), pk=pk)
    submission = None
    submissions = None
    decision = None
    if request.user.role == User.Role.STUDENT:
        submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
        decision = evaluate_lateness(
            due_at=assignment.due_at,
            submitted_at=timezone.now(),
            policy=assignment.late_policy,
            grace_minutes=assignment.grace_minutes,
            penalty_percent=assignment.penalty_percent,
        )
    elif request.user.role == User.Role.TA:
        submissions = assignment.submissions.select_related("student").all()
    return render(
        request,
        "core/assignment_detail.html",
        {"assignment": assignment, "submission": submission, "submissions": submissions, "decision": decision},
    )


@role_required(User.Role.STUDENT)
@transaction.atomic
def assignment_submit(request, pk):
    assignment = get_object_or_404(Assignment, pk=pk)
    if Submission.objects.filter(assignment=assignment, student=request.user).exists():
        messages.error(request, "You have already submitted this assignment.")
        return redirect("assignment_detail", pk=pk)
    submitted_at = timezone.now()
    decision = evaluate_lateness(
        due_at=assignment.due_at,
        submitted_at=submitted_at,
        policy=assignment.late_policy,
        grace_minutes=assignment.grace_minutes,
        penalty_percent=assignment.penalty_percent,
    )
    if not decision.accepted:
        messages.error(request, decision.reason)
        return redirect("assignment_detail", pk=pk)

    form = SubmissionForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        uploaded_file = form.cleaned_data["file"]
        comparison = Submission.objects.filter(assignment=assignment)
        score = similarity_stub(uploaded_file, comparison)
        submission = form.save(commit=False)
        submission.assignment = assignment
        submission.student = request.user
        submission.submitted_at = submitted_at
        submission.late_status = decision.status
        submission.penalty_percent = decision.penalty_percent
        submission.similarity_score = score
        submission.save()
        _audit(request.user, "submission.created", submission, {"late_status": decision.status, "similarity_stub": str(score)})
        messages.success(request, f"Submission received. {decision.reason}.")
        return redirect("submission_detail", pk=submission.pk)
    return render(request, "core/form.html", {"form": form, "title": f"Submit: {assignment.title}", "submit_label": "Submit assignment", "notice": decision.reason})


@login_required
def submission_detail(request, pk):
    submission = get_object_or_404(Submission.objects.select_related("assignment", "student"), pk=pk)
    if request.user.role == User.Role.STUDENT and submission.student_id != request.user.id:
        raise PermissionDenied
    grade = Grade.objects.filter(submission=submission).select_related("graded_by").first()
    return render(request, "core/submission_detail.html", {"submission": submission, "grade": grade})


@login_required
def submission_download(request, pk):
    submission = get_object_or_404(Submission.objects.select_related("student"), pk=pk)
    if request.user.role == User.Role.STUDENT and submission.student_id != request.user.id:
        raise PermissionDenied
    return FileResponse(
        submission.file.open("rb"),
        as_attachment=True,
        filename=submission.file.name.rsplit("/", 1)[-1],
    )


@role_required(User.Role.TA)
def submission_review(request, pk):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])
    submission = get_object_or_404(Submission, pk=pk)
    if submission.status != Submission.Status.GRADED:
        submission.status = Submission.Status.UNDER_REVIEW
        submission.save(update_fields=["status"])
        _audit(request.user, "submission.review_started", submission)
    return redirect("submission_detail", pk=pk)


@role_required(User.Role.TA)
@transaction.atomic
def submission_grade(request, pk):
    submission = get_object_or_404(Submission.objects.select_related("assignment", "student"), pk=pk)
    grade = Grade.objects.filter(submission=submission).first()
    form = GradeForm(request.POST or None, instance=grade)
    if request.method == "POST" and form.is_valid():
        grade = form.save(commit=False)
        grade.submission = submission
        grade.graded_by = request.user
        grade.save()
        submission.status = Submission.Status.GRADED
        submission.save(update_fields=["status"])
        _audit(request.user, "submission.graded", submission, {"score": str(grade.score), "max_score": str(grade.max_score)})
        messages.success(request, "Grade published to the student.")
        return redirect("submission_detail", pk=pk)
    return render(request, "core/form.html", {"form": form, "title": f"Grade {submission.student}", "submit_label": "Publish grade"})
