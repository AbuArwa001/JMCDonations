<!-- Copilot instructions for the JMCDonations codebase -->
# JMCDonations — Copilot Instructions

Purpose: help AI coding agents become productive quickly in this Django + DRF repository.

1) Quick start (commands)

```bash
# create venv, install deps
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# apply DB migrations and create an admin
python manage.py migrate
python manage.py createsuperuser

# run development server
python manage.py runserver

# run tests
python manage.py test
```

2) Big picture

- This is a Django REST API (DRF) with the following app boundaries (top-level directories):
  - `users`: custom user model and auth flows (`AUTH_USER_MODEL = 'users.Users'` in `JMCDonations/settings.py`).
  - `donations`: donation models, PDF receipt generation (uses ReportLab), saved donations, and viewsets (`donations/views.py`).
  - `transactions`: payment handling, MPESA/Daraja integration (`transactions/daraja.py`) and transaction viewset (`transactions/views.py`).
  - `analytics`, `ratings`, `categories`: reporting, rating, and classification features.

- Auth & integrations:
  - Authentication: Djoser + JWT + social auth (`drf_social_oauth2`). Check `JMCDonations/settings.py` for backends and `djoser` serializers.
  - MPESA (Daraja): wrapped in `transactions/daraja.py` via `MpesaClient`. Settings keys live in `JMCDonations/settings.py` (e.g. `MPESA_CONSUMER_KEY`, `MPESA_CALLBACK_URL`).
  - Firebase: initialized from `firebase_config.py` using `FIREBASE_SERVICE_ACCOUNT_PATH` environment variable.

3) Code patterns & conventions (concrete, discoverable)

- App layout: each app follows the typical Django app layout with `models.py`, `serializers.py`, `views.py`, `urls.py`, and `tests.py`.
- Views use DRF patterns:
  - Prefer `viewsets.ModelViewSet` for resource CRUD (see `donations.views.DonationViewSet`).
  - For list/create filtered by user, use `generics.ListCreateAPIView` and override `get_queryset()` and `perform_create()` to attach `request.user` (see `donations.views.SavedDonationView`).
  - Use `APIView` for custom endpoints that return non-model responses (see `donations.views.ReceiptView`).
- Use `get_object_or_404()` for fetching single resources and raise 404 if missing.
- Permissions: endpoints that change data generally use `permissions.IsAuthenticated`. Check and mirror existing patterns when adding endpoints.

4) Integrations & env secrets (what to set)

- MPESA / Daraja: set environment or local settings for `MPESA_CONSUMER_KEY`, `MPESA_CONSUMER_SECRET`, `MPESA_PASSKEY`, `MPESA_SHORTCODE`, and `MPESA_CALLBACK_URL`. `transactions/daraja.py` expects these keys via Django settings.
- Firebase: set `FIREBASE_SERVICE_ACCOUNT_PATH` to a JSON service account file path (see `firebase_config.py`).
- JWT / social auth: client IDs/secrets for Google/Facebook show as stubs in `JMCDonations/settings.py`; update them in a local settings file or via environment variables before running social flows.

5) Tests & debugging

- Run `python manage.py test` to execute app tests (tests are located in each app's `tests.py`).
- To reproduce API behavior interactively, run the server and open the Swagger UI at `/swagger/` (routes configured in `JMCDonations/urls.py`).
- If a test or local run hits external APIs (MPESA, Firebase), mock those calls in tests or set sandbox/test credentials (Daraja sandbox URL is configured by default in settings).

6) Common edits and examples (copy-paste friendly)

- Add a new endpoint that creates a model tied to the current user:

  - Use `generics.CreateAPIView` or `ListCreateAPIView`.
  - In `perform_create(self, serializer)`: call `serializer.save(user=self.request.user)`.

- Call MPESA STK push from backend (example):

```python
from transactions.daraja import MpesaClient
cl = MpesaClient()
resp = cl.stk_push(phone_number='+2547xxxxxxx', amount=100, account_reference='donation-123', transaction_desc='Donation')
```

7) Files to inspect for context

- `JMCDonations/settings.py` — auth backends, DRF, MPESA placeholders, and SWAGGER settings.
- `JMCDonations/urls.py` — where app URL mounts and the Swagger UI live.
- `transactions/daraja.py` — MPESA wrapper; copy patterns for external API wrappers (requests + token handling).
- `firebase_config.py` — firebase initialization pattern (guard against re-initializing apps).
- `donations/views.py`, `transactions/views.py`, `users/serializers.py` — examples of view/serializer interactions.

8) Small gotchas observed

- `requirements.txt` lists main packages but some runtime imports used in settings/views (e.g., `rest_framework_simplejwt`, `firebase-admin`, `requests`) may be missing from `requirements.txt`. Verify installed packages before running.
- Settings contain plaintext secrets and stubs. Prefer local settings or environment variables for production secrets.

If any section seems incomplete or you'd like examples for a specific task (adding an endpoint, writing tests, modifying MPESA flow), tell me which area to expand and I'll update this file accordingly.
