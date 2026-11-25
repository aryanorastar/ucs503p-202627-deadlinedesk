from datetime import timedelta
from decimal import Decimal
import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import Assignment, AuditLog, ChecklistItem, Company, Grade, PlacementRound, ReminderLog, Submission, User


@pytest.fixture
def users(db):
    student = User.objects.create_user(username="student_test", password="SafePass123!", role=User.Role.STUDENT)
    ta = User.objects.create_user(username="ta_test", password="SafePass123!", role=User.Role.TA)
    admin = User.objects.create_user(username="admin_test", password="SafePass123!", role=User.Role.PLACEMENT_ADMIN)
    return student, ta, admin


@pytest.mark.django_db
def test_student_cannot_open_placement_admin_create_page(users):
    student, _, _ = users
    client = Client()
    client.force_login(student)
    response = client.get(reverse("company_create"))
    assert response.status_code == 403


@pytest.mark.django_db
def test_publishing_round_creates_t_minus_24_hour_reminder(users):
    _, _, admin = users
    company = Company.objects.create(name="Vector Labs", created_by=admin)
    placement_round = PlacementRound.objects.create(
        company=company,
        title="Application",
        opens_at=timezone.now(),
        closes_at=timezone.now() + timedelta(days=3),
        created_by=admin,
    )
    ChecklistItem.objects.create(placement_round=placement_round, title="Resume", required=True)
    client = Client()
    client.force_login(admin)
    response = client.post(reverse("round_publish", args=[placement_round.pk]))
    assert response.status_code == 302
    placement_round.refresh_from_db()
    assert placement_round.status == PlacementRound.Status.PUBLISHED
    reminder = ReminderLog.objects.get(placement_round=placement_round)
    assert reminder.scheduled_for == placement_round.closes_at - timedelta(hours=24)


@pytest.mark.django_db
def test_student_checklist_completion_is_idempotent_toggle(users):
    student, _, admin = users
    company = Company.objects.create(name="Orbit Works", created_by=admin)
    placement_round = PlacementRound.objects.create(
        company=company,
        title="Technical Round",
        opens_at=timezone.now() - timedelta(hours=1),
        closes_at=timezone.now() + timedelta(hours=3),
        status=PlacementRound.Status.PUBLISHED,
        created_by=admin,
    )
    item = ChecklistItem.objects.create(placement_round=placement_round, title="Transcript")
    client = Client()
    client.force_login(student)
    client.post(reverse("checklist_toggle", args=[item.pk]))
    assert item.completions.filter(student=student).exists()
    client.post(reverse("checklist_toggle", args=[item.pk]))
    assert not item.completions.filter(student=student).exists()


@pytest.mark.django_db
def test_late_penalty_submission_and_ta_grade_complete_academic_path(users):
    student, ta, _ = users
    assignment = Assignment.objects.create(
        title="Design Review",
        description="Submit the design review.",
        due_at=timezone.now() - timedelta(minutes=10),
        late_policy=Assignment.LatePolicy.PENALTY,
        penalty_percent=20,
        created_by=ta,
    )
    client = Client()
    client.force_login(student)
    upload = SimpleUploadedFile("review.txt", b"requirements traceability acceptance test", content_type="text/plain")
    with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
        response = client.post(reverse("assignment_submit", args=[assignment.pk]), {"file": upload, "note": "Week 7"})
        assert response.status_code == 302
        submission = Submission.objects.get(assignment=assignment, student=student)
        assert submission.late_status == Submission.LateStatus.PENALTY
        assert submission.penalty_percent == 20

        client.force_login(ta)
        response = client.post(
            reverse("submission_grade", args=[submission.pk]),
            {"score": "82", "max_score": "100", "feedback": "Clear traceability."},
        )
        assert response.status_code == 302
        submission.refresh_from_db()
        assert submission.status == Submission.Status.GRADED
        grade = Grade.objects.get(submission=submission)
        assert grade.score == Decimal("82")


@pytest.mark.django_db
def test_reject_policy_does_not_create_late_submission(users):
    student, ta, _ = users
    assignment = Assignment.objects.create(
        title="Closed Dropbox",
        description="No late work.",
        due_at=timezone.now() - timedelta(seconds=1),
        late_policy=Assignment.LatePolicy.REJECT,
        created_by=ta,
    )
    client = Client()
    client.force_login(student)
    upload = SimpleUploadedFile("late.txt", b"late", content_type="text/plain")
    response = client.post(reverse("assignment_submit", args=[assignment.pk]), {"file": upload})
    assert response.status_code == 302
    assert not Submission.objects.filter(assignment=assignment, student=student).exists()


