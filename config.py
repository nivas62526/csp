"""
Smart Poultry Farm Management System - Configuration Layer
Loads environment variables and sets up MySQL 8 / SQLAlchemy / JWT / SMS settings.
Includes smart MySQL connection checking with seamless fallback for dev/test environments.
"""

import os
import socket
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

def resolve_database_uri(db_engine, db_user, db_password, db_host, db_port, db_name, sqlite_path):
    """
    Constructs MySQL 8 URI. If MySQL is unreachable on specified host:port,
    smoothly falls back to SQLite for local development and test stability.
    """
    custom_url = os.environ.get("DATABASE_URL")
    if custom_url:
        return custom_url

    if db_engine == "sqlite":
        return f"sqlite:///{sqlite_path}"

    mysql_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}?charset=utf8mb4"

    # Quick port probe (1 second timeout)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.8)
            result = sock.connect_ex((db_host, int(db_port)))
            if result == 0:
                return mysql_uri
            else:
                # Fall back to SQLite
                return f"sqlite:///{sqlite_path}"
    except Exception:
        return mysql_uri

class Config:
    # Flask Core
    SECRET_KEY = os.environ.get("SECRET_KEY", "smart_poultry_super_secret_jwt_key_2026_dev")
    DEBUG = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1", "yes")

    # Database Configuration (MySQL 8)
    DB_ENGINE = os.environ.get("DB_ENGINE", "mysql").lower()
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
    DB_HOST = os.environ.get("DB_HOST", "127.0.0.1")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_NAME = os.environ.get("DB_NAME", "smart_poultry")

    MYSQL_DATABASE_URI = (
        f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"
    )
    SQLITE_DATABASE_PATH = os.path.join(BASE_DIR, "poultry_farm.db")
    SQLITE_DATABASE_URI = f"sqlite:///{SQLITE_DATABASE_PATH}"

    # Resolve active URI with connectivity probe
    SQLALCHEMY_DATABASE_URI = resolve_database_uri(
        DB_ENGINE, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME, SQLITE_DATABASE_PATH
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 280,
    }

    # JWT Authentication Configuration
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "smart_poultry_jwt_secret_token_secure_key_2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=int(os.environ.get("JWT_ACCESS_TOKEN_EXPIRES_HOURS", 72)))
    JWT_TOKEN_LOCATION = ["headers", "cookies"]
    JWT_HEADER_NAME = "Authorization"
    JWT_HEADER_TYPE = "Bearer"

    # SMS Gateway & OTP Verification Policies
    SMS_PROVIDER = os.environ.get("SMS_PROVIDER", "mock").lower()
    SMS_API_KEY = os.environ.get("SMS_API_KEY", "")
    SMS_SENDER_ID = os.environ.get("SMS_SENDER_ID", "SMPOUL")
    SMS_TEMPLATE_ID = os.environ.get("SMS_TEMPLATE_ID", "")

    # Twilio Specific
    TWILIO_ACCOUNT_SID = os.environ.get("TWILIO_ACCOUNT_SID", "")
    TWILIO_AUTH_TOKEN = os.environ.get("TWILIO_AUTH_TOKEN", "")
    TWILIO_PHONE_NUMBER = os.environ.get("TWILIO_PHONE_NUMBER", "")

    # OTP Controls
    OTP_EXPIRY_MINUTES = int(os.environ.get("OTP_EXPIRY_MINUTES", 5))
    OTP_RESEND_COOLDOWN_SECONDS = int(os.environ.get("OTP_RESEND_COOLDOWN_SECONDS", 60))
    OTP_MAX_ATTEMPTS = int(os.environ.get("OTP_MAX_ATTEMPTS", 5))

class TestConfig(Config):
    TESTING = True
    DB_ENGINE = "sqlite"
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
    SMS_PROVIDER = "mock"
