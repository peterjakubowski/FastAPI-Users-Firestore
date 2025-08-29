import logging
import uuid
from typing import Optional, AsyncGenerator

from fastapi_users.db import BaseUserDatabase
from google.api_core.exceptions import GoogleAPICallError, NotFound, GoogleAPIError
from google.cloud import firestore
from fastapi import Request

from models import User, UserCreate, UserUpdate
from dotenv import load_dotenv

load_dotenv()


# --- Custom Exceptions for the Database Layer ---

class DatabaseError(Exception):
    """Base exception for database-related errors."""
    pass


class UserNotFoundError(DatabaseError):
    """Raised when a user is not found in the database."""
    pass


class DuplicateUserError(DatabaseError):
    """Raised when attempting to create a user that already exists."""
    pass


class DatabaseOperationError(DatabaseError):
    """Raised for general database operation failures."""
    pass


# Initialize Firestore client
# In a deployed environment, service account credentials will be used automatically.
db = firestore.AsyncClient()

USERS_COLLECTION = "users"


class FirestoreUserDatabase(BaseUserDatabase[User, uuid.UUID]):
    """
    Database adapter for Firestore.

    :param: Pydantic model of a DB user.

    """

    async def get(self, id: uuid.UUID) -> Optional[User]:
        """Get a single user by id."""
        try:
            doc_ref = db.collection(USERS_COLLECTION).document(str(id))
            doc = await doc_ref.get()
            if doc.exists:
                return User(**doc.to_dict())
            raise UserNotFoundError(f"User with id {id} not found.")
        except UserNotFoundError:
            raise
        except (GoogleAPICallError, NotFound) as e:
            logging.error(f"Database error getting user {id}: {e}")
            raise DatabaseOperationError(f"Error accessing database: {e}")

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a single user by email"""
        try:
            query = db.collection(USERS_COLLECTION).where("email", "==", email.lower()).limit(1)
            async for doc in query.stream():
                return User(**doc.to_dict())
            # Return None as per FastAPI-Users' expectation for non-existent users during auth flows
            return None
        except (GoogleAPICallError, NotFound) as e:
            logging.error(f"Database error getting user by email {email}: {e}")
            raise DatabaseOperationError(f"Error accessing database: {e}")

    async def create(self, user: dict, safe: bool = False, request: Optional[Request] = None) -> User:
        """Create a new user."""
        try:
            # Check if user with this email already exists
            existing_user = await self.get_by_email(user["email"])
            if existing_user:
                raise DuplicateUserError(f"User with email {user['email']} already exists.")

            # Create a User object from the UserCreate schema
            new_user = User(**user, id=uuid.uuid4())

            # Convert the Pydantic model to a dict for Firestore
            user_dict = new_user.model_dump()
            user_dict.update({'id': str(user_dict.get('id'))})

            # Firestore needs string ids
            user_id = str(new_user.id)

            await db.collection(USERS_COLLECTION).document(user_id).set(user_dict)
            return new_user
        except DuplicateUserError:
            raise
        except GoogleAPICallError as e:
            logging.error(f"Error creating user: {e}")
            raise DatabaseOperationError(f"Error creating user in database: {e}")

    async def update(self, user: User, update_dict: dict) -> User:
        """Update a user."""
        try:
            # Update the user a with the update values
            for key, value in update_dict.items():
                setattr(user, key, value)

            # Convert back to a plain dict for Firestore
            updated_payload = user.model_dump()
            updated_payload.update({'id': str(updated_payload.get('id'))})

            await db.collection(USERS_COLLECTION).document(str(user.id)).set(updated_payload, merge=True)
            return user
        except GoogleAPICallError as e:
            logging.error(f"Error updating user {user.id}: {e}")
            raise DatabaseOperationError(f"Error updating user in database: {e}")

    async def delete(self, user: User) -> None:
        """Delete a user."""
        try:
            await db.collection(USERS_COLLECTION).document(str(user.id)).delete()
        except GoogleAPICallError as e:
            logging.error(f"Error deleting user {user.id}: {e}")
            raise DatabaseOperationError(f"Error deleting user from database: {e}")


# Dependency to get the user db
async def get_user_db() -> AsyncGenerator[FirestoreUserDatabase, None]:
    yield FirestoreUserDatabase()
