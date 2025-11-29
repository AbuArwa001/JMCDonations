import firebase_admin
from firebase_admin import credentials
import os

# Get path from environment variable for security
SERVICE_ACCOUNT_PATH = os.environ.get(
    "FIREBASE_SERVICE_ACCOUNT_PATH", "path/to/your/serviceAccountKey.json"
)

if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
