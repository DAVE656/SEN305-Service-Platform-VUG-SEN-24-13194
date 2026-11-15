# VUA SEN305 — In-Lab Exercise 0002

This is a clean starting project reconstructed from the uploaded VUA SEN305 Lab Session 3 notes, with the required Part N extension represented as migration `0002`.

The notes specify Django 5.2, MySQL 8, the `requests_app` application, the `Category`, `ServiceRequest`, `WorkOrder`, and `Comment` domain models, and the original `ServiceRequest` fields. The exercise requires extending that model without changing `0001`.

## Setup

From the project root:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
cd backend
python -m pip install -r requirements.txt
```

If PowerShell blocks activation, use Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

## MySQL

Create the laboratory MySQL database/user as instructed in the class notes. Then copy:

```text
backend/.env.example
```

to:

```text
backend/.env
```

and enter your local password. Never commit `.env`.

Before migrating:

```powershell
python manage.py check
```

## Migration discipline

The project intentionally contains:

```text
requests_app/migrations/0001_initial.py
requests_app/migrations/0002_service_request_due_date_and_resolution.py
```

Do not edit `0001_initial.py`.

Inspect:

```powershell
python manage.py sqlmigrate requests_app 0002
```

Apply:

```powershell
python manage.py migrate
python manage.py showmigrations requests_app
```

Both `0001` and `0002` should show `[X]`.

## Admin

Create a lab-only administrator:

```powershell
python manage.py createsuperuser
python manage.py runserver
```

Open:

```text
http://127.0.0.1:8000/admin/
```

Service Requests show `due_at`, `resolved_at`, and `resolution_summary`, with an Overdue filter and resolution-summary search.

## Synthetic data

Create the required ten-record laboratory dataset:

```powershell
python manage.py lab_seed
```

It creates two categories (`Electrical`, `ICT Support`) and three statuses in the seed (`open`, `assigned`, `resolved`), using only synthetic data. It also assigns different due dates.

For Task 1:

```powershell
python manage.py shell
```

```python
from django.utils import timezone
from requests_app.models import ServiceRequest

chosen_time = timezone.now()
qs = ServiceRequest.objects.filter(due_at__lt=chosen_time)
print(qs)
print(qs.count())
exit()
```

## Resolution validation

```powershell
python manage.py shell
```

```python
from django.core.exceptions import ValidationError
from django.utils import timezone
from requests_app.models import ServiceRequest

bad = ServiceRequest.objects.first()
bad.status = ServiceRequest.Status.RESOLVED
bad.resolved_at = None
bad.resolution_summary = ""

try:
    bad.full_clean()
except ValidationError as exc:
    print("EXPECTED ValidationError:")
    print(exc)

good = ServiceRequest.objects.first()
good.status = ServiceRequest.Status.RESOLVED
good.resolved_at = timezone.now()
good.resolution_summary = "Synthetic laboratory issue resolved."
good.full_clean()
print("VALID resolved record passed full_clean().")
exit()
```

## Task 3 SQL and EXPLAIN

Run:

```powershell
python manage.py lab_query
```

It prints `queryset.query` and `queryset.explain()` for open/assigned requests in `ICT Support`, ordered by priority and created date.

Record the actual EXPLAIN output you receive. With only ten rows, MySQL may choose a table scan because the dataset is too small for an index to be cheaper.

## Tests

```powershell
python manage.py test requests_app -v 2
python manage.py check
python manage.py makemigrations --check --dry-run
```

The tests contain the original Lab 3 model tests plus the new 0002 validation/due-date tests.

Only synthetic laboratory data should be used.
