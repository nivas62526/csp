"""
Smart Poultry Farm Management and Monitoring System - SQLAlchemy Models
Complete database models for MySQL 8 & SQLite compatibility.
All 18 core relational tables with foreign keys, indexes, timestamps, constraints, and audit trails.
"""

from datetime import datetime, date, timezone
from decimal import Decimal
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint, Index
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

# ------------------------------------------------------------------------------
# 1. User Model (Table: users)
# ------------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(50), unique=True, nullable=False, index=True) # Mobile Number
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="farmer") # 'farmer', 'veterinarian', 'admin'
    mobile_verified = db.Column(db.Boolean, nullable=False, default=True)
    account_status = db.Column(db.String(20), nullable=False, default="active") # 'active', 'pending', 'suspended'
    language = db.Column(db.String(10), nullable=False, default="en")
    specialization = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    # Relationships
    farms = db.relationship("Farm", backref="owner", cascade="all, delete-orphan", lazy="dynamic")
    notifications = db.relationship("Notification", backref="user", cascade="all, delete-orphan", lazy="dynamic")
    settings = db.relationship("UserSetting", backref="user", uselist=False, cascade="all, delete-orphan")
    otps = db.relationship("OtpVerification", backref="user", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def mobile_number(self):
        return self.phone

    @mobile_number.setter
    def mobile_number(self, val):
        self.phone = val

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "fullName": self.name,
            "email": self.email,
            "phone": self.phone,
            "mobile_number": self.phone,
            "role": self.role,
            "mobile_verified": self.mobile_verified,
            "account_status": self.account_status,
            "language": self.language,
            "specialization": self.specialization,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ------------------------------------------------------------------------------
# 2. Farm Model (Table: farms)
# ------------------------------------------------------------------------------
class Farm(db.Model):
    __tablename__ = "farms"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(255), nullable=True)
    address = db.Column(db.Text, nullable=True)
    total_capacity = db.Column(db.Integer, nullable=False, default=5000)
    farm_type = db.Column(db.String(50), nullable=False, default="Broiler") # Broiler, Layer, Breeder, Country/Desi
    farm_size = db.Column(db.String(100), nullable=True, default="2 Acres")
    established_date = db.Column(db.Date, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint("total_capacity >= 0", name="chk_farms_capacity"),
    )

    # Relationships
    flocks = db.relationship("Flock", backref="farm", cascade="all, delete-orphan", lazy="dynamic")
    environment_records = db.relationship("EnvironmentRecord", backref="farm", cascade="all, delete-orphan", lazy="dynamic")
    expenses = db.relationship("Expense", backref="farm", cascade="all, delete-orphan", lazy="dynamic")
    sales = db.relationship("Sale", backref="farm", cascade="all, delete-orphan", lazy="dynamic")
    inventory = db.relationship("Inventory", backref="farm", cascade="all, delete-orphan", lazy="dynamic")
    tasks = db.relationship("Task", backref="farm", cascade="all, delete-orphan", lazy="dynamic")
    alerts = db.relationship("Alert", backref="farm", cascade="all, delete-orphan", lazy="dynamic")

    def to_dict(self):
        # Calculate current active bird population across all active flocks
        active_flocks = self.flocks.filter_by(status="active").all()
        current_birds = sum(f.current_bird_count for f in active_flocks)
        return {
            "id": self.id,
            "owner_id": self.owner_id,
            "name": self.farm_name,
            "farm_name": self.farm_name,
            "location": self.location or "Agro Zone",
            "address": self.address,
            "capacity": self.total_capacity,
            "total_capacity": self.total_capacity,
            "birdType": self.farm_type,
            "farm_type": self.farm_type,
            "farmSize": self.farm_size or "2 Acres",
            "establishedDate": self.established_date.isoformat() if self.established_date else None,
            "currentBirds": current_birds,
            "activeFlocksCount": len(active_flocks),
            "healthScore": 88,
            "riskLevel": "Low",
            "mortalityRate": 0.8,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ------------------------------------------------------------------------------
# 3. Flock / Batch Model (Table: flocks)
# ------------------------------------------------------------------------------
class Flock(db.Model):
    __tablename__ = "flocks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    batch_number = db.Column(db.String(100), nullable=False) # e.g. B-101, BATCH-2026-01
    bird_type = db.Column(db.String(100), nullable=False, default="Broiler")
    breed = db.Column(db.String(100), nullable=False, default="Cobb 500")
    initial_bird_count = db.Column(db.Integer, nullable=False, default=1000)
    current_bird_count = db.Column(db.Integer, nullable=False, default=1000)
    arrival_date = db.Column(db.Date, nullable=False, default=date.today)
    expected_sale_date = db.Column(db.Date, nullable=True)
    target_weight_kg = db.Column(db.Numeric(6, 2), nullable=False, default=Decimal("2.00"))
    status = db.Column(db.String(20), nullable=False, default="active") # 'active', 'sold', 'closed'
    health_status = db.Column(db.String(50), nullable=False, default="Good")
    risk_level = db.Column(db.String(20), nullable=False, default="Low") # 'Low', 'Medium', 'High'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint("initial_bird_count >= 0", name="chk_initial_bird_count"),
        CheckConstraint("current_bird_count >= 0", name="chk_current_bird_count"),
        UniqueConstraint("farm_id", "batch_number", name="uq_farm_batch"),
        Index("idx_flocks_farm_status", "farm_id", "status")
    )

    # Relationships
    birds = db.relationship("Bird", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    daily_records = db.relationship("DailyRecord", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    feed_records = db.relationship("FeedRecord", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    water_records = db.relationship("WaterRecord", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    egg_records = db.relationship("EggRecord", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    mortality_records = db.relationship("MortalityRecord", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    weight_records = db.relationship("WeightRecord", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    vaccinations = db.relationship("Vaccination", backref="flock", cascade="all, delete-orphan", lazy="dynamic")
    medicines = db.relationship("Medicine", backref="flock", cascade="all, delete-orphan", lazy="dynamic")

    @property
    def age_days(self) -> int:
        if not self.arrival_date:
            return 0
        diff = date.today() - self.arrival_date
        return max(0, diff.days)

    def to_dict(self):
        # Fetch latest daily stats if available
        latest_daily = self.daily_records.order_by(DailyRecord.record_date.desc()).first()
        daily_feed = float(latest_daily.feed_consumed_kg) if latest_daily and latest_daily.feed_consumed_kg else 0.0
        daily_water = float(latest_daily.water_consumed_liters) if latest_daily and latest_daily.water_consumed_liters else 0.0
        mortality_cnt = int(latest_daily.mortality) if latest_daily and latest_daily.mortality else 0
        avg_weight = float(latest_daily.average_weight_kg) if latest_daily and latest_daily.average_weight_kg else float(self.target_weight_kg or 2.0)

        return {
            "id": self.id,
            "farmId": self.farm_id,
            "farm_id": self.farm_id,
            "name": f"Batch {self.batch_number}",
            "batch_number": self.batch_number,
            "birdType": f"{self.bird_type} ({self.breed})" if self.breed else self.bird_type,
            "breed": self.breed,
            "birdCount": self.current_bird_count,
            "initial_bird_count": self.initial_bird_count,
            "current_bird_count": self.current_bird_count,
            "ageDays": self.age_days,
            "age_days": self.age_days,
            "startDate": self.arrival_date.isoformat() if self.arrival_date else None,
            "arrival_date": self.arrival_date.isoformat() if self.arrival_date else None,
            "expected_sale_date": self.expected_sale_date.isoformat() if self.expected_sale_date else None,
            "target_weight_kg": float(self.target_weight_kg),
            "status": self.status,
            "healthStatus": self.health_status,
            "health_status": self.health_status,
            "riskLevel": self.risk_level,
            "risk_level": self.risk_level,
            "avgWeightKg": avg_weight,
            "dailyFeedKg": daily_feed,
            "dailyWaterL": daily_water,
            "mortalityCount": mortality_cnt,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ------------------------------------------------------------------------------
# 4. Bird Model (Table: birds)
# ------------------------------------------------------------------------------
class Bird(db.Model):
    __tablename__ = "birds"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    tag_number = db.Column(db.String(50), nullable=True) # Tag / Band ID
    shed_name = db.Column(db.String(100), nullable=False, default="Shed 1")
    cage_or_pen = db.Column(db.String(100), nullable=True)
    current_weight_kg = db.Column(db.Numeric(6, 3), nullable=False, default=Decimal("0.000"))
    health_status = db.Column(db.String(50), nullable=False, default="Healthy")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "tag_number": self.tag_number or f"TAG-{self.id}",
            "shed_name": self.shed_name,
            "cage_or_pen": self.cage_or_pen,
            "current_weight_kg": float(self.current_weight_kg),
            "health_status": self.health_status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ------------------------------------------------------------------------------
# 5. Feed Record Model (Table: feed_records)
# ------------------------------------------------------------------------------
class FeedRecord(db.Model):
    __tablename__ = "feed_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    record_date = db.Column(db.Date, nullable=False, default=date.today)
    feed_type = db.Column(db.String(100), nullable=False, default="Broiler Starter")
    quantity_kg = db.Column(db.Numeric(8, 2), nullable=False)
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total_cost = db.Column(db.Numeric(12, 2), nullable=False, default=Decimal("0.00"))
    supplier = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("quantity_kg >= 0", name="chk_feed_quantity"),
        CheckConstraint("total_cost >= 0", name="chk_feed_cost"),
        Index("idx_feed_flock_date", "flock_id", "record_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "farm_id": self.farm_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "feed_type": self.feed_type,
            "quantity_kg": float(self.quantity_kg),
            "unit_cost": float(self.unit_cost),
            "total_cost": float(self.total_cost),
            "supplier": self.supplier,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 6. Water Record Model (Table: water_records)
# ------------------------------------------------------------------------------
class WaterRecord(db.Model):
    __tablename__ = "water_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    record_date = db.Column(db.Date, nullable=False, default=date.today)
    quantity_liters = db.Column(db.Numeric(8, 2), nullable=False)
    water_source = db.Column(db.String(100), nullable=True, default="Borewell")
    temperature_celsius = db.Column(db.Numeric(5, 2), nullable=True)
    ph_level = db.Column(db.Numeric(4, 2), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("quantity_liters >= 0", name="chk_water_quantity"),
        Index("idx_water_flock_date", "flock_id", "record_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "farm_id": self.farm_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "quantity_liters": float(self.quantity_liters),
            "water_source": self.water_source,
            "temperature_celsius": float(self.temperature_celsius) if self.temperature_celsius is not None else None,
            "ph_level": float(self.ph_level) if self.ph_level is not None else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 7. Egg Production Record Model (Table: egg_records)
# ------------------------------------------------------------------------------
class EggRecord(db.Model):
    __tablename__ = "egg_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    record_date = db.Column(db.Date, nullable=False, default=date.today)
    eggs_produced = db.Column(db.Integer, nullable=False, default=0)
    eggs_sold = db.Column(db.Integer, nullable=False, default=0)
    damaged_eggs = db.Column(db.Integer, nullable=False, default=0)
    selling_price_per_egg = db.Column(db.Numeric(8, 2), nullable=False, default=Decimal("0.00"))
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("eggs_produced >= 0", name="chk_egg_produced"),
        CheckConstraint("eggs_sold >= 0", name="chk_egg_sold"),
        CheckConstraint("damaged_eggs >= 0", name="chk_egg_damaged"),
        Index("idx_egg_flock_date", "flock_id", "record_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "farm_id": self.farm_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "eggs_produced": self.eggs_produced,
            "eggs_collected": self.eggs_produced,
            "eggs_sold": self.eggs_sold,
            "damaged_eggs": self.damaged_eggs,
            "selling_price_per_egg": float(self.selling_price_per_egg),
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 8. Mortality Record Model (Table: mortality_records)
# ------------------------------------------------------------------------------
class MortalityRecord(db.Model):
    __tablename__ = "mortality_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    record_date = db.Column(db.Date, nullable=False, default=date.today)
    mortality_count = db.Column(db.Integer, nullable=False, default=1)
    culls_count = db.Column(db.Integer, nullable=False, default=0)
    suspected_cause = db.Column(db.String(255), nullable=True, default="Natural / Unknown")
    symptoms = db.Column(db.Text, nullable=True)
    disposal_method = db.Column(db.String(100), nullable=True, default="Composting")
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("mortality_count >= 0", name="chk_mortality_cnt"),
        CheckConstraint("culls_count >= 0", name="chk_culls_cnt"),
        Index("idx_mortality_flock_date", "flock_id", "record_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "farm_id": self.farm_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "mortality_count": self.mortality_count,
            "culls_count": self.culls_count,
            "suspected_cause": self.suspected_cause,
            "symptoms": self.symptoms,
            "disposal_method": self.disposal_method,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 9. Weight Record Model (Table: weight_records)
# ------------------------------------------------------------------------------
class WeightRecord(db.Model):
    __tablename__ = "weight_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    record_date = db.Column(db.Date, nullable=False, default=date.today)
    sample_size = db.Column(db.Integer, nullable=False, default=10)
    average_weight_kg = db.Column(db.Numeric(6, 3), nullable=False)
    target_weight_kg = db.Column(db.Numeric(6, 3), nullable=False, default=Decimal("2.000"))
    uniformity_percentage = db.Column(db.Numeric(5, 2), nullable=True, default=Decimal("85.00"))
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("sample_size > 0", name="chk_sample_size"),
        CheckConstraint("average_weight_kg >= 0", name="chk_avg_weight"),
        Index("idx_weight_flock_date", "flock_id", "record_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "farm_id": self.farm_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "sample_size": self.sample_size,
            "average_weight_kg": float(self.average_weight_kg),
            "target_weight_kg": float(self.target_weight_kg),
            "uniformity_percentage": float(self.uniformity_percentage) if self.uniformity_percentage else None,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 10. Environment Record Model (Table: environment_records)
# ------------------------------------------------------------------------------
class EnvironmentRecord(db.Model):
    __tablename__ = "environment_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="SET NULL"), nullable=True, index=True)
    recorded_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    temperature_celsius = db.Column(db.Numeric(5, 2), nullable=False)
    humidity_percentage = db.Column(db.Numeric(5, 2), nullable=False)
    ammonia_ppm = db.Column(db.Numeric(5, 2), nullable=False, default=Decimal("0.00"))
    water_level_pct = db.Column(db.Numeric(5, 2), nullable=True, default=Decimal("100.00"))
    feed_level_pct = db.Column(db.Numeric(5, 2), nullable=True, default=Decimal("100.00"))
    source = db.Column(db.String(50), nullable=False, default="IoT_Sensor")
    notes = db.Column(db.Text, nullable=True)

    __table_args__ = (
        CheckConstraint("humidity_percentage >= 0 AND humidity_percentage <= 100", name="chk_env_humidity"),
        CheckConstraint("ammonia_ppm >= 0", name="chk_env_ammonia"),
        Index("idx_env_farm_time", "farm_id", "recorded_at")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "flock_id": self.flock_id,
            "recorded_at": self.recorded_at.isoformat() if self.recorded_at else None,
            "temperature_celsius": float(self.temperature_celsius),
            "temperature": float(self.temperature_celsius),
            "humidity_percentage": float(self.humidity_percentage),
            "humidity": float(self.humidity_percentage),
            "ammonia_ppm": float(self.ammonia_ppm),
            "ammonia": float(self.ammonia_ppm),
            "water_level_pct": float(self.water_level_pct) if self.water_level_pct is not None else 100.0,
            "feed_level_pct": float(self.feed_level_pct) if self.feed_level_pct is not None else 100.0,
            "source": self.source,
            "notes": self.notes
        }


# ------------------------------------------------------------------------------
# 11. Vaccination Schedule Model (Table: vaccinations)
# ------------------------------------------------------------------------------
class Vaccination(db.Model):
    __tablename__ = "vaccinations"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    vaccine_name = db.Column(db.String(150), nullable=False) # e.g. Newcastle (LaSota), Gumboro (IBD), Marek's
    target_disease = db.Column(db.String(150), nullable=True)
    route = db.Column(db.String(100), nullable=False, default="Drinking Water") # Eye Drop, Drinking Water, Injection, Spray
    scheduled_date = db.Column(db.Date, nullable=False)
    administered_date = db.Column(db.Date, nullable=True)
    status = db.Column(db.String(50), nullable=False, default="scheduled") # 'scheduled', 'completed', 'overdue', 'cancelled'
    dosage = db.Column(db.String(100), nullable=True)
    administered_by = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_vac_flock_date", "flock_id", "scheduled_date"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "batchId": self.flock_id,
            "farm_id": self.farm_id,
            "vaccine_name": self.vaccine_name,
            "name": self.vaccine_name,
            "target_disease": self.target_disease,
            "route": self.route,
            "scheduled_date": self.scheduled_date.isoformat() if self.scheduled_date else None,
            "administered_date": self.administered_date.isoformat() if self.administered_date else None,
            "date": self.administered_date.isoformat() if self.administered_date else (self.scheduled_date.isoformat() if self.scheduled_date else None),
            "status": self.status,
            "dosage": self.dosage,
            "administered_by": self.administered_by,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 12. Medicine Model (Table: medicines)
# ------------------------------------------------------------------------------
class Medicine(db.Model):
    __tablename__ = "medicines"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    medicine_name = db.Column(db.String(150), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    administration_route = db.Column(db.String(100), nullable=False, default="Drinking Water")
    start_date = db.Column(db.Date, nullable=False, default=date.today)
    end_date = db.Column(db.Date, nullable=True)
    purpose = db.Column(db.String(255), nullable=True)
    withdrawal_days = db.Column(db.Integer, nullable=False, default=0)
    prescribed_by = db.Column(db.String(150), nullable=True)
    status = db.Column(db.String(50), nullable=False, default="active") # 'active', 'completed'
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "farm_id": self.farm_id,
            "medicine_name": self.medicine_name,
            "dosage": self.dosage,
            "administration_route": self.administration_route,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "purpose": self.purpose,
            "withdrawal_days": self.withdrawal_days,
            "prescribed_by": self.prescribed_by,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 13. Expense Model (Table: expenses)
# ------------------------------------------------------------------------------
class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="SET NULL"), nullable=True, index=True)
    expense_date = db.Column(db.Date, nullable=False, default=date.today)
    category = db.Column(db.String(100), nullable=False) # Chicks, Feed, Medicines, Vaccines, Electricity, Water, Labour, Transport, Other
    description = db.Column(db.String(255), nullable=False)
    amount = db.Column(db.Numeric(12, 2), nullable=False)
    payment_method = db.Column(db.String(50), nullable=False, default="Cash")
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("amount >= 0.00", name="chk_expense_amount"),
        Index("idx_expense_farm_date", "farm_id", "expense_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "flock_id": self.flock_id,
            "expense_date": self.expense_date.isoformat() if self.expense_date else None,
            "date": self.expense_date.isoformat() if self.expense_date else None,
            "category": self.category,
            "description": self.description,
            "amount": float(self.amount),
            "payment_method": self.payment_method,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 14. Sale Model (Table: sales)
# ------------------------------------------------------------------------------
class Sale(db.Model):
    __tablename__ = "sales"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="SET NULL"), nullable=True, index=True)
    sale_date = db.Column(db.Date, nullable=False, default=date.today)
    product_type = db.Column(db.String(50), nullable=False, default="birds") # birds, eggs, manure, other
    quantity = db.Column(db.Numeric(10, 2), nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    total_amount = db.Column(db.Numeric(12, 2), nullable=False)
    buyer_name = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        CheckConstraint("quantity >= 0.00", name="chk_sales_qty"),
        CheckConstraint("total_amount >= 0.00", name="chk_sales_amount"),
        Index("idx_sales_farm_date", "farm_id", "sale_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "flock_id": self.flock_id,
            "sale_date": self.sale_date.isoformat() if self.sale_date else None,
            "date": self.sale_date.isoformat() if self.sale_date else None,
            "product_type": self.product_type,
            "quantity": float(self.quantity),
            "unit_price": float(self.unit_price),
            "total_amount": float(self.total_amount),
            "buyer_name": self.buyer_name,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 15. Inventory Model (Table: inventory)
# ------------------------------------------------------------------------------
class Inventory(db.Model):
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = db.Column(db.String(150), nullable=False)
    category = db.Column(db.String(100), nullable=False) # Feed, Medicine, Vaccine, Equipment, Litter, Other
    quantity = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    unit = db.Column(db.String(50), nullable=False, default="kg") # kg, bags, liters, vials, pieces
    unit_cost = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    reorder_level = db.Column(db.Numeric(10, 2), nullable=False, default=Decimal("10.00"))
    supplier = db.Column(db.String(150), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        CheckConstraint("quantity >= 0.00", name="chk_inventory_qty"),
        Index("idx_inventory_farm", "farm_id", "category")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "item_name": self.item_name,
            "category": self.category,
            "quantity": float(self.quantity),
            "unit": self.unit,
            "unit_cost": float(self.unit_cost),
            "reorder_level": float(self.reorder_level),
            "is_low": float(self.quantity) <= float(self.reorder_level),
            "supplier": self.supplier,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ------------------------------------------------------------------------------
# 16. Task Model (Table: tasks)
# ------------------------------------------------------------------------------
class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="SET NULL"), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    due_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(50), nullable=False, default="pending") # 'pending', 'in_progress', 'completed', 'cancelled'
    priority = db.Column(db.String(20), nullable=False, default="medium") # 'low', 'medium', 'high', 'urgent'
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("idx_tasks_farm_status", "farm_id", "status"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "farm_id": self.farm_id,
            "flock_id": self.flock_id,
            "title": self.title,
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "status": self.status,
            "priority": self.priority,
            "is_completed": self.status == "completed",
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ------------------------------------------------------------------------------
# 17. Notification Model (Table: notifications)
# ------------------------------------------------------------------------------
class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=True, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), nullable=False, default="info") # 'info', 'warning', 'danger', 'critical'
    notification_type = db.Column(db.String(100), nullable=False, default="system") # 'alert', 'task', 'vaccine', 'system'
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    link = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_notif_user_unread", "user_id", "is_read"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "farm_id": self.farm_id,
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
            "notification_type": self.notification_type,
            "is_read": self.is_read,
            "link": self.link,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# 18. User Settings Model (Table: user_settings)
# ------------------------------------------------------------------------------
class UserSetting(db.Model):
    __tablename__ = "user_settings"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False, index=True)
    theme = db.Column(db.String(20), nullable=False, default="light")
    language = db.Column(db.String(10), nullable=False, default="en")
    fcr_target = db.Column(db.Numeric(4, 2), nullable=False, default=Decimal("1.60"))
    currency = db.Column(db.String(10), nullable=False, default="INR")
    phone_alerts = db.Column(db.Boolean, nullable=False, default=True)
    email_alerts = db.Column(db.Boolean, nullable=False, default=True)
    auto_refresh_seconds = db.Column(db.Integer, nullable=False, default=30)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "theme": self.theme,
            "language": self.language,
            "fcr_target": float(self.fcr_target),
            "currency": self.currency,
            "phone_alerts": self.phone_alerts,
            "email_alerts": self.email_alerts,
            "auto_refresh_seconds": self.auto_refresh_seconds,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ------------------------------------------------------------------------------
# Supplementary Model: DailyRecord (Table: daily_records)
# Kept for aggregated queries & legacy compatibility
# ------------------------------------------------------------------------------
class DailyRecord(db.Model):
    __tablename__ = "daily_records"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="CASCADE"), nullable=False, index=True)
    record_date = db.Column(db.Date, nullable=False)
    opening_birds = db.Column(db.Integer, nullable=False, default=0)
    mortality = db.Column(db.Integer, nullable=False, default=0)
    culls = db.Column(db.Integer, nullable=False, default=0)
    closing_birds = db.Column(db.Integer, nullable=False, default=0)
    average_weight_kg = db.Column(db.Numeric(6, 3), nullable=False, default=Decimal("0.000"))
    feed_consumed_kg = db.Column(db.Numeric(8, 2), nullable=False, default=Decimal("0.00"))
    water_consumed_liters = db.Column(db.Numeric(8, 2), nullable=False, default=Decimal("0.00"))
    eggs_produced = db.Column(db.Integer, nullable=False, default=0)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime, nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        UniqueConstraint("flock_id", "record_date", name="uq_flock_record_date"),
        Index("idx_daily_flock_date", "flock_id", "record_date")
    )

    def to_dict(self):
        return {
            "id": self.id,
            "flock_id": self.flock_id,
            "record_date": self.record_date.isoformat() if self.record_date else None,
            "opening_birds": self.opening_birds,
            "mortality": self.mortality,
            "culls": self.culls,
            "closing_birds": self.closing_birds,
            "average_weight_kg": float(self.average_weight_kg),
            "feed_consumed_kg": float(self.feed_consumed_kg),
            "water_consumed_liters": float(self.water_consumed_liters),
            "eggs_produced": self.eggs_produced,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# Supplementary Model: Alert (Table: alerts)
# ------------------------------------------------------------------------------
class Alert(db.Model):
    __tablename__ = "alerts"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    farm_id = db.Column(db.Integer, db.ForeignKey("farms.id", ondelete="CASCADE"), nullable=False, index=True)
    flock_id = db.Column(db.Integer, db.ForeignKey("flocks.id", ondelete="SET NULL"), nullable=True, index=True)
    alert_type = db.Column(db.String(100), nullable=False)
    message = db.Column(db.Text, nullable=False)
    severity = db.Column(db.String(50), nullable=False, default="warning") # info, warning, danger, critical
    is_read = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_alerts_farm_unread", "farm_id", "is_read"),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "farmId": self.farm_id,
            "farm_id": self.farm_id,
            "flockId": self.flock_id,
            "flock_id": self.flock_id,
            "alertType": self.alert_type,
            "alert_type": self.alert_type,
            "title": self.alert_type,
            "message": self.message,
            "description": self.message,
            "severity": self.severity.capitalize(),
            "isRead": self.is_read,
            "is_read": self.is_read,
            "timestamp": self.created_at.strftime("%I:%M %p") if self.created_at else "Just now",
            "created_at": self.created_at.isoformat() if self.created_at else None
        }


# ------------------------------------------------------------------------------
# Supplementary Model: OtpVerification (Table: otp_verifications)
# ------------------------------------------------------------------------------
class OtpVerification(db.Model):
    __tablename__ = "otp_verifications"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    otp_hash = db.Column(db.String(255), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    is_used = db.Column(db.Boolean, nullable=False, default=False)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        Index("idx_otp_user_lookup", "user_id", "is_used", "expires_at"),
    )
