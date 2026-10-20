import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    DATABASE_URL = os.getenv("DATABASE_URL")
    DB_SSLMODE = os.getenv("DB_SSLMODE", "require")
