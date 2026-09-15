# Church Roster

A minimal volunteer-scheduling app: assign volunteers to roles for a
service week, email them, and let them approve/decline with one click —
visible live to office staff in the admin panel.

## What's in here

- `scheduling/models.py` — Volunteer, Role, ServiceWeek, Assignment
- Django admin (`/admin/`) — this is your office dashboard: create weeks,
  assign volunteers to roles, see who's approved/declined/pending, and
  trigger emails with a bulk action.
- `/respond/<token>/` — the page a volunteer lands on from their email,
  with Approve / Decline buttons.
- `python manage.py send_assignment_emails --week YYYY-MM-DD` — emails
  everyone pending for that week.

## Get it running locally (10 min)

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `http://127.0.0.1:8000/admin/` and log in. With no `EMAIL_HOST`
env var set, emails print to your terminal instead of sending — good
for testing the flow before it's live.

Try it end to end locally:
1. Add a Role (e.g. "Sound"), a Volunteer (your own email), a
   ServiceWeek (any upcoming Sunday).
2. Add an Assignment linking them together.
3. Run `python manage.py send_assignment_emails --week 2026-09-20`
   (use your ServiceWeek's date) — the email prints to your terminal
   with a respond link.
4. Copy that link into your browser, click Approve.
5. Refresh the Assignment in `/admin/` — status is now "Approved".

That loop is the whole product. Everything else is polish.

## Deploy today

### 1. Push to GitHub
```bash
cd church_roster
git init
git add .
git commit -m "Initial roster app"
gh repo create church-roster --private --source=. --push
# or create a repo on github.com and follow its "push an existing repo" instructions
```

### 2. Set up email sending
Sign up for **Resend** (resend.com) — free tier, fast to set up, and
gives you SMTP credentials without needing domain verification to get
started (their test sender works immediately; verify your own domain
later for production-quality deliverability). SendGrid or Mailgun work
identically — just different SMTP hosts.

### 3. Deploy to Render
Easiest path: in the Render dashboard, choose **New +** → **Blueprint**,
point it at your GitHub repo — it reads `render.yaml` and creates the
web service *and* the Postgres database together.

Then, in the web service's Environment tab, add:
- `EMAIL_HOST`, `EMAIL_PORT`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD`
  (from Resend/SendGrid)
- `DEFAULT_FROM_EMAIL` (e.g. `roster@yourchurch.org`)
- `SITE_URL` — set this **after** the first deploy, once Render gives
  you the live URL (e.g. `https://church-roster.onrender.com`)

`SECRET_KEY` and `DATABASE_URL` are already handled by the blueprint.

### 4. Create your admin login
In Render, open the web service's **Shell** tab and run:
```bash
python manage.py createsuperuser
```

### 5. Try it for real
Log into `https://<your-app>.onrender.com/admin/`, add a couple of
real roles/volunteers/a service week/assignments, and either use the
"Email selected volunteers their assignment" admin action or run the
management command from the Shell tab.

## Realistic scope for "today"

What you can have live today: the full assign → email → approve →
visible-in-admin loop, for one small team, run manually by you from
the admin panel.

What's *not* in here yet, for later days: recurring rotation logic
(auto-avoiding people who served last week), a nicer non-admin
dashboard for office staff, SMS reminders, a self-serve "set your
regular unavailability" page, and scheduled/automatic email sends
(you'd add a Render Cron Job for that once the manual flow feels
solid).
