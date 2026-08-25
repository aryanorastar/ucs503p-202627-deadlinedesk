from datetime import timedelta
from decimal import Decimal
import tempfile

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, override_settings
from django.urls import reverse
from django.utils import timezone

from core.models import Assignment, ChecklistItem, Company, Grade, PlacementRound, ReminderLog, Submission, User


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
