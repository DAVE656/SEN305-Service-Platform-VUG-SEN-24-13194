from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import ProtectedError
from django.test import TestCase
from django.utils import timezone

from .models import Category, ServiceRequest, WorkOrder


class ServiceRequestModelTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.requester = User.objects.create_user(username="requester")
        self.technician = User.objects.create_user(username="technician")
        self.category = Category.objects.create(name="Electrical")

    def make_request(self, **overrides):
        values = {
            "requester": self.requester,
            "category": self.category,
            "title": "Faulty socket",
            "description": "Socket does not supply power.",
            "location": "Software Engineering Lab",
            "priority": 2,
        }
        values.update(overrides)
        return ServiceRequest.objects.create(**values)

    # Original Lab 3 tests
    def test_default_status_is_open(self):
        item = self.make_request()
        self.assertEqual(item.status, ServiceRequest.Status.OPEN)

    def test_priority_validator_rejects_zero(self):
        item = ServiceRequest(
            requester=self.requester,
            category=self.category,
            title="Invalid",
            description="Invalid priority.",
            location="Lab",
            priority=0,
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_database_constraint_rejects_priority_six(self):
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                self.make_request(priority=6)

    def test_category_in_use_is_protected(self):
        self.make_request()
        with self.assertRaises(ProtectedError):
            self.category.delete()

    def test_request_accepts_only_one_work_order(self):
        item = self.make_request()
        WorkOrder.objects.create(service_request=item, technician=self.technician)
        with self.assertRaises(IntegrityError):
            with transaction.atomic():
                WorkOrder.objects.create(
                    service_request=item, technician=self.technician
                )

    # New 0002 exercise tests
    def test_resolved_requires_resolved_at(self):
        item = self.make_request(
            status=ServiceRequest.Status.RESOLVED,
            resolution_summary="Issue fixed.",
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_resolved_requires_non_empty_summary(self):
        item = self.make_request(
            status=ServiceRequest.Status.RESOLVED,
            resolved_at=timezone.now(),
            resolution_summary="   ",
        )
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_closed_requires_both_fields(self):
        item = self.make_request(status=ServiceRequest.Status.CLOSED)
        with self.assertRaises(ValidationError):
            item.full_clean()

    def test_valid_resolved_request_passes_full_clean(self):
        item = self.make_request(
            status=ServiceRequest.Status.RESOLVED,
            resolved_at=timezone.now(),
            resolution_summary="Network connection restored.",
        )
        item.full_clean()

    def test_due_date_filter_returns_only_due_records(self):
        now = timezone.now()
        self.make_request(due_at=now - timedelta(hours=1))
        self.make_request(
            title="Future request",
            due_at=now + timedelta(hours=1),
        )
        self.assertEqual(
            ServiceRequest.objects.filter(due_at__lt=now).count(), 1
        )

    def test_status_due_index_is_declared(self):
        names = {index.name for index in ServiceRequest._meta.indexes}
        self.assertIn("req_status_due_idx", names)