@pytest.mark.django_db
def test_student_cannot_download_another_students_submission(users):
    student, ta, _ = users
    other_student = User.objects.create_user(username="other_student", password="SafePass123!", role=User.Role.STUDENT)
    assignment = Assignment.objects.create(
        title="Private Upload",
        description="Student files are private.",
        due_at=timezone.now() + timedelta(hours=1),
        late_policy=Assignment.LatePolicy.REJECT,
        created_by=ta,
    )
    with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
        submission = Submission.objects.create(
            assignment=assignment,
            student=other_student,
            file=SimpleUploadedFile("private.txt", b"private content"),
            late_status=Submission.LateStatus.ON_TIME,
        )
        client = Client()
        client.force_login(student)
        response = client.get(reverse("submission_download", args=[submission.pk]))
        assert response.status_code == 403


@pytest.mark.django_db
@pytest.mark.parametrize("role", [User.Role.TA, User.Role.PLACEMENT_ADMIN, User.Role.STUDENT])
@pytest.mark.parametrize("route", ["submission_detail", "submission_download", "submission_review", "submission_grade"])
def test_submission_access_rejects_unrelated_users(users, role, route):
    student, owner, _ = users
    outsider = User.objects.create_user(username="outsider", role=role)
    assignment = Assignment.objects.create(title="Private", description="Private", due_at=timezone.now(), late_policy="reject", created_by=owner)
    with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
        submission = Submission.objects.create(assignment=assignment, student=student, file=SimpleUploadedFile("work.txt", b"private"), late_status="on_time")
        client = Client()
        client.force_login(outsider)
        response = client.post(reverse(route, args=[submission.pk]), {"score": "80", "max_score": "100"}) if route == "submission_review" else client.get(reverse(route, args=[submission.pk]))
        assert response.status_code == 403
        assert not Grade.objects.filter(submission=submission).exists()


@pytest.mark.django_db
@pytest.mark.parametrize("status,offset", [("draft", 1), ("archived", 1), ("published", -1), ("published", 2)])
def test_checklist_changes_require_open_round(users, status, offset):
    student, _, admin = users
    company = Company.objects.create(name="Guarded", created_by=admin)
    now = timezone.now()
    round_ = PlacementRound.objects.create(company=company, title="Restricted", opens_at=now + timedelta(hours=offset) if offset == 2 else now - timedelta(days=2), closes_at=now + timedelta(days=offset), status=status, created_by=admin)
    item = ChecklistItem.objects.create(placement_round=round_, title="Resume")
    client = Client()
    client.force_login(student)
    assert client.post(reverse("checklist_toggle", args=[item.pk])).status_code == 403
    assert not item.completions.exists()


@pytest.mark.django_db
def test_dashboard_does_not_expose_other_users_activity(users):
    student, ta, _ = users
    AuditLog.objects.create(actor=ta, action="private.feedback", entity_type="Grade", entity_id=1, detail={"feedback": "Private"})
    client = Client()
    client.force_login(student)
    response = client.get(reverse("dashboard"))
    assert response.status_code == 200
    assert not list(response.context["recent_activity"])


@pytest.mark.django_db
def test_ta_cannot_view_other_assignment_roster(users):
    _, owner, _ = users
    outsider = User.objects.create_user(username="other_ta", role=User.Role.TA)
    assignment = Assignment.objects.create(title="Owner only", description="Private roster", due_at=timezone.now(), late_policy="reject", created_by=owner)
    client = Client()
    client.force_login(outsider)
    assert client.get(reverse("assignment_detail", args=[assignment.pk])).status_code == 403
    assert not list(client.get(reverse("assignment_list")).context["assignments"])


@pytest.mark.django_db
@pytest.mark.parametrize("filename,content", [("blocked.exe", b"bad"), ("large.txt", b"a" * (5 * 1024 * 1024 + 1))], ids=["blocked-extension", "oversized-file"])
def test_invalid_upload_creates_no_submission(users, filename, content):
    student, ta, _ = users
    assignment = Assignment.objects.create(title="Upload validation", description="File validation", due_at=timezone.now() + timedelta(days=1), late_policy="reject", created_by=ta)
    client = Client()
    client.force_login(student)
    response = client.post(reverse("assignment_submit", args=[assignment.pk]), {"file": SimpleUploadedFile(filename, content)})
    assert response.status_code == 200
    assert response.context["form"].errors.get("file")
    assert not assignment.submissions.exists()


