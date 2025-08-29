# FastAPI-Users-Firestore

This project provides a starting point for a FastAPI server that uses FastAPI-Users for user management and authentication, connected to a Google Firestore database as the backend.

It is configured with a JWT authentication backend, Pydantic for settings management, and follows modern FastAPI best practices.

## 🚀 Getting Started

### Prerequisites

* Python 3.8+

* A Google Cloud Platform (GCP) project with Firestore enabled.

* The Google Cloud CLI installed and authenticated (for local development).

### 1. Installation

Clone the repository and install the required dependencies:

```commandline
git clone https://your-repository-url/FastAPI-Users-Firestore.git
cd FastAPI-Users-Firestore
pip install -r requirements.txt
```

### 2. Environment Configuration

This project uses a `.env` file for managing secrets and configuration during local development.

1. Create a file named `.env` in the root of the project.

2. Add the required environment variables as listed below.

```commandline
# .env file

# JWT Secrets (generate with `openssl rand -hex 32`)
AUTHENTICATION_BACKEND_SECRET=your_32-byte_hex_secret_for_jwt
RESET_PASSWORD_TOKEN_SECRET=your_32-byte_hex_secret_for_password_resets
VERIFICATION_TOKEN_SECRET=your_32-byte_hex_secret_for_email_verification

# Google Cloud Credentials (for local development using a service account)
# GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/gcp-service-account.json"
```

### 3. Google Cloud Authentication

For the application to communicate with Firestore, you need to provide Google Cloud credentials.

#### Recommended Method (Local Development)

Use the `gcloud` CLI to set up Application Default Credentials (ADC). This is the most secure and straightforward method for your local machine.

```commandline
gcloud auth application-default login
```

#### Alternative Method (Service Account)

If you prefer to use a service account key file:

1. In your GCP project, create a service account and grant it the "Cloud Datastore User" role.

2. Download the JSON key file for the service account.

3. Uncomment and set the GOOGLE_APPLICATION_CREDENTIALS variable in your .env file to the absolute path of the downloaded JSON file.

### 4. Run the FastAPI Server

Once your environment is configured, you can run the server using Uvicorn:

```commandline
uvicorn main:app --reload
```

The API documentation will be available at http://127.0.0.1:8000/docs.

### API Endpoints

The server exposes the following sets of endpoints, managed by FastAPI-Users.

`/auth`

/auth/jwt/login: User login to get an authentication token.

/auth/jwt/logout: User logout.

/auth/register: New user registration.

`/users`

/users/me: Get details for the currently authenticated user.

/users/{id}: Get details for any user (admin only).

/users/me: Update details for the currently authenticated user.

#### Protected Route

/authenticated-route: An example endpoint that is only accessible to authenticated and active users.
