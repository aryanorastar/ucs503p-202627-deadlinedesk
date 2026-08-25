from dataclasses import dataclass
from datetime import timedelta
from decimal import Decimal
import re

from .models import Assignment, Submission


@dataclass(frozen=True)
class LateDecision:
    accepted: bool
    status: str | None
    penalty_percent: int
    reason: str


def evaluate_lateness(*, due_at, submitted_at, policy, grace_minutes=0, penalty_percent=0):
    if submitted_at <= due_at:
        return LateDecision(True, Submission.LateStatus.ON_TIME, 0, "Submitted on time")

    if policy == Assignment.LatePolicy.REJECT:
        return LateDecision(False, None, 0, "The deadline has passed and late submissions are rejected")

    if policy == Assignment.LatePolicy.PENALTY:
        return LateDecision(
            True,
            Submission.LateStatus.PENALTY,
            penalty_percent,
            f"Accepted with a {penalty_percent}% late penalty",
        )

    if policy == Assignment.LatePolicy.GRACE:
        grace_ends_at = due_at + timedelta(minutes=grace_minutes)
        if submitted_at <= grace_ends_at:
            return LateDecision(True, Submission.LateStatus.GRACE, 0, "Accepted within the grace window")
        return LateDecision(False, None, 0, "The grace window has ended")

    raise ValueError(f"Unsupported late policy: {policy}")


def _tokens(text):
    return set(re.findall(r"[a-z0-9_]{3,}", text.lower()))


def similarity_stub(uploaded_file, comparison_submissions):
    """Return a transparent token-overlap score for text files only.

    This is intentionally a teaching stub, not a plagiarism detector.
    """
    try:
        uploaded_file.seek(0)
        current_text = uploaded_file.read().decode("utf-8", errors="ignore")
        uploaded_file.seek(0)
    except (AttributeError, UnicodeDecodeError):
        return Decimal("0.00")

    current_tokens = _tokens(current_text)
    if not current_tokens:
        return Decimal("0.00")

    best = 0.0
    for submission in comparison_submissions:
        try:
            with submission.file.open("rb") as previous_file:
                previous_tokens = _tokens(previous_file.read().decode("utf-8", errors="ignore"))
        except (OSError, UnicodeDecodeError):
            continue
        union = current_tokens | previous_tokens
        if union:
            best = max(best, len(current_tokens & previous_tokens) / len(union))
    return Decimal(str(round(best * 100, 2)))
