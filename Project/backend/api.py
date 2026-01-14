from fastapi import FastAPI
from .auth.controller import auth_router
from .chat.controller import chat_router
from .static.controller import static_router

def register_routes(app: FastAPI):
    app.include_router(auth_router)
    app.include_router(chat_router)
    app.include_router(static_router)