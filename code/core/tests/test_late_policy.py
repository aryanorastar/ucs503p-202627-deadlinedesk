from datetime import timedelta

import pytest
from django.utils import timezone

from core.models import Assignment, Submission
from core.services import evaluate_lateness


@pytest.fixture
def due_at():
    return timezone.now().replace(microsecond=0)


def test_submission_at_exact_deadline_is_on_time(due_at):
    decision = evaluate_lateness(due_at=due_at, submitted_at=due_at, policy=Assignment.LatePolicy.REJECT)
    assert decision.accepted is True
    assert decision.status == Submission.LateStatus.ON_TIME
    assert decision.penalty_percent == 0


def test_reject_policy_blocks_one_second_late(due_at):
    decision = evaluate_lateness(
        due_at=due_at,
        submitted_at=due_at + timedelta(seconds=1),
        policy=Assignment.LatePolicy.REJECT,
    )
    assert decision.accepted is False
    assert decision.status is None


def test_penalty_policy_accepts_and_applies_configured_percentage(due_at):
    decision = evaluate_lateness(
        due_at=due_at,
        submitted_at=due_at + timedelta(hours=3),
        policy=Assignment.LatePolicy.PENALTY,
        penalty_percent=15,
    )
    assert decision.accepted is True
    assert decision.status == Submission.LateStatus.PENALTY
    assert decision.penalty_percent == 15


def test_grace_policy_accepts_at_grace_boundary(due_at):
    decision = evaluate_lateness(
        due_at=due_at,
        submitted_at=due_at + timedelta(minutes=30),
        policy=Assignment.LatePolicy.GRACE,
        grace_minutes=30,
    )
    assert decision.accepted is True
    assert decision.status == Submission.LateStatus.GRACE


def test_grace_policy_rejects_after_grace_boundary(due_at):
    decision = evaluate_lateness(
        due_at=due_at,
        submitted_at=due_at + timedelta(minutes=30, seconds=1),
        policy=Assignment.LatePolicy.GRACE,
        grace_minutes=30,
    )
    assert decision.accepted is False


def test_unknown_policy_fails_closed(due_at):
    with pytest.raises(ValueError):
        evaluate_lateness(due_at=due_at, submitted_at=due_at + timedelta(seconds=1), policy="unknown")
