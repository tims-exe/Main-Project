from fastapi import FastAPI
from .auth.controller import auth_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)