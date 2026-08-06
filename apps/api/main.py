from fastapi import FastAPI

from apps.api.router import auth

app = FastAPI()
app.include_router(auth.router)