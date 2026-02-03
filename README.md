# All Minnesota

Indigenous-led community meal distribution fundraising and awareness site (Django).

## Setup

1. Copy `.env.example` to `.env` and set `SECRET_KEY` (and `DATABASE_URL` if using PostgreSQL).
2. Install dependencies: `pip install -r requirements.txt`  
   (On Windows, gunicorn may fail; use `python manage.py runserver` for development.)
3. Run migrations: `python manage.py migrate`
4. Create a superuser: `python manage.py createsuperuser`
5. In Django admin (`/admin/`), create at least one **Fundraising Goal** (set title, target amount, and check "Is active") so the home page and dashboard show progress.
6. Run the server: `python manage.py runserver`

## URLs

- **Public:** `/`, `/about/`, `/events/`, `/how-it-works/`, `/impact/`, `/volunteer/`, `/contact/`
- **Dashboard (login required):** `/dashboard/`, `/dashboard/goal/`, `/dashboard/events/...`, `/dashboard/volunteers/`, `/dashboard/contacts/`
- **Django admin:** `/admin/`

The "Donate Now" button links to `#DONATE_PLACEHOLDER` (no payment processing).
