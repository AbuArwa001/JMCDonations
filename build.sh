#!/usr/bin/env bash
# Exit on error
set -o errexit

# Install dependencies
pip install -r requirements.txt

# Collect static files
python manage.py collectstatic --no-input

# Apply database migrations
python manage.py migrate

# Seed initial data (if any)
python manage.py loaddata initial_data.json


# Bash

# python manage.py loaddata initial_data.json
# Login details:

# Admin Email: admin@example.com

# Donor Emails: donor1@example.com through donor9@example.com

# Password for ALL users: password123
