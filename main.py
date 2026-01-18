from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Імпортуємо мідлвар
from routers import auth, projects
from crud.database import engine
import models.models_db as models

# Створюємо таблиці при запуску
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="FlyZenWork API")

# Налаштування CORS
origins = [
    "http://localhost",
    "http://localhost:3000",  # Для React/Next.js
    "http://127.0.0.1:3000",
    "http://localhost:8000",  # Swagger/Docs
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(projects.router)

@app.get("/")
def home():
    return {"message": "Welcome to FlyZenWork API"}