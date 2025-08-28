import uuid

from fastapi import FastAPI, Depends

from db import get_user_db
from models import User, UserCreate, UserUpdate
from users import auth_backend, api_users

app = FastAPI()

# Include the main auth router
app.include_router(
    api_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"]
)

# Include the registration router
app.include_router(
    api_users.get_register_router(User, UserCreate),
    prefix="/auth",
    tags=["auth"]
)

# Include the user management router
app.include_router(
    api_users.get_users_router(User, UserUpdate),
    prefix="/users",
    tags=["users"]
)


# --- Protected Route ---

@app.get("/authenticated-route")
def authenticated_route(user: User = Depends(api_users.current_user(active=True))):
    """
    An example of a protected route.

    This route will only be accessible to authenticated and active users.
    """
    return {"message": f"Hello {user.email}"}


# --- Root Route ---

@app.get("/")
def read_root():
    return {"Hello": "World"}
