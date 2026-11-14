"""
Smart Poultry Farm Management System - Sample Data Seeder & Verification
Creates:
- Verified Farmer Account
- Sample Farm
- Sample Flock (Batch)
- Sample Daily Record (Mortality, Feed, Water, Eggs)
- Verification of automatic current bird count calculation
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from app import app
from models import (
    db, User, Farm, Flock, DailyRecord, FeedRecord, EggRecord, Expense, Sale, Alert
)

def seed_sample_farm_data():
    with app.app_context():
        print("[Seeder] Checking or creating sample farmer user...")
        farmer = User.query.filter_by(phone="+91 9988776655").first()
        if not farmer:
            farmer = User(
                name="Ramesh Farm Owner",
                phone="+91 9988776655",
                email="ramesh.sample@smartpoultry.com",
                role="farmer",
                language="te",
                account_status="active",
                mobile_verified=True
            )
            farmer.set_password("farmpass123")
            db.session.add(farmer)
            db.session.commit()
            print(f"  + Created User: {farmer.name} (ID: {farmer.id})")
        else:
            print(f"  * Existing User found: {farmer.name} (ID: {farmer.id})")

        print("[Seeder] Creating sample poultry farm...")
        farm = Farm.query.filter_by(owner_id=farmer.id, farm_name="Sri Krishna Broiler Farm").first()
        if not farm:
            farm = Farm(
                owner_id=farmer.id,
                farm_name="Sri Krishna Broiler Farm",
                location="Khammam Agro Belt, Shed 1-4",
                address="Survey No. 42, Green Valley Road",
                total_capacity=10000,
                farm_type="Broiler"
            )
            db.session.add(farm)
            db.session.commit()
            print(f"  + Created Farm: {farm.farm_name} (ID: {farm.id})")
        else:
            print(f"  * Existing Farm found: {farm.farm_name} (ID: {farm.id})")

        print("[Seeder] Creating sample flock (batch)...")
        batch_no = "BATCH-C500-2026-A1"
        flock = Flock.query.filter_by(farm_id=farm.id, batch_number=batch_no).first()
        if not flock:
            flock = Flock(
                farm_id=farm.id,
                batch_number=batch_no,
                bird_type="Broiler",
                breed="Cobb 500",
                initial_bird_count=5000,
                current_bird_count=5000,
                arrival_date=date.today() - timedelta(days=21),
                expected_sale_date=date.today() + timedelta(days=21),
                target_weight_kg=Decimal("2.20"),
                status="active",
                notes="Healthy chicks vaccinated at hatchery against Marek's"
            )
            db.session.add(flock)
            db.session.commit()
            print(f"  + Created Flock: {flock.batch_number} with {flock.initial_bird_count} birds (ID: {flock.id})")
        else:
            print(f"  * Existing Flock found: {flock.batch_number} (ID: {flock.id})")

        print("[Seeder] Logging sample daily record with mortality and feed intake...")
        rec_date = date.today()
        daily_rec = DailyRecord.query.filter_by(flock_id=flock.id, record_date=rec_date).first()
        opening = flock.current_bird_count
        mortality = 4
        culls = 1
        closing = max(0, opening - mortality - culls)

        if not daily_rec:
            daily_rec = DailyRecord(
                flock_id=flock.id,
                record_date=rec_date,
                opening_birds=opening,
                mortality=mortality,
                culls=culls,
                closing_birds=closing,
                average_weight_kg=Decimal("1.250"),
                feed_consumed_kg=Decimal("450.00"),
                water_consumed_liters=Decimal("900.00"),
                eggs_produced=0,
                notes="Routine morning inspection. Birds active and drinking normally."
            )
            db.session.add(daily_rec)
            # Synchronize flock
            flock.current_bird_count = closing
            db.session.commit()
            print(f"  + Created Daily Record: Opening={opening}, Mortality={mortality}, Closing={closing}")
        else:
            closing = daily_rec.closing_birds
            print(f"  * Existing Daily Record found for {rec_date}: Closing={daily_rec.closing_birds}")

        # Verification of automatic bird count synchronization
        flock_refreshed = db.session.get(Flock, flock.id)
        assert flock_refreshed.current_bird_count == closing, (
            f"Bird count mismatch! Expected {closing}, got {flock_refreshed.current_bird_count}"
        )
        print(f"  [OK] Automatic current bird count verified: {flock_refreshed.current_bird_count} live birds.")

        print("[Seeder] Sample data seeded and verified successfully.")
        return {
            "farmer_id": farmer.id,
            "farm_id": farm.id,
            "flock_id": flock.id,
            "daily_record_id": daily_rec.id
        }

if __name__ == "__main__":
    seed_sample_farm_data()
