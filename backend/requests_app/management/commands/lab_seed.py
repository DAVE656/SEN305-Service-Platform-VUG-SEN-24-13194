from datetime import timedelta

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone

from requests_app.models import Category, ServiceRequest


class Command(BaseCommand):
    help = "Create synthetic laboratory data for the SEN305 0002 exercise."

    def handle(self, *args, **options):
        User = get_user_model()
        requester, _ = User.objects.get_or_create(username="lab_requester")
        requester.set_password("LabPass123!")
        requester.save()

        electrical, _ = Category.objects.get_or_create(
            name="Electrical", defaults={"description": "Synthetic electrical category"}
        )
        ict, _ = Category.objects.get_or_create(
            name="ICT Support", defaults={"description": "Synthetic ICT category"}
        )

        now = timezone.now()
        rows = [
            (electrical, "open", 1),
            (electrical, "assigned", 2),
            (electrical, "resolved", 3),
            (electrical, "open", 2),
            (electrical, "assigned", 1),
            (ict, "open", 3),
            (ict, "assigned", 2),
            (ict, "resolved", 1),
            (ict, "open", 1),
            (ict, "assigned", 3),
        ]

        for number, (category, status, priority) in enumerate(rows, start=1):
            defaults = {
                "requester": requester,
                "category": category,
                "title": f"Synthetic lab request {number:02d}",
                "description": "Synthetic data created only for the SEN305 laboratory exercise.",
                "location": f"Synthetic Lab Room {number:02d}",
                "priority": priority,
                "status": status,
                "due_at": now + timedelta(days=number - 5),
            }
            if status == "resolved":
                defaults["resolved_at"] = now - timedelta(hours=number)
                defaults["resolution_summary"] = "Synthetic issue resolved for laboratory testing."
            else:
                defaults["resolved_at"] = None
                defaults["resolution_summary"] = ""
            item, _ = ServiceRequest.objects.update_or_create(
                title=defaults["title"], defaults=defaults
            )
            item.full_clean()
            item.save()

        self.stdout.write(self.style.SUCCESS(
            "Created/updated 10 synthetic ServiceRequest records across Electrical and ICT Support."
        ))
