import uuid
from typing import Optional, AsyncGenerator

from fastapi_users.db import BaseUserDatabase
from google.cloud import firestore
from fastapi import Request

from models import User, UserCreate, UserUpdate

from dotenv import load_dotenv

load_dotenv()

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
        doc_ref = db.collection(USERS_COLLECTION).document(str(id))
        doc = await doc_ref.get()
        if doc.exists:
            return User(**doc.to_dict())
        return None

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get a single user by email"""
        query = db.collection(USERS_COLLECTION).where("email", "==", email.lower()).limit(1)
        async for doc in query.stream():
            return User(**doc.to_dict())
        return None

    async def create(self, user: dict, safe: bool = False, request: Optional[Request] = None) -> User:
        """Create a new user."""
        # Create a User object from the UserCreate schema
        new_user = User(**user, id=uuid.uuid4())

        # Convert the Pydantic model to a dict for Firestore
        user_dict = new_user.model_dump()
        user_dict.update({'id': str(user_dict.get('id'))})

        # Firestore needs string ids
        user_id = str(new_user.id)

        await db.collection(USERS_COLLECTION).document(user_id).set(user_dict)
        return new_user

    async def update(self, user: User, update_dict: dict) -> User:
        """Update a user."""
        # Create a new dict with the update values
        updated_user_data = {**user.model_dump(), **update_dict}
        updated_user = User(**updated_user_data)

        # Convert back to a plain dict for Firestore
        updated_payload = updated_user.model_dump()
        updated_payload.update({'id': str(updated_payload.get('id'))})

        await db.collection(USERS_COLLECTION).document(str(user.id)).set(updated_payload, merge=True)
        return updated_user

    async def delete(self, user: User) -> None:
        """Delete a user."""
        await db.collection(USERS_COLLECTION).document(str(user.id)).delete()


# Dependency to get the user db
async def get_user_db() -> AsyncGenerator[FirestoreUserDatabase, None]:
    yield FirestoreUserDatabase()
