#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# rm db.sqlite3
# Apply database migrations
python manage.py migrate

# Seed initial data (if any)

python manage.py loaddata initial_data.json
python manage.py loaddata additional_transactions.json
python manage.py loaddata additional_donation_data.json
python manage.py loaddata ratings_additional_data.json

# python set_admin_claims.py

# python manage.py loaddata initial_data.json
# Bash

# python manage.py loaddata initial_data.json
# Login details:

# Admin Email: admin@example.com

# Donor Emails: donor1@example.com through donor9@example.com

# Password for ALL users: password123
