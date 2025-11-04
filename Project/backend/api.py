from fastapi import FastAPI
from .auth.controller import auth_router
from .model.controller import model_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(model_router)