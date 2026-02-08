# JMC Donations Backend API

![Project Status](https://img.shields.io/badge/status-active-success.svg)
![Django](https://img.shields.io/badge/Django-5.0-092E20)
![Python](https://img.shields.io/badge/Python-3.12-blue)
![Rest Framework](https://img.shields.io/badge/DRF-3.14-red)

## 📖 Overview

The **JMC Donations Backend** is the robust server-side application powering the Jamia Mosque Committee's digital ecosystem. It provides a secure, scalable REST API for handling donation processing, user authentication, and system analytics.

Built with **Django Rest Framework (DRF)**, it ensures high performance and reliability, integrating seamlessly with mobile and web clients.

## ✨ Key Features

- **🔐 Advanced Authentication**: JWT-based authentication using `SimpleJWT` and `Djoser`, supporting social login (Google/Facebook via `social-auth-app-django`).
- **💳 Donation Processing**: Secure endpoints for managing donation transactions and history.
- **⚡ Asynchronous Tasks**: Integrated **Celery** and **Redis** for handling background jobs like report generation and email notifications.
- **🔥 Firebase Integration**: Syncs data with Firebase/Firestore for real-time updates and notifications using `firebase-admin`.
- **📖 API Documentation**: Auto-generated Swagger/OpenAPI documentation via `drf-spectacular`.
- **☁️ Cloud Storage**: AWS S3 (`boto3`) and Google Cloud Storage integration for media handling.

## 🛠️ Tech Stack

- **Framework**: [Django 5](https://www.djangoproject.com/) & [Django Rest Framework](https://www.django-rest-framework.org/)
- **Database**: SQLite (Development) / PostgreSQL (Production)
- **Task Queue**: [Celery](https://docs.celeryq.dev/) & [Redis](https://redis.io/)
- **Documentation**: Swagger / OpenAPI (`drf-spectacular`)
- **Containerization**: Docker (optional/implied support)
- **Utilities**: `django-filter`, `django-cors-headers`, `WhiteNoise`

## 🚀 Getting Started

Follow these steps to set up the backend locally.

### Prerequisites

- Python 3.10+
- Redis (for Celery tasks)

### Installation

1.  **Clone the repository**

    ```bash
    git clone https://github.com/AbuArwa001/JMCDonations.git
    cd JMCDonations
    ```

2.  **Create a Virtual Environment**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install Requirements**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Environment Configuration**
    Create a `.env` file in the root directory:

    ```env
    DEBUG=True
    SECRET_KEY=your_secret_key
    ALLOWED_HOSTS=localhost,127.0.0.1
    # Database
    DATABASE_URL=sqlite:///db.sqlite3
    # Celery
    CELERY_BROKER_URL=redis://localhost:6379/0
    # Firebase
    FIREBASE_CREDENTIALS=path/to/serviceAccountKey.json
    ```

5.  **Run Migrations**

    ```bash
    python manage.py migrate
    ```

6.  **Create Superuser**

    ```bash
    python manage.py createsuperuser
    ```

7.  **Run Development Server**
    ```bash
    python manage.py runserver
    ```
    Access the API at [http://localhost:8000/api/](http://localhost:8000/api/).
    View API Docs at [http://localhost:8000/api/schema/swagger-ui/](http://localhost:8000/api/schema/swagger-ui/).

## 📂 Project Structure

```bash
├── JMCDonations/       # Project settings and configuration
├── authentication/     # User auth logic (JWT, Social)
├── donations/         # Donation models and logic
├── transactions/      # Payment processing logic
├── users/             # Custom user model and profiles
├── analytics/         # Reporting and stats
├── manage.py          # Django CLI utility
└── requirements.txt   # Python dependencies
```

## 🤝 Contributing

1.  Fork the repo.
2.  Create a feature branch.
3.  Commit your changes.
4.  Push and open a PR.

## 📄 License

Proprietary software. All rights reserved by **Jamia Mosque Committee**.
