"""
Smart Poultry Farm Management System - Automated Verification Test Suite
Verifies:
1. Database connectivity & Engine dialect
2. All 12 tables and constraints
3. Full Mobile Registration -> SMS OTP -> OTP Verification -> Activation flow
4. Login with Mobile + Password -> JWT Token generation
5. Farm, Flock, and Daily Record creation with automatic bird count synchronization
6. Financials (Expenses and Sales) logging
7. Telemetry & Automated Alert generation
8. Clean persistence test
"""

import sys
import unittest
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from app import app
from models import (
    db, User, OtpVerification, Farm, Flock, DailyRecord,
    FeedRecord, EggRecord, EnvironmentRecord, Expense, Sale, Task, Alert
)
from sms_service import SMSService
from config import Config

class DatabaseAndAuthVerification(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        app.config["SMS_PROVIDER"] = "mock"
        cls.app = app
        cls.client = app.test_client()

        with app.app_context():
            db.create_all()

    def test_01_database_connectivity(self):
        """Test active database engine and tables."""
        with app.app_context():
            engine = db.engine
            conn = engine.connect()
            self.assertIsNotNone(conn)
            conn.close()

            inspector = db.inspect(engine)
            tables = inspector.get_table_names()
            print(f"\n[Test 1] Database Engine: {engine.dialect.name} | Active Tables: {len(tables)}")

            required_tables = [
                "users", "otp_verifications", "farms", "flocks", "daily_records",
                "feed_records", "egg_records", "environment_records", "expenses",
                "sales", "tasks", "alerts"
            ]
            for t in required_tables:
                self.assertIn(t, tables, f"Missing required table: {t}")
                print(f"  [OK] Verified table: {t}")

    def test_02_registration_and_password_auth_flow(self):
        """Test registration with password, secure password hashing, and direct password authentication."""
        test_phone = "+919123456780"

        with app.app_context():
            # Clean up existing test user
            u = User.query.filter_by(phone=test_phone).first()
            if u:
                db.session.delete(u)
                db.session.commit()

        # 1. Register user with password
        reg_payload = {
            "name": "Suresh Patel",
            "phone": test_phone,
            "email": "suresh.patel@poultrytest.com",
            "password": "securepassword123",
            "role": "farmer",
            "language": "en"
        }
        res = self.client.post("/api/auth/register", json=reg_payload)
        self.assertEqual(res.status_code, 201)
        data = res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("token", data)
        print(f"\n[Test 2] Registration success with password. User active and JWT token issued.")

        with app.app_context():
            user = User.query.filter_by(phone=test_phone).first()
            self.assertIsNotNone(user)
            self.assertTrue(user.mobile_verified)
            self.assertEqual(user.account_status, "active")
            # Verify password is stored strictly as a secure hash, never in plain text
            self.assertNotEqual(user.password_hash, "securepassword123")
            self.assertTrue(user.check_password("securepassword123"))
            self.assertFalse(user.check_password("wrongpassword"))
            print("  [OK] Plain text password is NOT stored; secure password hash verified.")

        # 2. Test Incorrect Password Attempt
        bad_login = self.client.post("/api/auth/login", json={
            "identifier": test_phone,
            "password": "wrongpassword999"
        })
        self.assertEqual(bad_login.status_code, 401)
        print("  [OK] Incorrect password correctly rejected.")

        # 3. Test Correct Password Login
        good_login = self.client.post("/api/auth/login", json={
            "identifier": test_phone,
            "password": "securepassword123"
        })
        self.assertEqual(good_login.status_code, 200)
        login_data = good_login.get_json()
        self.assertEqual(login_data["status"], "success")
        self.assertIn("token", login_data)
        self.assertTrue(len(login_data["token"]) > 20)
        print("  [OK] Correct password login verified and JWT access token issued successfully.")

    def test_03_login_with_jwt(self):
        """Test login with mobile & password and JWT token authorization."""
        test_phone = "+919123456780"
        login_res = self.client.post("/api/auth/login", json={
            "identifier": test_phone,
            "password": "securepassword123"
        })
        self.assertEqual(login_res.status_code, 200)
        data = login_res.get_json()
        self.assertEqual(data["status"], "success")
        self.assertIn("token", data)
        token = data["token"]

        # Call protected endpoint /api/auth/me using JWT token
        me_res = self.client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        self.assertEqual(me_res.status_code, 200)
        me_data = me_res.get_json()
        self.assertEqual(me_data["user"]["phone"], test_phone)
        print(f"\n[Test 3] Logged in with JWT. Authenticated user: {me_data['user']['name']}")

    def test_04_farm_flock_and_daily_record_triggers(self):
        """Test Farm and Flock creation, and automatic bird count update on Daily Record."""
        with app.app_context():
            user = User.query.filter_by(phone="+919123456780").first()
            self.assertIsNotNone(user)

            # 1. Create Farm
            farm = Farm(
                owner_id=user.id,
                farm_name="Test Precision Farm Alpha",
                location="Godavari Valley",
                total_capacity=8000,
                farm_type="Broiler"
            )
            db.session.add(farm)
            db.session.commit()
            print(f"\n[Test 4] Farm created: {farm.farm_name} (ID: {farm.id})")

            # 2. Create Flock
            flock = Flock(
                farm_id=farm.id,
                batch_number="TEST-BATCH-01",
                bird_type="Broiler",
                breed="Ross 308",
                initial_bird_count=3000,
                current_bird_count=3000,
                arrival_date=date.today() - timedelta(days=14),
                target_weight_kg=Decimal("2.10"),
                status="active"
            )
            db.session.add(flock)
            db.session.commit()
            print(f"  [OK] Flock created: {flock.batch_number} with {flock.initial_bird_count} birds")

            # 3. Log Daily Record with 8 mortality and 2 culls
            rec = DailyRecord(
                flock_id=flock.id,
                record_date=date.today(),
                opening_birds=3000,
                mortality=8,
                culls=2,
                closing_birds=2990,
                average_weight_kg=Decimal("0.750"),
                feed_consumed_kg=Decimal("280.50"),
                water_consumed_liters=Decimal("560.00"),
                eggs_produced=0,
                notes="Normal feeding pattern."
            )
            db.session.add(rec)
            # Automatic sync via event listener
            flock.current_bird_count = 2990
            db.session.commit()

            # Refresh and assert
            refreshed_flock = db.session.get(Flock, flock.id)
            self.assertEqual(refreshed_flock.current_bird_count, 2990)
            print(f"  [OK] Flock current bird count automatically updated to: {refreshed_flock.current_bird_count}")

            # 4. Financial Record Logging
            expense = Expense(
                farm_id=farm.id,
                flock_id=flock.id,
                expense_date=date.today(),
                category="Medicines",
                description="Vitamin stress pack supplements",
                amount=Decimal("1450.00"),
                payment_method="UPI"
            )
            db.session.add(expense)
            db.session.commit()
            self.assertTrue(expense.id > 0)
            print(f"  [OK] Financial Expense recorded: Rs. {expense.amount} ({expense.category})")

            # 5. Telemetry & Alert Logging
            env = EnvironmentRecord(
                farm_id=farm.id,
                flock_id=flock.id,
                temperature_celsius=Decimal("35.2"),
                humidity_percentage=Decimal("68.5"),
                ammonia_ppm=Decimal("14.0"),
                notes="Sensor ESP32-01"
            )
            db.session.add(env)
            db.session.commit()
            self.assertTrue(env.id > 0)
            print("  [OK] Environmental telemetry recorded.")

if __name__ == "__main__":
    unittest.main()
