from django.core.management.base import BaseCommand
from requests_app.models import ServiceRequest


class Command(BaseCommand):
    help = "Print the Task 3 queryset SQL and EXPLAIN output."

    def handle(self, *args, **options):
        queryset = (
            ServiceRequest.objects
            .filter(
                category__name="ICT Support",
                status__in=[
                    ServiceRequest.Status.OPEN,
                    ServiceRequest.Status.ASSIGNED,
                ],
            )
            .order_by("priority", "created_at")
        )

        self.stdout.write("QUERYSET:")
        self.stdout.write(str(queryset.query))
        self.stdout.write("\nEXPLAIN:")
        self.stdout.write(queryset.explain())
        self.stdout.write(
            "\nAnalysis: the dataset contains only 10 synthetic rows. "
            "If MySQL chooses a table scan, record that the optimizer may consider "
            "the small table cheaper to scan than to use an index."
        )
