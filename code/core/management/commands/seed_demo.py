from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.models import Assignment, ChecklistItem, Company, PlacementRound, ReminderLog, User


class Command(BaseCommand):
    help = "Create deterministic Week 7 demo accounts and sample deadlines."

    def handle(self, *args, **options):
        accounts = [
            ("student", "Student@W7", User.Role.STUDENT, "Aarav", "Mehta", "1024030999"),
            ("ta", "Faculty@W7", User.Role.TA, "Meera", "Sharma", ""),
            ("placement", "Placement@W7", User.Role.PLACEMENT_ADMIN, "Kabir", "Singh", ""),
        ]
        users = {}
        for username, password, role, first_name, last_name, roll_number in accounts:
            user, _ = User.objects.update_or_create(
                username=username,
                defaults={
                    "role": role,
                    "first_name": first_name,
                    "last_name": last_name,
                    "roll_number": roll_number,
                    "email": f"{username}@deadlinedesk.local",
                },
            )
            user.set_password(password)
            user.save()
            users[role] = user

        now = timezone.now()
        company, _ = Company.objects.update_or_create(
            name="Northstar Systems",
            defaults={
                "description": "Sample campus placement company for the Week 7 demonstration.",
                "created_by": users[User.Role.PLACEMENT_ADMIN],
            },
        )
        placement_round, _ = PlacementRound.objects.update_or_create(
            company=company,
            title="Software Engineering Technical Round",
            defaults={
                "opens_at": now - timedelta(days=1),
                "closes_at": now + timedelta(days=2),
                "status": PlacementRound.Status.PUBLISHED,
                "created_by": users[User.Role.PLACEMENT_ADMIN],
            },
        )
        for position, title in enumerate(["Updated resume", "Government photo ID", "Latest grade transcript"], start=1):
            ChecklistItem.objects.update_or_create(
                placement_round=placement_round,
                title=title,
                defaults={"required": True, "position": position},
            )
        ReminderLog.objects.update_or_create(
            placement_round=placement_round,
            scheduled_for=placement_round.closes_at - timedelta(hours=24),
            defaults={"created_by": users[User.Role.PLACEMENT_ADMIN]},
        )
        Assignment.objects.update_or_create(
            title="Requirements Traceability Exercise",
            defaults={
                "description": "Submit a concise requirements traceability matrix connecting user stories, acceptance criteria, and test cases.",
                "due_at": now + timedelta(days=1),
                "late_policy": Assignment.LatePolicy.GRACE,
                "grace_minutes": 60,
                "penalty_percent": 0,
                "created_by": users[User.Role.TA],
            },
        )

        self.stdout.write(self.style.SUCCESS("Week 7 demo data is ready."))
        self.stdout.write("student / Student@W7")
        self.stdout.write("ta / Faculty@W7")
        self.stdout.write("placement / Placement@W7")
