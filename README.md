# FastAPI-Users-Firestore

FastAPI server using FastAPI-Users to manage users and auth with a Firestore database.

## Run FastAPI Server

```commandline
uvicorn main:app --reload
```

## Authentication Backend

Requires secret, generate with openssl.

```commandline
openssl rand -hex 32
```
