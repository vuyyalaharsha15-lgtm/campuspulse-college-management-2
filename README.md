# CampusPulse — Supabase PostgreSQL edition

CampusPulse is the existing Flask college-event-management application, updated to use Supabase PostgreSQL instead of MySQL. Existing templates and routes are retained.

## Local setup
1. Install Python 3.10+ (or a version supported by your deployment host).
2. Create and activate a virtual environment.
3. Run `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`. Fill in `SECRET_KEY`, `DATABASE_URL`, `MAIL_USERNAME`, and `MAIL_PASSWORD`.
5. Start with `python app.py` (if your local setup uses Flask's standard entry point) or `flask --app app run`.

## Supabase connection
In Supabase, open **Project Settings → Database → Connect** and copy the PostgreSQL connection URI. Put it in `DATABASE_URL` in `.env`; do not put database credentials in HTML/JavaScript or commit `.env`. Use the pooler URI for serverless hosts if the direct connection is not available. The connection uses SSL by default.

## Email OTP
New registrations receive a six-digit OTP. The OTP expires after 10 minutes. An account remains unverified until the correct, unexpired OTP is entered; login redirects unverified accounts to verification. SMTP requires a Gmail App Password (not the normal Gmail account password) when using Gmail.

## Important notes
- This project ZIP includes the app-code migration only; it does not automatically copy records from your old MySQL database into Supabase. Import existing records separately after backing up the source data.
- The existing project stores passwords as plain text. Before public production use, migrate to password hashing and reset existing passwords.
- Never commit `.env` or publish database credentials.
