import uuid
from typing import Optional
from fastapi import Depends, Request
from fastapi_users import BaseUserManager, FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    CookieTransport,
    JWTStrategy
)

from db import get_user_db, FirestoreUserDatabase
from models import User


# --- User Manager ---
class UserManager(BaseUserManager[User, uuid.UUID]):
    reset_password_token_secret = "YOUR_SECRET_KEY_HERE"
    verification_token_secret = "YOUR_SECRET_KEY_HERE"

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered.")

    def parse_id(self, id: str) -> uuid.UUID:
        return uuid.UUID(id)


async def get_user_manager(user_db: FirestoreUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)

# --- Authentication Backend ---
SECRET = "aa7658b3da4724caf41d2e0566eb4669c45393c7be2efb41225294a96adc9a32"


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(secret=SECRET, lifetime_seconds=3600)


cookie_transport = CookieTransport(cookie_name="bonds", cookie_max_age=3600)

auth_backend = AuthenticationBackend(
    name="jwt",
    transport=cookie_transport,
    get_strategy=get_jwt_strategy
)

api_users = FastAPIUsers[User, uuid.UUID](
    get_user_manager,
    [auth_backend]
)
