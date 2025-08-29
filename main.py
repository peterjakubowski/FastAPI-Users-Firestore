from fastapi import FastAPI, Depends, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from db import get_user_db, DatabaseOperationError, UserNotFoundError, DuplicateUserError
from models import User, UserCreate, UserUpdate
from users import auth_backend, api_users
import logging


# Configure logging
logging.basicConfig(level=logging.INFO)


app = FastAPI()


# --- Global Exception Handlers ---

@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """
    Handles ValueError exceptions, commonly raised for malformed UUIDs,
    by returning a 400 Bad Request.
    """
    return JSONResponse(
        status_code=400,
        content={"message": str(exc)},
    )


@app.exception_handler(UserNotFoundError)
async def user_not_found_exception_handler(request: Request, exc: UserNotFoundError):
    """Handles UserNotFound errors by returning a 404 Not Found."""
    return JSONResponse(
        status_code=404,
        content={"message": str(exc)},
    )


@app.exception_handler(DuplicateUserError)
async def duplicate_user_exception_handler(request: Request, exc: DuplicateUserError):
    """Handles DuplicateUserError by returning a 409 Conflict."""
    return JSONResponse(
        status_code=409,
        content={"message": str(exc)},
    )


@app.exception_handler(DatabaseOperationError)
async def database_operation_exception_handler(request: Request, exc: DatabaseOperationError):
    """Handles generic database errors by returning a 500 Internal Server Error."""
    logging.error(f"Database operation error for request {request.url}: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred. Please try again later."},
    )


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000"],  # Add your frontend URL here
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

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