@pytest.mark.django_db
def test_login_logout_and_csrf_boundary(users):
    client = Client(enforce_csrf_checks=True)
    assert client.get(reverse("dashboard")).status_code == 302
    assert client.post(reverse("login"), {"username": "student_test", "password": "SafePass123!"}).status_code == 403
    client.get(reverse("login"))
    token = client.cookies["csrftoken"].value
    assert client.post(reverse("login"), {"username": "student_test", "password": "wrong", "csrfmiddlewaretoken": token}).status_code == 200
    assert client.post(reverse("login"), {"username": "student_test", "password": "SafePass123!", "csrfmiddlewaretoken": token}).status_code == 302
    assert client.get(reverse("dashboard")).status_code == 200
    assert client.post(reverse("logout"), {"csrfmiddlewaretoken": client.cookies["csrftoken"].value}).status_code == 302
    assert client.get(reverse("dashboard")).status_code == 302


@pytest.mark.django_db
def test_publish_without_required_item_fails_and_repeat_is_deduplicated(users):
    _, _, admin = users
    company = Company.objects.create(name="Publication checks", created_by=admin)
    round_ = PlacementRound.objects.create(company=company, title="Draft", opens_at=timezone.now(), closes_at=timezone.now() + timedelta(days=2), created_by=admin)
    client = Client()
    client.force_login(admin)
    client.post(reverse("round_publish", args=[round_.pk]))
    round_.refresh_from_db()
    assert round_.status == "draft"
    assert not round_.reminders.exists()
    ChecklistItem.objects.create(placement_round=round_, title="Resume")
    client.post(reverse("round_publish", args=[round_.pk]))
    client.post(reverse("round_publish", args=[round_.pk]))
    assert round_.reminders.count() == 1


@pytest.mark.django_db
def test_duplicate_upload_and_invalid_grade_preserve_existing_data(users):
    student, ta, _ = users
    assignment = Assignment.objects.create(title="State preservation", description="Validation", due_at=timezone.now() + timedelta(days=1), late_policy="reject", created_by=ta)
    client = Client()
    client.force_login(student)
    with tempfile.TemporaryDirectory() as media_root, override_settings(MEDIA_ROOT=media_root):
        client.post(reverse("assignment_submit", args=[assignment.pk]), {"file": SimpleUploadedFile("first.txt", b"original submission")})
        client.post(reverse("assignment_submit", args=[assignment.pk]), {"file": SimpleUploadedFile("second.txt", b"replacement")})
        assert assignment.submissions.count() == 1
        submission = assignment.submissions.get()
        client.force_login(ta)
        response = client.post(reverse("submission_grade", args=[submission.pk]), {"score": "101", "max_score": "100"})
        assert response.context["form"].errors.get("score")
        assert not Grade.objects.filter(submission=submission).exists()
        client.post(reverse("submission_review", args=[submission.pk]))
        client.post(reverse("submission_grade", args=[submission.pk]), {"score": "92", "max_score": "100", "feedback": "Verified"})
        client.post(reverse("submission_review", args=[submission.pk]))
        submission.refresh_from_db()
        assert submission.status == "graded"
        client.force_login(student)
        assert b"Verified" in client.get(reverse("submission_detail", args=[submission.pk])).content
        response = client.get(reverse("submission_download", args=[submission.pk]))
        assert b"".join(response.streaming_content) == b"original submission"


@pytest.mark.django_db
def test_demo_seed_refreshes_without_duplicating_schedule():
    call_command("seed_demo")
    first_schedule = ReminderLog.objects.get().pk
    call_command("seed_demo")
    assert User.objects.count() == 3
    assert Company.objects.count() == 1
    assert PlacementRound.objects.count() == 1
    assert ChecklistItem.objects.count() == 3
    assert Assignment.objects.count() == 1
    assert ReminderLog.objects.count() == 1
    reminder = ReminderLog.objects.get()
    assert reminder.pk == first_schedule
    assert reminder.scheduled_for == reminder.placement_round.closes_at - timedelta(hours=24)
