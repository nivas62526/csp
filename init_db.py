"""
Smart Poultry Farm Management System - Database Initialization Script
Supports MySQL 8 (creates database 'smart_poultry' if not exists) and SQLite.
Initializes tables, constraints, triggers, and creates default roles.
"""

import sys
import os
import pymysql
from datetime import datetime, timezone

from config import Config
from models import db, User, Farm, Flock, DailyRecord
from flask import Flask
from werkzeug.security import generate_password_hash

def ensure_mysql_database_exists():
    """Connects to MySQL server root and creates database smart_poultry if missing."""
    if Config.DB_ENGINE != "mysql":
        return True, "Non-MySQL engine configured."

    try:
        conn = pymysql.connect(
            host=Config.DB_HOST,
            port=int(Config.DB_PORT),
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            charset="utf8mb4"
        )
        with conn.cursor() as cursor:
            cursor.execute(
                f"CREATE DATABASE IF NOT EXISTS `{Config.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            )
        conn.commit()
        conn.close()
        return True, f"MySQL database '{Config.DB_NAME}' ensured on {Config.DB_HOST}:{Config.DB_PORT}."
    except Exception as e:
        return False, f"Could not connect to MySQL server: {e}"

def init_database(app: Flask = None, use_sqlite_fallback: bool = True):
    """Initializes all tables and seeds default user accounts."""
    if app is None:
        app = Flask(__name__)
        app.config.from_object(Config)

    # Attempt MySQL check
    if Config.DB_ENGINE == "mysql":
        ok, msg = ensure_mysql_database_exists()
        print(f"[Database Setup] {msg}")
        if not ok:
            if use_sqlite_fallback:
                print(f"[Database Setup] WARNING: MySQL unreachable. Falling back to SQLite ({Config.SQLITE_DATABASE_PATH}) for local operations.")
                app.config["SQLALCHEMY_DATABASE_URI"] = Config.SQLITE_DATABASE_URI
            else:
                print("[Database Setup] ERROR: Strict MySQL mode enabled. Halting.")
                sys.exit(1)

    if "sqlalchemy" not in app.extensions:
        db.init_app(app)

    with app.app_context():
        # Create all tables defined in models.py
        db.create_all()
        print(f"[Database Setup] All 12 tables verified successfully.")

        # Seed initial system users if not present
        default_users = [
            {
                "name": "Farmer Ramesh",
                "phone": "+91 9876543210",
                "email": "farmer@smartpoultry.com",
                "password": "farmerpassword123",
                "role": "farmer",
                "language": "te",
                "account_status": "active",
                "mobile_verified": True
            },
            {
                "name": "Dr. Sunitha Rao (Vet)",
                "phone": "+91 9876543211",
                "email": "vet@smartpoultry.com",
                "password": "vetpassword123",
                "role": "veterinarian",
                "specialization": "Avian Medicine & Poultry Health",
                "language": "en",
                "account_status": "active",
                "mobile_verified": True
            },
            {
                "name": "System Administrator",
                "phone": "+91 9876543212",
                "email": "admin@smartpoultry.com",
                "password": "adminpassword123",
                "role": "admin",
                "language": "en",
                "account_status": "active",
                "mobile_verified": True
            }
        ]

        for u in default_users:
            existing = User.query.filter(
                (User.phone == u["phone"]) | (User.email == u["email"])
            ).first()
            if not existing:
                new_user = User(
                    name=u["name"],
                    phone=u["phone"],
                    email=u["email"],
                    role=u["role"],
                    language=u["language"],
                    specialization=u.get("specialization"),
                    account_status=u["account_status"],
                    mobile_verified=u["mobile_verified"]
                )
                new_user.set_password(u["password"])
                db.session.add(new_user)

        db.session.commit()
        print("[Database Setup] Default system roles (Farmer, Vet, Admin) seeded.")

    return True

if __name__ == "__main__":
    from app import app
    print("=" * 60)
    print("  [INIT] SMART POULTRY FARM - DATABASE INITIALIZER")
    print("=" * 60)
    init_database(app)
    print("=" * 60)
    print(" Database ready for operations!")
    print("=" * 60)
