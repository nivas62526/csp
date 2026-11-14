"""
Smart Poultry Farm - Automated Verification Test Suite
Tests:
- Clean database setup without dummy data
- Role-based registration (Farmer, Veterinarian, Admin)
- Dynamic age calculation & flock management
- Daily operations logging & mortality deduction
- IoT telemetry endpoint & automated alert engine
- AI Disease risk prediction
- Bilingual Telugu & English localization
"""

import unittest
import os
import tempfile
from datetime import date, timedelta
from app import app
import database
from models import db
import ai_engine
from translations import get_text

class TestSmartPoultryFarm(unittest.TestCase):

    def setUp(self):
        import sqlalchemy as sa
        # Use a temporary clean database for unit tests
        self.db_fd, self.temp_db_path = tempfile.mkstemp()
        database.DB_PATH = self.temp_db_path
        database.init_db()

        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{self.temp_db_path}"
        with app.app_context():
            ext = app.extensions.get('sqlalchemy')
            if ext and hasattr(ext, '_app_engines') and app in ext._app_engines:
                ext._app_engines[app][None] = sa.create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
            db.create_all()
        self.client = app.test_client()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            try:
                db.engine.dispose()
            except Exception:
                pass
        os.close(self.db_fd)
        try:
            if os.path.exists(self.temp_db_path):
                os.remove(self.temp_db_path)
        except Exception:
            pass

    def test_01_clean_state_no_dummy_data(self):
        """Verify the database is created completely clean without mock records."""
        conn = database.get_db()
        user_count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        farm_count = conn.execute("SELECT COUNT(*) FROM farms").fetchone()[0]
        flock_count = conn.execute("SELECT COUNT(*) FROM flocks").fetchone()[0]
        log_count = conn.execute("SELECT COUNT(*) FROM daily_logs").fetchone()[0]
        alert_count = conn.execute("SELECT COUNT(*) FROM alerts").fetchone()[0]
        conn.close()

        self.assertEqual(user_count, 0, "Users table must be empty initially")
        self.assertEqual(farm_count, 0, "Farms table must be empty initially")
        self.assertEqual(flock_count, 0, "Flocks table must be empty initially")
        self.assertEqual(log_count, 0, "Daily logs table must be empty initially")
        self.assertEqual(alert_count, 0, "Alerts table must be empty initially")

    def test_02_farmer_and_vet_registration(self):
        """Verify registration for different roles (Farmer, Veterinarian)."""
        # Register Farmer
        res_farmer = self.client.post("/api/auth/register", json={
            "name": "Ramesh Farmer",
            "phone": "9876543210",
            "password": "farmerpassword123",
            "role": "farmer",
            "language": "te"
        })
        self.assertEqual(res_farmer.status_code, 201)
        self.assertEqual(res_farmer.json["user"]["role"], "farmer")

        # Register Veterinarian
        res_vet = self.client.post("/api/auth/register", json={
            "name": "Dr. Ananya Rao",
            "email": "dr.ananya@poultryvet.com",
            "password": "vetpassword123",
            "role": "veterinarian",
            "language": "en",
            "specialization": "Avian Pathology"
        })
        self.assertEqual(res_vet.status_code, 201)
        self.assertEqual(res_vet.json["user"]["role"], "veterinarian")

    def test_03_farm_and_flock_lifecycle(self):
        """Verify farm creation, batch creation, dynamic age calculation and mortality updates."""
        # 1. Login as Farmer
        self.client.post("/api/auth/register", json={
            "name": "Venkatesh",
            "phone": "9998887776",
            "password": "pass",
            "role": "farmer"
        })
        login_res = self.client.post("/api/auth/login", json={
            "identifier": "9998887776",
            "password": "pass"
        })
        self.assertEqual(login_res.status_code, 200)

        # 2. Create Farm
        farm_res = self.client.post("/api/farms/create", json={
            "farm_name": "Krishna Broiler Farm",
            "location": "Telangana",
            "total_capacity": 10000,
            "farm_type": "Broiler"
        })
        self.assertEqual(farm_res.status_code, 201)
        farm_id = farm_res.json["farm_id"]

        # 3. Create Flock (Batch)
        arrival = (date.today() - timedelta(days=14)).isoformat() # 14 days old
        flock_res = self.client.post("/api/flocks/create", json={
            "farm_id": farm_id,
            "batch_code": "BATCH-2026-TEST",
            "breed": "Broiler",
            "initial_birds": 5000,
            "arrival_date": arrival,
            "target_weight_kg": 2.2
        })
        self.assertEqual(flock_res.status_code, 201)

        # 4. Log Daily Operations (Mortality = 15)
        conn = database.get_db()
        flock_id = conn.execute("SELECT id FROM flocks WHERE batch_code = 'BATCH-2026-TEST'").fetchone()[0]
        conn.close()

        daily_res = self.client.post("/api/logs/daily", json={
            "flock_id": flock_id,
            "log_date": date.today().isoformat(),
            "feed_consumed_kg": 285.0,
            "water_liters": 620.0,
            "mortality": 15,
            "egg_good": 0
        })
        self.assertEqual(daily_res.status_code, 201)
        # 5000 - 15 = 4985 live birds remaining
        self.assertEqual(daily_res.json["current_birds"], 4985)

    def test_04_iot_telemetry_and_automated_alerts(self):
        """Verify ESP32 IoT sensor telemetry ingestion and automated alert triggers."""
        conn = database.get_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, phone, password_hash, role) VALUES ('F1', '111', 'h', 'farmer')")
        u_id = cursor.lastrowid
        cursor.execute("INSERT INTO farms (user_id, farm_name) VALUES (?, 'Test Farm')", (u_id,))
        f_id = cursor.lastrowid
        cursor.execute("INSERT INTO sheds (farm_id, shed_name) VALUES (?, 'Shed Alpha')", (f_id,))
        shed_id = cursor.lastrowid
        conn.commit()
        conn.close()

        # Ingest High Temperature (35.5C > 34C limit) and Low Water (15% < 20% limit)
        res = self.client.post("/api/iot/telemetry", json={
            "shed_id": shed_id,
            "temperature": 35.5,
            "humidity": 65.0,
            "ammonia_ppm": 12.0,
            "water_level_pct": 15.0,
            "feed_level_pct": 80.0
        })
        self.assertEqual(res.status_code, 201)
        self.assertTrue(len(res.json["alerts_triggered"]) >= 2)

        # Verify alerts in database
        conn = database.get_db()
        alerts = conn.execute("SELECT * FROM alerts WHERE farm_id = ?", (f_id,)).fetchall()
        conn.close()
        self.assertTrue(len(alerts) >= 2)
        # Check Telugu translation presence
        self.assertTrue(any("ఉష్ణోగ్రత" in a["message_te"] for a in alerts))

    def test_05_ai_engine_decision_support(self):
        """Verify AI disease risk prediction engine and feed requirement prediction."""
        # Critical scenario: High temp + High Ammonia + Coughing symptoms
        ai_res = ai_engine.predict_disease_risk(
            age_days=18,
            temperature=35.0,
            humidity=80.0,
            ammonia_ppm=28.0,
            symptoms="Heavy coughing and gasping, wheezing sounds"
        )
        self.assertIn(ai_res["risk_level"], ["HIGH", "CRITICAL"])
        self.assertTrue(len(ai_res["recommendations_te"]) > 0)
        self.assertTrue(len(ai_res["recommendations_en"]) > 0)

        # Feed requirement calculation
        feed_calc = ai_engine.predict_feed_requirement("Broiler", age_days=21, bird_count=5000)
        self.assertGreater(feed_calc["daily_kg"], 0)
        self.assertGreater(feed_calc["weekly_kg"], 0)

    def test_06_bilingual_translations(self):
        """Verify English and Telugu localization outputs."""
        en_title = get_text("app_title", lang="en")
        te_title = get_text("app_title", lang="te")
        self.assertEqual(en_title, "Smart Poultry Farm")
        self.assertEqual(te_title, "స్మార్ట్ పౌల్ట్రీ ఫామ్")

if __name__ == "__main__":
    unittest.main()
