from fastapi import FastAPI
from routers import auth
from crud.database import engine
import models.models_db as models

# Створюємо таблиці при запуску
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlyZenWork API")

app.include_router(auth.router)

@app.get("/")
def home():
    return {"message": "Welcome to FlyZenWork API"}