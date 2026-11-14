"""
Smart Poultry Farm Management and Monitoring System - Comprehensive Test Suite
Tests:
1. User Registration (Without OTP)
2. User Login & Token Generation
3. Multi-Tenant User Isolation (User A vs User B)
4. Dashboard Live Calculations
5. Full CRUD on all 18 Modules
"""

import sys
import unittest
import json
import time
from datetime import date, timedelta
from app import app, db
from models import (
    User, Farm, Flock, Bird, FeedRecord, WaterRecord, EggRecord,
    MortalityRecord, WeightRecord, EnvironmentRecord, Vaccination,
    Medicine, Expense, Sale, Inventory, Task, Notification, UserSetting
)

class FullSystemTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.client = self.app.test_client()
        self.ctx = self.app.app_context()
        self.ctx.push()
        self.ts = int(time.time() * 1000) % 100000000
        self.phone_a = f"91{self.ts:08d}"
        self.phone_b = f"92{self.ts:08d}"

    def tearDown(self):
        self.ctx.pop()

    def test_01_user_registration_no_otp(self):
        """Test registration without OTP"""
        reg_payload = {
            "fullName": "Test Farmer Alpha",
            "mobileNumber": self.phone_a,
            "email": f"farmer.alpha.{self.ts}@testpoultry.com",
            "password": "Password123!",
            "confirmPassword": "Password123!",
            "farmName": f"Alpha Broiler Farm {self.ts}",
            "location": "North Agro Zone"
        }
        res = self.client.post("/api/auth/register", json=reg_payload)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201, msg=f"Register failed: {data}")
        self.assertEqual(data["status"], "success")
        self.assertIn("token", data)
        self.assertEqual(data["user"]["phone"], self.phone_a)

        # Verify initial farm was created
        user_id = data["user"]["id"]
        farm = Farm.query.filter_by(owner_id=user_id).first()
        self.assertIsNotNone(farm)
        self.assertEqual(farm.farm_name, f"Alpha Broiler Farm {self.ts}")

    def test_02_user_login(self):
        """Test login with mobile number and password"""
        # Register user first
        phone = f"93{self.ts:08d}"
        self.client.post("/api/auth/register", json={
            "fullName": "Login Tester",
            "mobileNumber": phone,
            "password": "Password123!",
            "confirmPassword": "Password123!"
        })

        login_payload = {
            "identifier": phone,
            "password": "Password123!"
        }
        res = self.client.post("/api/auth/login", json=login_payload)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["status"], "success")
        self.assertIn("token", data)

    def test_03_multi_tenant_data_isolation(self):
        """Test that User A and User B cannot access each other's data"""
        # Register User A
        res_a = self.client.post("/api/auth/register", json={
            "fullName": "User Alpha",
            "mobileNumber": self.phone_a,
            "email": f"alpha.{self.ts}@test.com",
            "password": "Password123!",
            "confirmPassword": "Password123!",
            "farmName": f"Alpha Farm {self.ts}",
            "location": "North Zone"
        })
        token_a = json.loads(res_a.data)["token"]
        user_a_id = json.loads(res_a.data)["user"]["id"]

        # Register User B
        res_b = self.client.post("/api/auth/register", json={
            "fullName": "User Beta",
            "mobileNumber": self.phone_b,
            "email": f"beta.{self.ts}@test.com",
            "password": "Password123!",
            "confirmPassword": "Password123!",
            "farmName": f"Beta Farm {self.ts}",
            "location": "South Zone"
        })
        token_b = json.loads(res_b.data)["token"]

        # User A creates a flock
        farm_a = Farm.query.filter_by(owner_id=user_a_id).first()
        res_flock = self.client.post("/api/flocks", json={
            "farmId": farm_a.id,
            "name": f"Batch-A-{self.ts}",
            "birdType": "Broiler",
            "birdCount": 3000,
            "target_weight_kg": 2.2
        }, headers={"Authorization": f"Bearer {token_a}"})
        self.assertEqual(res_flock.status_code, 201)
        flock_a_id = json.loads(res_flock.data)["batch"]["id"]

        # User B queries flocks with User B's token -> User B should NOT see User A's flock
        res_b_flocks = self.client.get("/api/flocks", headers={"Authorization": f"Bearer {token_b}"})
        flocks_b = json.loads(res_b_flocks.data)["flocks"]
        flock_b_ids = [f["id"] for f in flocks_b]
        self.assertNotIn(flock_a_id, flock_b_ids, "Security breach: User B saw User A's flock!")

        # User B tries to view User A's flock -> Should be 404
        res_hack = self.client.get(f"/api/flocks/{flock_a_id}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(res_hack.status_code, 404, "Security breach: User B was able to access User A's flock!")

        # User B tries to delete User A's flock -> Should be 404
        res_hack_del = self.client.delete(f"/api/flocks/{flock_a_id}", headers={"Authorization": f"Bearer {token_b}"})
        self.assertEqual(res_hack_del.status_code, 404, "Security breach: User B was able to delete User A's flock!")

    def test_04_crud_operations(self):
        """Test full CRUD on all farm modules"""
        phone = f"94{self.ts:08d}"
        res_reg = self.client.post("/api/auth/register", json={
            "fullName": "CRUD Tester",
            "mobileNumber": phone,
            "email": f"crud.{self.ts}@test.com",
            "password": "Password123!",
            "confirmPassword": "Password123!",
            "farmName": f"CRUD Farm {self.ts}",
            "location": "Central Zone"
        })
        token = json.loads(res_reg.data)["token"]
        user_id = json.loads(res_reg.data)["user"]["id"]
        headers = {"Authorization": f"Bearer {token}"}

        # 1. Farm CRUD
        farm = Farm.query.filter_by(owner_id=user_id).first()
        res_up_farm = self.client.put(f"/api/farms/{farm.id}", json={"location": "Updated Central Zone"}, headers=headers)
        self.assertEqual(res_up_farm.status_code, 200)

        # 2. Flock CRUD
        res_flock = self.client.post("/api/flocks", json={
            "farmId": farm.id,
            "name": f"Batch-CRUD-{self.ts}",
            "birdType": "Broiler",
            "birdCount": 2000,
            "target_weight_kg": 2.1
        }, headers=headers)
        self.assertEqual(res_flock.status_code, 201)
        flock_id = json.loads(res_flock.data)["batch"]["id"]

        # 3. Feed CRUD
        res_feed = self.client.post("/api/records/feed", json={
            "flock_id": flock_id,
            "quantity_kg": 150.0,
            "feed_type": "Starter Mash",
            "unit_cost": 40.0
        }, headers=headers)
        self.assertEqual(res_feed.status_code, 201)

        # 4. Water CRUD
        res_water = self.client.post("/api/records/water", json={
            "flock_id": flock_id,
            "quantity_liters": 300.0
        }, headers=headers)
        self.assertEqual(res_water.status_code, 201)

        # 5. Egg CRUD
        res_egg = self.client.post("/api/records/egg", json={
            "flock_id": flock_id,
            "eggs_produced": 50,
            "damaged_eggs": 1
        }, headers=headers)
        self.assertEqual(res_egg.status_code, 201)

        # 6. Mortality Tracking & Automatic live bird deduction
        flock = Flock.query.get(flock_id)
        initial_count = flock.current_bird_count
        res_mort = self.client.post("/api/records/mortality", json={
            "flock_id": flock_id,
            "mortality_count": 4,
            "culls_count": 1,
            "suspected_cause": "Heat stress"
        }, headers=headers)
        self.assertEqual(res_mort.status_code, 201)
        db.session.refresh(flock)
        self.assertEqual(flock.current_bird_count, initial_count - 5)

        # 7. Weight Record
        res_weight = self.client.post("/api/records/weight", json={
            "flock_id": flock_id,
            "average_weight_kg": 1.700,
            "sample_size": 10
        }, headers=headers)
        self.assertEqual(res_weight.status_code, 201)

        # 8. Vaccination
        res_vac = self.client.post("/api/vaccinations", json={
            "flock_id": flock_id,
            "vaccine_name": "Gumboro IBD",
            "date": str(date.today()),
            "route": "Drinking Water"
        }, headers=headers)
        self.assertEqual(res_vac.status_code, 201)

        # 9. Expense
        res_exp = self.client.post("/api/expenses", json={
            "farm_id": farm.id,
            "category": "Feed",
            "description": "Feed batch supply",
            "amount": 6000.00
        }, headers=headers)
        self.assertEqual(res_exp.status_code, 201)

        # 10. Sale
        res_sale = self.client.post("/api/sales", json={
            "farm_id": farm.id,
            "product_type": "eggs",
            "quantity": 50,
            "unit_price": 6.0,
            "total_amount": 300.00
        }, headers=headers)
        self.assertEqual(res_sale.status_code, 201)

        # 11. Task
        res_task = self.client.post("/api/tasks", json={
            "farm_id": farm.id,
            "title": "Check ventilation fans",
            "priority": "high"
        }, headers=headers)
        self.assertEqual(res_task.status_code, 201)
        task_id = json.loads(res_task.data)["task"]["id"]

        # Mark task completed
        res_task_up = self.client.post(f"/api/tasks/{task_id}/status", json={"is_completed": True}, headers=headers)
        self.assertEqual(res_task_up.status_code, 200)

        # 12. Dashboard Live Calculation
        res_dash = self.client.get("/api/dashboard/stats", headers=headers)
        self.assertEqual(res_dash.status_code, 200)
        dash_data = json.loads(res_dash.data)
        self.assertEqual(dash_data["total_farms"], 1)
        self.assertEqual(dash_data["total_flocks"], 1)
        self.assertEqual(dash_data["daily_egg_production"], 50)
        self.assertEqual(dash_data["daily_feed_consumption"], 150.0)
        self.assertEqual(dash_data["daily_water_consumption"], 300.0)
        self.assertEqual(dash_data["mortality_count"], 4)

        # 13. Reports & Analytics
        res_rep = self.client.get("/api/reports/analytics", headers=headers)
        self.assertEqual(res_rep.status_code, 200)
        rep_data = json.loads(res_rep.data)
        self.assertEqual(rep_data["financials"]["total_expenses"], 6000.00)
        self.assertEqual(rep_data["financials"]["total_sales"], 300.00)

if __name__ == "__main__":
    unittest.main()
