from fastapi import FastAPI

from apps.api.router import auth, organizations

app = FastAPI()
app.include_router(auth.router)
app.include_router(organizations.router)
