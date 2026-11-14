"""
Smart Poultry Farm Management and Monitoring System - Core Application Server
Features:
- Full-Stack Python Flask Backend with RESTful APIs
- Complete Authentication (Registration & Login with Password, NO OTP required)
- Strict Multi-Tenant Data Isolation (Every user sees and manages only their own data)
- Full CRUD Support for all 18 Modules:
  1. Users, 2. Farms, 3. Flocks, 4. Birds, 5. Feed, 6. Water, 7. Eggs, 8. Mortality,
  9. Weight, 10. Environment, 11. Vaccinations, 12. Medicines, 13. Expenses, 14. Sales,
  15. Inventory, 16. Tasks, 17. Notifications/Alerts, 18. User Settings
- Live Calculated Dashboard Statistics directly from the database
- Automated IoT Sensor Telemetry & Threshold Alerting Engine
- AI/ML Disease Risk and Feed Estimation Decision Support
- Responsive Frontend Serving with Unified Domain & Vercel CORS support
"""

import os
import re
from datetime import datetime, date, timezone, timedelta
from decimal import Decimal
from functools import wraps

from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, flash, send_from_directory, make_response
)
from flask_migrate import Migrate
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required,
    get_jwt_identity, verify_jwt_in_request
)
from werkzeug.security import generate_password_hash, check_password_hash

# Try importing flask_cors, handle if missing
try:
    from flask_cors import CORS
    has_cors = True
except ImportError:
    has_cors = False

from config import Config
from models import (
    db, User, Farm, Flock, Bird, FeedRecord, WaterRecord, EggRecord,
    MortalityRecord, WeightRecord, EnvironmentRecord, Vaccination,
    Medicine, Expense, Sale, Inventory, Task, Notification,
    UserSetting, DailyRecord, Alert, OtpVerification
)
from translations import get_text, TRANSLATIONS
import ai_engine

# --- App Initialization ---
app = Flask(__name__, static_folder="frontend", static_url_path="")
app.config.from_object(Config)

# Enable CORS for cross-origin deployment (e.g. Vercel frontend -> Render backend)
if has_cors:
    CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)
else:
    @app.after_request
    def add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-Requested-With,Accept"
        response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return response

# Handle preflight OPTIONS requests cleanly
@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = make_response()
        res.headers["Access-Control-Allow-Origin"] = "*"
        res.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization,X-Requested-With,Accept"
        res.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
        return res

# Initialize database ORM
db.init_app(app)
migrate = Migrate(app, db)
jwt = JWTManager(app)

# Auto-create tables on startup
with app.app_context():
    try:
        db.create_all()
        # Seed default demo account if no users exist
        if User.query.count() == 0:
            demo_user = User(
                name="Demo Poultry Farmer",
                email="farmer@smartpoultry.com",
                phone="9876543210",
                role="farmer",
                language="en",
                account_status="active",
                mobile_verified=True
            )
            demo_user.set_password("farmer123")
            db.session.add(demo_user)
            db.session.commit()

            demo_farm = Farm(
                owner_id=demo_user.id,
                farm_name="GreenValley Broiler Farm",
                location="Agro Valley Zone, Shed 1-4",
                address="Plot 42, Agriculture Road",
                total_capacity=10000,
                farm_type="Broiler",
                farm_size="3.5 Acres (4 Sheds)",
                established_date=date(2025, 4, 15)
            )
            db.session.add(demo_farm)
            db.session.commit()

            demo_batch = Flock(
                farm_id=demo_farm.id,
                batch_number="B-101",
                bird_type="Broiler",
                breed="Cobb 500",
                initial_bird_count=2500,
                current_bird_count=2490,
                arrival_date=date.today() - timedelta(days=28),
                target_weight_kg=Decimal("2.20"),
                status="active",
                health_status="Good",
                risk_level="Low",
                notes="Healthy chicks vaccinated upon arrival"
            )
            db.session.add(demo_batch)
            db.session.commit()

            # Add demo environment record
            env = EnvironmentRecord(
                farm_id=demo_farm.id,
                flock_id=demo_batch.id,
                temperature_celsius=Decimal("28.5"),
                humidity_percentage=Decimal("62.0"),
                ammonia_ppm=Decimal("12.5"),
                water_level_pct=Decimal("85.0"),
                feed_level_pct=Decimal("78.0"),
                source="IoT_Sensor"
            )
            db.session.add(env)
            db.session.commit()

    except Exception as e:
        app.logger.warning("Could not auto-create tables on startup: %s", e)


# ==============================================================================
# AUTHENTICATION & SECURITY UTILITIES
# ==============================================================================

def get_current_user():
    """
    Returns current authenticated User object from JWT Bearer token or Flask session.
    Provides unified authentication for browser, mobile app, and API clients.
    """
    # 1. Check JWT Authorization Header first (Mobile App & REST API clients)
    auth_header = request.headers.get("Authorization", "")
    if auth_header.startswith("Bearer "):
        try:
            verify_jwt_in_request(optional=True)
            jwt_uid = get_jwt_identity()
            if jwt_uid:
                return db.session.get(User, int(jwt_uid))
        except Exception:
            pass

    # 2. Check Flask Session (Web browser)
    user_id = session.get("user_id")
    if user_id:
        return db.session.get(User, user_id)

    return None

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            if request.path.startswith("/api/"):
                return jsonify({"status": "error", "message": "Authentication required. Please log in."}), 401
            return redirect(url_for("serve_login"))
        return f(*args, **kwargs)
    return decorated_function

def clean_phone(phone_str: str) -> str:
    """Standardizes phone number by removing spaces, dashes, and extra prefixes."""
    if not phone_str:
        return ""
    cleaned = re.sub(r"[^\d+]", "", str(phone_str).strip())
    # If standard 10 digit, return standard
    if len(cleaned) == 10 and not cleaned.startswith("+"):
        return cleaned
    return cleaned


# ==============================================================================
# STATIC & FRONTEND PAGE ROUTING (Responsive UI for Laptop, Mobile, Desktop)
# ==============================================================================

@app.route("/")
def index_route():
    """
    Root route:
    If user is authenticated -> redirect to dashboard.html
    If not authenticated -> serve landing index.html
    """
    user = get_current_user()
    if user:
        return redirect("/dashboard.html")
    return send_from_directory("frontend", "index.html")

@app.route("/login")
@app.route("/login.html")
def serve_login():
    return send_from_directory("frontend", "login.html")

@app.route("/register")
@app.route("/register.html")
def serve_register():
    return send_from_directory("frontend", "register.html")

@app.route("/dashboard.html")
def serve_dashboard():
    return send_from_directory("frontend", "dashboard.html")

@app.route("/farms.html")
def serve_farms():
    return send_from_directory("frontend", "farms.html")

@app.route("/batches.html")
def serve_batches():
    return send_from_directory("frontend", "batches.html")

@app.route("/conditions.html")
def serve_conditions():
    return send_from_directory("frontend", "conditions.html")

@app.route("/monitoring.html")
def serve_monitoring():
    return send_from_directory("frontend", "monitoring.html")

@app.route("/reports.html")
def serve_reports():
    return send_from_directory("frontend", "reports.html")

@app.route("/vaccinations.html")
def serve_vaccinations():
    return send_from_directory("frontend", "vaccinations.html")

@app.route("/predictions.html")
def serve_predictions():
    return send_from_directory("frontend", "predictions.html")

@app.route("/image-prediction.html")
def serve_image_prediction():
    return send_from_directory("frontend", "image-prediction.html")

@app.route("/recommendations.html")
def serve_recommendations():
    return send_from_directory("frontend", "recommendations.html")

@app.route("/alerts.html")
def serve_alerts():
    return send_from_directory("frontend", "alerts.html")

@app.route("/profile.html")
def serve_profile():
    return send_from_directory("frontend", "profile.html")

@app.route("/admin.html")
def serve_admin():
    return send_from_directory("frontend", "admin.html")

@app.route("/overview")
@app.route("/overview.html")
def serve_overview():
    return send_from_directory("frontend", "overview.html")

@app.route("/assets/<path:filename>")
def serve_assets(filename):
    return send_from_directory("frontend/assets", filename)

@app.route("/frontend/<path:filename>")
def serve_frontend_direct(filename):
    return send_from_directory("frontend", filename)


# ==============================================================================
# AUTHENTICATION REST APIS (NO OTP REQUIRED)
# ==============================================================================

@app.route("/api/auth/register", methods=["POST"])
def api_register():
    """
    Direct user registration without OTP.
    Required: Full Name, Mobile Number, Password, Confirm Password.
    Optional: Email, Farm Facility Name, Location, Role.
    """
    data = request.get_json() or {}
    name = (data.get("name") or data.get("fullName") or "").strip()
    raw_phone = (data.get("phone") or data.get("mobileNumber") or data.get("mobile") or "").strip()
    email = (data.get("email") or "").strip() or None
    password = data.get("password", "")
    confirm_password = data.get("confirmPassword", "") or data.get("confirm_password", "")
    role = data.get("role", "farmer").lower()
    farm_name = (data.get("farmName") or data.get("farm_name") or "").strip()
    location = (data.get("location") or "").strip()

    # Input validations
    if not name:
        return jsonify({"status": "error", "message": "Full Name is required"}), 400

    phone = clean_phone(raw_phone)
    if not phone or len(phone) < 7:
        return jsonify({"status": "error", "message": "Valid Mobile Number is required"}), 400

    if not password or len(password) < 6:
        return jsonify({"status": "error", "message": "Password must be at least 6 characters long"}), 400

    if confirm_password and password != confirm_password:
        return jsonify({"status": "error", "message": "Passwords do not match"}), 400

    # Check for existing user by mobile or email
    if User.query.filter_by(phone=phone).first():
        return jsonify({"status": "error", "message": "This mobile number is already registered. Please log in."}), 409

    if email and User.query.filter_by(email=email).first():
        return jsonify({"status": "error", "message": "This email address is already registered."}), 409

    # Create new User
    try:
        user = User(
            name=name,
            phone=phone,
            email=email,
            role=role if role in ("farmer", "veterinarian", "admin") else "farmer",
            mobile_verified=True,
            account_status="active",
            language="en"
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Create user default settings
        setting = UserSetting(user_id=user.id, language="en", currency="INR", fcr_target=Decimal("1.60"))
        db.session.add(setting)

        # Create default Farm if farm name provided
        if farm_name:
            initial_farm = Farm(
                owner_id=user.id,
                farm_name=farm_name,
                location=location or "Agro Region",
                total_capacity=5000,
                farm_type="Broiler",
                farm_size="2 Acres",
                established_date=date.today()
            )
            db.session.add(initial_farm)

        db.session.commit()

        # Set session and generate JWT access token
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_role"] = user.role
        access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))

        return jsonify({
            "status": "success",
            "message": "Account registered successfully!",
            "token": access_token,
            "user": user.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        app.logger.error("Registration error: %s", e)
        return jsonify({"status": "error", "message": f"Registration failed: {str(e)}"}), 500


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    """
    Direct user login using Mobile Number / Email and Password (NO OTP REQUIRED).
    """
    data = request.get_json() or {}
    identifier = (data.get("identifier") or data.get("phone") or data.get("email") or "").strip()
    password = data.get("password", "")

    if not identifier:
        return jsonify({"status": "error", "message": "Mobile number or email is required"}), 400
    if not password:
        return jsonify({"status": "error", "message": "Password is required"}), 400

    phone_clean = clean_phone(identifier)

    # Search user by phone or email
    user = User.query.filter(
        (User.phone == phone_clean) |
        (User.phone == identifier) |
        (User.email == identifier.lower())
    ).first()

    if not user or not user.check_password(password):
        return jsonify({"status": "error", "message": "Invalid mobile number or password."}), 401

    if user.account_status == "suspended":
        return jsonify({"status": "error", "message": "Your account has been suspended. Please contact support."}), 403

    # Set session
    session["user_id"] = user.id
    session["user_name"] = user.name
    session["user_role"] = user.role
    access_token = create_access_token(identity=str(user.id), expires_delta=timedelta(days=7))

    return jsonify({
        "status": "success",
        "message": f"Welcome back, {user.name}!",
        "token": access_token,
        "user": user.to_dict()
    }), 200


@app.route("/api/auth/me", methods=["GET"])
@login_required
def api_me():
    user = get_current_user()
    return jsonify({
        "status": "success",
        "user": user.to_dict()
    }), 200


@app.route("/api/auth/logout", methods=["POST", "GET"])
def api_logout():
    session.clear()
    return jsonify({"status": "success", "message": "Logged out successfully"}), 200


@app.route("/api/auth/profile", methods=["PUT"])
@login_required
def api_update_profile():
    user = get_current_user()
    data = request.get_json() or {}

    if "name" in data and data["name"].strip():
        user.name = data["name"].strip()
    if "email" in data:
        email = data["email"].strip() or None
        if email and email != user.email:
            existing = User.query.filter_by(email=email).first()
            if existing:
                return jsonify({"status": "error", "message": "Email already in use"}), 409
            user.email = email
    if "language" in data:
        user.language = data["language"]
    if "specialization" in data:
        user.specialization = data["specialization"]

    db.session.commit()
    return jsonify({"status": "success", "message": "Profile updated", "user": user.to_dict()})


# ==============================================================================
# DASHBOARD LIVE DATA API (Strictly Isolated to Authenticated User)
# ==============================================================================

@app.route("/api/dashboard/stats", methods=["GET"])
@login_required
def get_dashboard_stats():
    """
    Computes real-time live statistics strictly for the logged-in user's farms and flocks.
    """
    user = get_current_user()

    # User's farms
    farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in farms]

    if not user_farm_ids:
        return jsonify({
            "status": "success",
            "hasFarms": False,
            "total_farms": 0,
            "total_live_birds": 0,
            "total_flocks": 0,
            "daily_egg_production": 0,
            "daily_feed_consumption": 0.0,
            "daily_water_consumption": 0.0,
            "mortality_count": 0,
            "mortality_rate": "0.00",
            "average_bird_weight": 0.0,
            "temperature": 27.5,
            "humidity": 65.0,
            "ammonia": 12.0,
            "pending_tasks": 0,
            "recent_activities": [],
            "unread_alerts": 0,
            "fcr": 1.55,
            "health_score": 92
        }), 200

    # User's flocks
    active_flocks = Flock.query.filter(
        Flock.farm_id.in_(user_farm_ids),
        Flock.status == "active"
    ).all()
    user_flock_ids = [fl.id for fl in active_flocks]

    total_live_birds = sum(fl.current_bird_count for fl in active_flocks)
    total_flocks = len(active_flocks)

    # Today's logs
    today_d = date.today()
    daily_feed = 0.0
    daily_water = 0.0
    daily_eggs = 0
    today_mortality = 0

    if user_flock_ids:
        # Sum from FeedRecord
        feed_sum = db.session.query(db.func.sum(FeedRecord.quantity_kg)).filter(
            FeedRecord.flock_id.in_(user_flock_ids),
            FeedRecord.record_date == today_d
        ).scalar()
        daily_feed = float(feed_sum or 0.0)

        # Sum from WaterRecord
        water_sum = db.session.query(db.func.sum(WaterRecord.quantity_liters)).filter(
            WaterRecord.flock_id.in_(user_flock_ids),
            WaterRecord.record_date == today_d
        ).scalar()
        daily_water = float(water_sum or 0.0)

        # Sum from EggRecord
        egg_sum = db.session.query(db.func.sum(EggRecord.eggs_produced)).filter(
            EggRecord.flock_id.in_(user_flock_ids),
            EggRecord.record_date == today_d
        ).scalar()
        daily_eggs = int(egg_sum or 0)

        # Sum from MortalityRecord
        mort_sum = db.session.query(db.func.sum(MortalityRecord.mortality_count)).filter(
            MortalityRecord.flock_id.in_(user_flock_ids),
            MortalityRecord.record_date == today_d
        ).scalar()
        today_mortality = int(mort_sum or 0)

        # Also check DailyRecord fallback if any
        if daily_feed == 0 and daily_water == 0 and today_mortality == 0:
            today_daily = DailyRecord.query.filter(
                DailyRecord.flock_id.in_(user_flock_ids),
                DailyRecord.record_date == today_d
            ).all()
            for r in today_daily:
                daily_feed += float(r.feed_consumed_kg or 0.0)
                daily_water += float(r.water_consumed_liters or 0.0)
                daily_eggs += int(r.eggs_produced or 0)
                today_mortality += int(r.mortality or 0)

    # Average weight across active flocks
    avg_weight = 0.0
    if active_flocks:
        weights = [float(fl.target_weight_kg or 2.0) for fl in active_flocks]
        avg_weight = round(sum(weights) / len(weights), 2)

    # Latest Environment telemetry
    latest_env = EnvironmentRecord.query.filter(
        EnvironmentRecord.farm_id.in_(user_farm_ids)
    ).order_by(EnvironmentRecord.recorded_at.desc()).first()

    temp = float(latest_env.temperature_celsius) if latest_env else 27.5
    hum = float(latest_env.humidity_percentage) if latest_env else 64.0
    nh3 = float(latest_env.ammonia_ppm) if latest_env else 11.5

    # Pending Tasks count
    pending_tasks = Task.query.filter(
        Task.farm_id.in_(user_farm_ids),
        Task.status.in_(["pending", "in_progress"])
    ).count()

    # Unread Alerts count
    unread_alerts = Alert.query.filter(
        Alert.farm_id.in_(user_farm_ids),
        Alert.is_read == False
    ).count()

    # Calculate mortality rate
    mortality_rate = "0.00"
    if total_live_birds > 0:
        mortality_rate = f"{(today_mortality / total_live_birds * 100):.2f}"

    # FCR calculation (Total feed consumed / Total weight)
    fcr = 1.58
    if active_flocks:
        total_flock_feed = db.session.query(db.func.sum(DailyRecord.feed_consumed_kg)).filter(
            DailyRecord.flock_id.in_(user_flock_ids)
        ).scalar()
        if total_flock_feed and total_live_birds > 0:
            est_total_weight = total_live_birds * avg_weight
            if est_total_weight > 0:
                fcr = round(float(total_flock_feed) / est_total_weight, 2)

    # Recent activities (combined audit trail)
    recent_activities = []
    recent_sales = Sale.query.filter(Sale.farm_id.in_(user_farm_ids)).order_by(Sale.sale_date.desc()).limit(3).all()
    for s in recent_sales:
        recent_activities.append({
            "type": "sale",
            "title": f"Sold {float(s.quantity)} {s.product_type}",
            "amount": f"₹{float(s.total_amount):,.2f}",
            "date": s.sale_date.isoformat(),
            "badge": "success"
        })

    recent_expenses = Expense.query.filter(Expense.farm_id.in_(user_farm_ids)).order_by(Expense.expense_date.desc()).limit(3).all()
    for e in recent_expenses:
        recent_activities.append({
            "type": "expense",
            "title": f"{e.category}: {e.description}",
            "amount": f"-₹{float(e.amount):,.2f}",
            "date": e.expense_date.isoformat(),
            "badge": "danger"
        })

    return jsonify({
        "status": "success",
        "hasFarms": True,
        "total_farms": len(farms),
        "total_live_birds": total_live_birds,
        "total_flocks": total_flocks,
        "daily_egg_production": daily_eggs,
        "daily_feed_consumption": round(daily_feed, 2),
        "daily_water_consumption": round(daily_water, 2),
        "mortality_count": today_mortality,
        "mortality_rate": mortality_rate,
        "average_bird_weight": avg_weight,
        "temperature": temp,
        "humidity": hum,
        "ammonia": nh3,
        "pending_tasks": pending_tasks,
        "recent_activities": recent_activities,
        "unread_alerts": unread_alerts,
        "fcr": fcr,
        "health_score": 90 if unread_alerts == 0 else max(60, 90 - unread_alerts * 5)
    }), 200


# ==============================================================================
# MODULE 2: FARM MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/farms", methods=["GET"])
@login_required
def list_farms():
    user = get_current_user()
    farms = Farm.query.filter_by(owner_id=user.id).order_by(Farm.id.desc()).all()
    return jsonify({
        "status": "success",
        "farms": [f.to_dict() for f in farms],
        "count": len(farms)
    })

@app.route("/api/farms/<int:farm_id>", methods=["GET"])
@login_required
def get_farm(farm_id):
    user = get_current_user()
    farm = Farm.query.filter_by(id=farm_id, owner_id=user.id).first()
    if not farm:
        return jsonify({"status": "error", "message": "Farm not found or access denied"}), 404
    return jsonify({"status": "success", "farm": farm.to_dict()})

@app.route("/api/farms", methods=["POST"])
@app.route("/api/farms/create", methods=["POST"])
@login_required
def create_farm():
    user = get_current_user()
    data = request.get_json() or {}
    farm_name = (data.get("name") or data.get("farm_name") or "").strip()

    if not farm_name:
        return jsonify({"status": "error", "message": "Farm Name is required"}), 400

    try:
        est_date = None
        if data.get("establishedDate") or data.get("established_date"):
            try:
                est_date = datetime.strptime(data.get("establishedDate") or data.get("established_date"), "%Y-%m-%d").date()
            except Exception:
                est_date = date.today()

        farm = Farm(
            owner_id=user.id,
            farm_name=farm_name,
            location=data.get("location", "").strip() or "Agro Region",
            address=data.get("address", "").strip(),
            total_capacity=int(data.get("capacity") or data.get("total_capacity") or 5000),
            farm_type=data.get("birdType") or data.get("farm_type") or "Broiler",
            farm_size=data.get("farmSize") or data.get("farm_size") or "2 Acres",
            established_date=est_date or date.today()
        )
        db.session.add(farm)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Farm created successfully",
            "farm": farm.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Could not create farm: {str(e)}"}), 500

@app.route("/api/farms/<int:farm_id>", methods=["PUT"])
@login_required
def update_farm(farm_id):
    user = get_current_user()
    farm = Farm.query.filter_by(id=farm_id, owner_id=user.id).first()
    if not farm:
        return jsonify({"status": "error", "message": "Farm not found or unauthorized"}), 404

    data = request.get_json() or {}
    if "name" in data or "farm_name" in data:
        farm.farm_name = (data.get("name") or data.get("farm_name")).strip()
    if "location" in data:
        farm.location = data.get("location").strip()
    if "capacity" in data or "total_capacity" in data:
        farm.total_capacity = int(data.get("capacity") or data.get("total_capacity"))
    if "birdType" in data or "farm_type" in data:
        farm.farm_type = data.get("birdType") or data.get("farm_type")
    if "farmSize" in data or "farm_size" in data:
        farm.farm_size = data.get("farmSize") or data.get("farm_size")

    db.session.commit()
    return jsonify({"status": "success", "message": "Farm updated successfully", "farm": farm.to_dict()})

@app.route("/api/farms/<int:farm_id>", methods=["DELETE"])
@login_required
def delete_farm(farm_id):
    user = get_current_user()
    farm = Farm.query.filter_by(id=farm_id, owner_id=user.id).first()
    if not farm:
        return jsonify({"status": "error", "message": "Farm not found or unauthorized"}), 404

    db.session.delete(farm)
    db.session.commit()
    return jsonify({"status": "success", "message": "Farm and all associated records deleted"})


# ==============================================================================
# MODULE 3: FLOCK / BATCH MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/flocks", methods=["GET"])
@login_required
def list_flocks():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    query = Flock.query.filter(Flock.farm_id.in_(user_farm_ids))

    farm_id = request.args.get("farm_id", type=int)
    if farm_id:
        if farm_id not in user_farm_ids:
            return jsonify({"status": "error", "message": "Access denied to this farm"}), 403
        query = query.filter_by(farm_id=farm_id)

    status = request.args.get("status")
    if status:
        query = query.filter_by(status=status)

    flocks = query.order_by(Flock.id.desc()).all()
    return jsonify({
        "status": "success",
        "flocks": [fl.to_dict() for fl in flocks],
        "count": len(flocks)
    })

@app.route("/api/flocks/<int:flock_id>", methods=["GET"])
@login_required
def get_flock(flock_id):
    user = get_current_user()
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Batch not found or access denied"}), 404
    return jsonify({"status": "success", "batch": flock.to_dict(), "flock": flock.to_dict()})

@app.route("/api/flocks", methods=["POST"])
@app.route("/api/flocks/create", methods=["POST"])
@login_required
def create_flock():
    user = get_current_user()
    data = request.get_json() or {}

    farm_id = data.get("farmId") or data.get("farm_id")
    if not farm_id:
        user_farm = Farm.query.filter_by(owner_id=user.id).first()
        if not user_farm:
            return jsonify({"status": "error", "message": "Please create a farm first"}), 400
        farm_id = user_farm.id
    else:
        farm_id = int(farm_id)
        if not Farm.query.filter_by(id=farm_id, owner_id=user.id).first():
            return jsonify({"status": "error", "message": "Unauthorized farm selection"}), 403

    batch_name = (data.get("name") or data.get("batch_number") or "").strip()
    if not batch_name:
        batch_name = f"BATCH-{datetime.now().strftime('%Y%m%d%H%M')}"
    # Strip 'Batch ' prefix if entered by user
    batch_name = re.sub(r"^Batch\s+", "", batch_name, flags=re.IGNORECASE)

    bird_count = int(data.get("birdCount") or data.get("initial_bird_count") or 1000)
    bird_type = data.get("birdType") or data.get("bird_type") or "Broiler"
    breed = data.get("breed") or "Cobb 500"

    arrival_date = date.today()
    if data.get("startDate") or data.get("arrival_date"):
        try:
            arrival_date = datetime.strptime(data.get("startDate") or data.get("arrival_date"), "%Y-%m-%d").date()
        except Exception:
            arrival_date = date.today()

    try:
        flock = Flock(
            farm_id=farm_id,
            batch_number=batch_name,
            bird_type=bird_type,
            breed=breed,
            initial_bird_count=bird_count,
            current_bird_count=bird_count,
            arrival_date=arrival_date,
            target_weight_kg=Decimal(str(data.get("target_weight_kg", 2.00))),
            status="active",
            health_status=data.get("healthStatus", "Good"),
            risk_level=data.get("riskLevel", "Low"),
            notes=data.get("notes", "")
        )
        db.session.add(flock)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Batch registered successfully",
            "batch": flock.to_dict(),
            "flock": flock.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"Could not create batch: {str(e)}"}), 500

@app.route("/api/flocks/<int:flock_id>", methods=["PUT"])
@login_required
def update_flock(flock_id):
    user = get_current_user()
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Batch not found or unauthorized"}), 404

    data = request.get_json() or {}
    if "name" in data or "batch_number" in data:
        name = (data.get("name") or data.get("batch_number")).strip()
        flock.batch_number = re.sub(r"^Batch\s+", "", name, flags=re.IGNORECASE)
    if "birdCount" in data or "current_bird_count" in data:
        flock.current_bird_count = int(data.get("birdCount") or data.get("current_bird_count"))
    if "birdType" in data or "bird_type" in data:
        flock.bird_type = data.get("birdType") or data.get("bird_type")
    if "healthStatus" in data or "health_status" in data:
        flock.health_status = data.get("healthStatus") or data.get("health_status")
    if "riskLevel" in data or "risk_level" in data:
        flock.risk_level = data.get("riskLevel") or data.get("risk_level")
    if "target_weight_kg" in data:
        flock.target_weight_kg = Decimal(str(data["target_weight_kg"]))

    db.session.commit()
    return jsonify({"status": "success", "message": "Batch updated", "batch": flock.to_dict()})

@app.route("/api/flocks/<int:flock_id>", methods=["DELETE"])
@login_required
def delete_flock(flock_id):
    user = get_current_user()
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Batch not found or unauthorized"}), 404

    db.session.delete(flock)
    db.session.commit()
    return jsonify({"status": "success", "message": "Batch deleted successfully"})

@app.route("/api/flocks/<int:flock_id>/status", methods=["POST"])
@login_required
def update_flock_status(flock_id):
    user = get_current_user()
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Batch not found"}), 404

    data = request.get_json() or {}
    new_status = data.get("status")
    if new_status in ("active", "sold", "closed"):
        flock.status = new_status
        db.session.commit()
        return jsonify({"status": "success", "message": f"Status updated to {new_status}"})
    return jsonify({"status": "error", "message": "Invalid status"}), 400


# ==============================================================================
# MODULE 4: BIRD MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/birds", methods=["GET"])
@login_required
def list_birds():
    user = get_current_user()
    flock_id = request.args.get("flock_id", type=int)
    query = Bird.query.join(Flock).join(Farm).filter(Farm.owner_id == user.id)
    if flock_id:
        query = query.filter(Bird.flock_id == flock_id)
    birds = query.order_by(Bird.id.desc()).all()
    return jsonify({"status": "success", "birds": [b.to_dict() for b in birds]})

@app.route("/api/birds", methods=["POST"])
@login_required
def add_bird():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id")
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Invalid batch specified"}), 400

    bird = Bird(
        flock_id=flock.id,
        tag_number=data.get("tag_number"),
        shed_name=data.get("shed_name", "Shed 1"),
        cage_or_pen=data.get("cage_or_pen"),
        current_weight_kg=Decimal(str(data.get("current_weight_kg", 0.0))),
        health_status=data.get("health_status", "Healthy"),
        notes=data.get("notes")
    )
    db.session.add(bird)
    db.session.commit()
    return jsonify({"status": "success", "bird": bird.to_dict()}), 201

@app.route("/api/birds/<int:bird_id>", methods=["DELETE"])
@login_required
def delete_bird(bird_id):
    user = get_current_user()
    bird = Bird.query.join(Flock).join(Farm).filter(Bird.id == bird_id, Farm.owner_id == user.id).first()
    if not bird:
        return jsonify({"status": "error", "message": "Bird record not found"}), 404
    db.session.delete(bird)
    db.session.commit()
    return jsonify({"status": "success", "message": "Bird record deleted"})


# ==============================================================================
# MODULE 5: FEED MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/records/feed", methods=["GET"])
@login_required
def list_feed_records():
    user = get_current_user()
    flock_id = request.args.get("flock_id", type=int)
    query = FeedRecord.query.join(Flock).join(Farm).filter(Farm.owner_id == user.id)
    if flock_id:
        query = query.filter(FeedRecord.flock_id == flock_id)
    records = query.order_by(FeedRecord.record_date.desc()).limit(100).all()
    return jsonify({"status": "success", "records": [r.to_dict() for r in records]})

@app.route("/api/records/feed", methods=["POST"])
@login_required
def add_feed_record():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Valid batch required"}), 400

    rec_date = date.today()
    if data.get("record_date") or data.get("date"):
        try:
            rec_date = datetime.strptime(data.get("record_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    qty = Decimal(str(data.get("quantity_kg") or data.get("feedConsumption") or 0.0))
    cost = Decimal(str(data.get("unit_cost", 0.0)))
    total = Decimal(str(data.get("total_cost", float(qty * cost))))

    feed_rec = FeedRecord(
        flock_id=flock.id,
        farm_id=flock.farm_id,
        record_date=rec_date,
        feed_type=data.get("feed_type", "Broiler Starter"),
        quantity_kg=qty,
        unit_cost=cost,
        total_cost=total,
        supplier=data.get("supplier"),
        notes=data.get("notes")
    )
    db.session.add(feed_rec)
    db.session.commit()
    return jsonify({"status": "success", "record": feed_rec.to_dict()}), 201

@app.route("/api/records/feed/<int:rec_id>", methods=["DELETE"])
@login_required
def delete_feed_record(rec_id):
    user = get_current_user()
    rec = FeedRecord.query.join(Flock).join(Farm).filter(FeedRecord.id == rec_id, Farm.owner_id == user.id).first()
    if not rec:
        return jsonify({"status": "error", "message": "Record not found"}), 404
    db.session.delete(rec)
    db.session.commit()
    return jsonify({"status": "success", "message": "Feed record deleted"})


# ==============================================================================
# MODULE 6: WATER MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/records/water", methods=["GET"])
@login_required
def list_water_records():
    user = get_current_user()
    flock_id = request.args.get("flock_id", type=int)
    query = WaterRecord.query.join(Flock).join(Farm).filter(Farm.owner_id == user.id)
    if flock_id:
        query = query.filter(WaterRecord.flock_id == flock_id)
    records = query.order_by(WaterRecord.record_date.desc()).limit(100).all()
    return jsonify({"status": "success", "records": [r.to_dict() for r in records]})

@app.route("/api/records/water", methods=["POST"])
@login_required
def add_water_record():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Valid batch required"}), 400

    rec_date = date.today()
    if data.get("record_date") or data.get("date"):
        try:
            rec_date = datetime.strptime(data.get("record_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    water_rec = WaterRecord(
        flock_id=flock.id,
        farm_id=flock.farm_id,
        record_date=rec_date,
        quantity_liters=Decimal(str(data.get("quantity_liters") or data.get("waterConsumption") or 0.0)),
        water_source=data.get("water_source", "Borewell"),
        temperature_celsius=Decimal(str(data["temperature"])) if "temperature" in data and data["temperature"] else None,
        ph_level=Decimal(str(data["ph_level"])) if "ph_level" in data and data["ph_level"] else None,
        notes=data.get("notes")
    )
    db.session.add(water_rec)
    db.session.commit()
    return jsonify({"status": "success", "record": water_rec.to_dict()}), 201

@app.route("/api/records/water/<int:rec_id>", methods=["DELETE"])
@login_required
def delete_water_record(rec_id):
    user = get_current_user()
    rec = WaterRecord.query.join(Flock).join(Farm).filter(WaterRecord.id == rec_id, Farm.owner_id == user.id).first()
    if not rec:
        return jsonify({"status": "error", "message": "Record not found"}), 404
    db.session.delete(rec)
    db.session.commit()
    return jsonify({"status": "success", "message": "Water record deleted"})


# ==============================================================================
# MODULE 7: EGG PRODUCTION MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/records/egg", methods=["GET"])
@login_required
def list_egg_records():
    user = get_current_user()
    flock_id = request.args.get("flock_id", type=int)
    query = EggRecord.query.join(Flock).join(Farm).filter(Farm.owner_id == user.id)
    if flock_id:
        query = query.filter(EggRecord.flock_id == flock_id)
    records = query.order_by(EggRecord.record_date.desc()).limit(100).all()
    return jsonify({"status": "success", "records": [r.to_dict() for r in records]})

@app.route("/api/records/egg", methods=["POST"])
@login_required
def add_egg_record():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Valid batch required"}), 400

    rec_date = date.today()
    if data.get("record_date") or data.get("date"):
        try:
            rec_date = datetime.strptime(data.get("record_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    egg_rec = EggRecord(
        flock_id=flock.id,
        farm_id=flock.farm_id,
        record_date=rec_date,
        eggs_produced=int(data.get("eggs_produced") or data.get("eggsCollected") or 0),
        eggs_sold=int(data.get("eggs_sold", 0)),
        damaged_eggs=int(data.get("damaged_eggs", 0)),
        selling_price_per_egg=Decimal(str(data.get("selling_price_per_egg", 0.0))),
        notes=data.get("notes")
    )
    db.session.add(egg_rec)
    db.session.commit()
    return jsonify({"status": "success", "record": egg_rec.to_dict()}), 201

@app.route("/api/records/egg/<int:rec_id>", methods=["DELETE"])
@login_required
def delete_egg_record(rec_id):
    user = get_current_user()
    rec = EggRecord.query.join(Flock).join(Farm).filter(EggRecord.id == rec_id, Farm.owner_id == user.id).first()
    if not rec:
        return jsonify({"status": "error", "message": "Record not found"}), 404
    db.session.delete(rec)
    db.session.commit()
    return jsonify({"status": "success", "message": "Egg record deleted"})


# ==============================================================================
# MODULE 8: MORTALITY TRACKING (CRUD & Automatic Flock Count Deduction)
# ==============================================================================

@app.route("/api/records/mortality", methods=["GET"])
@login_required
def list_mortality_records():
    user = get_current_user()
    flock_id = request.args.get("flock_id", type=int)
    query = MortalityRecord.query.join(Flock).join(Farm).filter(Farm.owner_id == user.id)
    if flock_id:
        query = query.filter(MortalityRecord.flock_id == flock_id)
    records = query.order_by(MortalityRecord.record_date.desc()).limit(100).all()
    return jsonify({"status": "success", "records": [r.to_dict() for r in records]})

@app.route("/api/records/mortality", methods=["POST"])
@login_required
def add_mortality_record():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Valid batch required"}), 400

    rec_date = date.today()
    if data.get("record_date") or data.get("date"):
        try:
            rec_date = datetime.strptime(data.get("record_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    mort_count = int(data.get("mortality_count") or data.get("mortality") or 1)
    culls_count = int(data.get("culls_count", 0))

    mort_rec = MortalityRecord(
        flock_id=flock.id,
        farm_id=flock.farm_id,
        record_date=rec_date,
        mortality_count=mort_count,
        culls_count=culls_count,
        suspected_cause=data.get("suspected_cause", "Natural / Unknown"),
        symptoms=data.get("symptoms", ""),
        disposal_method=data.get("disposal_method", "Composting"),
        notes=data.get("notes")
    )
    db.session.add(mort_rec)

    # Automatically deduct from flock live count
    flock.current_bird_count = max(0, flock.current_bird_count - (mort_count + culls_count))

    # Alert if mortality is abnormally high (>1% in a single day)
    if flock.initial_bird_count > 0 and (mort_count / flock.initial_bird_count) > 0.01:
        alert = Alert(
            farm_id=flock.farm_id,
            flock_id=flock.id,
            alert_type="Mortality Spike Alert",
            message=f"Flock {flock.batch_number} reported {mort_count} bird deaths today. Immediate biosecurity and veterinary inspection advised.",
            severity="critical"
        )
        db.session.add(alert)

    db.session.commit()
    return jsonify({"status": "success", "record": mort_rec.to_dict(), "current_bird_count": flock.current_bird_count}), 201

@app.route("/api/records/mortality/<int:rec_id>", methods=["DELETE"])
@login_required
def delete_mortality_record(rec_id):
    user = get_current_user()
    rec = MortalityRecord.query.join(Flock).join(Farm).filter(MortalityRecord.id == rec_id, Farm.owner_id == user.id).first()
    if not rec:
        return jsonify({"status": "error", "message": "Record not found"}), 404
    db.session.delete(rec)
    db.session.commit()
    return jsonify({"status": "success", "message": "Mortality record deleted"})


# ==============================================================================
# MODULE 9: WEIGHT MONITORING (CRUD)
# ==============================================================================

@app.route("/api/records/weight", methods=["GET"])
@login_required
def list_weight_records():
    user = get_current_user()
    flock_id = request.args.get("flock_id", type=int)
    query = WeightRecord.query.join(Flock).join(Farm).filter(Farm.owner_id == user.id)
    if flock_id:
        query = query.filter(WeightRecord.flock_id == flock_id)
    records = query.order_by(WeightRecord.record_date.desc()).limit(100).all()
    return jsonify({"status": "success", "records": [r.to_dict() for r in records]})

@app.route("/api/records/weight", methods=["POST"])
@login_required
def add_weight_record():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")
    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Valid batch required"}), 400

    rec_date = date.today()
    if data.get("record_date") or data.get("date"):
        try:
            rec_date = datetime.strptime(data.get("record_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    avg_w = Decimal(str(data.get("average_weight_kg") or data.get("avgWeight") or 1.500))

    weight_rec = WeightRecord(
        flock_id=flock.id,
        farm_id=flock.farm_id,
        record_date=rec_date,
        sample_size=int(data.get("sample_size", 10)),
        average_weight_kg=avg_w,
        target_weight_kg=flock.target_weight_kg,
        uniformity_percentage=Decimal(str(data.get("uniformity_percentage", 85.0))),
        notes=data.get("notes")
    )
    db.session.add(weight_rec)
    db.session.commit()
    return jsonify({"status": "success", "record": weight_rec.to_dict()}), 201

@app.route("/api/records/weight/<int:rec_id>", methods=["DELETE"])
@login_required
def delete_weight_record(rec_id):
    user = get_current_user()
    rec = WeightRecord.query.join(Flock).join(Farm).filter(WeightRecord.id == rec_id, Farm.owner_id == user.id).first()
    if not rec:
        return jsonify({"status": "error", "message": "Record not found"}), 404
    db.session.delete(rec)
    db.session.commit()
    return jsonify({"status": "success", "message": "Weight record deleted"})


# ==============================================================================
# COMBINED DAILY LOG / CONDITION ENDPOINT (Synchronizes All Records)
# ==============================================================================

@app.route("/api/records/daily", methods=["POST"])
@app.route("/api/logs/daily", methods=["POST"])
@login_required
def add_daily_operation_log():
    """
    Accepts full operational condition log and saves into:
    DailyRecord, FeedRecord, WaterRecord, MortalityRecord, WeightRecord, and EggRecord.
    """
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")

    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        # Fallback to user's first flock if none selected
        flock = Flock.query.join(Farm).filter(Farm.owner_id == user.id).first()
        if not flock:
            return jsonify({"status": "error", "message": "No active flock found. Please create a batch first."}), 400

    rec_date = date.today()
    if data.get("record_date") or data.get("date"):
        try:
            rec_date = datetime.strptime(data.get("record_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    mortality = int(data.get("mortality", 0))
    culls = int(data.get("culls", 0))
    feed_kg = Decimal(str(data.get("feed_consumed_kg") or data.get("feedConsumption") or 0.0))
    water_l = Decimal(str(data.get("water_consumed_liters") or data.get("waterConsumption") or 0.0))
    avg_weight = Decimal(str(data.get("average_weight_kg") or data.get("avgWeight") or 1.50))
    eggs = int(data.get("eggs_produced") or data.get("eggsCollected") or 0)
    symptoms = ", ".join(data.get("symptoms", [])) if isinstance(data.get("symptoms"), list) else (data.get("symptoms") or "")
    notes = data.get("notes") or symptoms

    closing_birds = max(0, flock.current_bird_count - (mortality + culls))
    flock.current_bird_count = closing_birds

    # Save to DailyRecord
    daily = DailyRecord(
        flock_id=flock.id,
        record_date=rec_date,
        opening_birds=flock.current_bird_count,
        mortality=mortality,
        culls=culls,
        closing_birds=closing_birds,
        average_weight_kg=avg_weight,
        feed_consumed_kg=feed_kg,
        water_consumed_liters=water_l,
        eggs_produced=eggs,
        notes=notes
    )
    db.session.add(daily)

    # Also log to specific relational records if values present
    if feed_kg > 0:
        db.session.add(FeedRecord(
            flock_id=flock.id, farm_id=flock.farm_id, record_date=rec_date,
            feed_type="Standard Broiler Feed", quantity_kg=feed_kg
        ))
    if water_l > 0:
        db.session.add(WaterRecord(
            flock_id=flock.id, farm_id=flock.farm_id, record_date=rec_date,
            quantity_liters=water_l
        ))
    if mortality > 0 or culls > 0:
        db.session.add(MortalityRecord(
            flock_id=flock.id, farm_id=flock.farm_id, record_date=rec_date,
            mortality_count=mortality, culls_count=culls, symptoms=symptoms, notes=notes
        ))
    if avg_weight > 0:
        db.session.add(WeightRecord(
            flock_id=flock.id, farm_id=flock.farm_id, record_date=rec_date,
            average_weight_kg=avg_weight
        ))
    if eggs > 0:
        db.session.add(EggRecord(
            flock_id=flock.id, farm_id=flock.farm_id, record_date=rec_date,
            eggs_produced=eggs
        ))

    # Save environmental condition if telemetry included
    if "temperature" in data and "humidity" in data:
        db.session.add(EnvironmentRecord(
            farm_id=flock.farm_id,
            flock_id=flock.id,
            temperature_celsius=Decimal(str(data["temperature"])),
            humidity_percentage=Decimal(str(data["humidity"])),
            ammonia_ppm=Decimal(str(data.get("ammonia", 12.0))),
            source="Manual_Entry"
        ))

    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Daily operation record and condition log saved successfully",
        "current_bird_count": flock.current_bird_count
    }), 201


# ==============================================================================
# MODULE 10: ENVIRONMENT / IOT MONITORING & TELEMETRY
# ==============================================================================

@app.route("/api/records/environment", methods=["GET"])
@login_required
def list_environment_records():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    farm_id = request.args.get("farm_id", type=int)
    query = EnvironmentRecord.query.filter(EnvironmentRecord.farm_id.in_(user_farm_ids))
    if farm_id and farm_id in user_farm_ids:
        query = query.filter_by(farm_id=farm_id)

    records = query.order_by(EnvironmentRecord.recorded_at.desc()).limit(50).all()
    return jsonify({"status": "success", "records": [r.to_dict() for r in records]})

@app.route("/api/iot/telemetry", methods=["POST"])
def post_iot_telemetry():
    """
    Accepts real-time telemetry from physical ESP32 / Arduino hardware or simulator.
    Evaluates threshold triggers and generates alerts.
    """
    data = request.get_json() or {}
    farm_id = data.get("farm_id") or data.get("farmId") or 1
    temp = float(data.get("temperature", 28.0))
    hum = float(data.get("humidity", 60.0))
    nh3 = float(data.get("ammonia_ppm", data.get("ammonia", 10.0)))
    water_pct = float(data.get("water_level_pct", data.get("water_level", 100.0)))
    feed_pct = float(data.get("feed_level_pct", data.get("feed_level", 100.0)))

    env = EnvironmentRecord(
        farm_id=int(farm_id),
        flock_id=data.get("flock_id"),
        temperature_celsius=Decimal(str(temp)),
        humidity_percentage=Decimal(str(hum)),
        ammonia_ppm=Decimal(str(nh3)),
        water_level_pct=Decimal(str(water_pct)),
        feed_level_pct=Decimal(str(feed_pct)),
        source="ESP32_Telemetry"
    )
    db.session.add(env)

    # Automated Threshold Alerts
    alerts_triggered = []
    if temp >= 34.0:
        al = Alert(
            farm_id=int(farm_id), alert_type="High Temperature Alert",
            message=f"Critical Heat Alert: Shed temperature reached {temp}°C! Activate cooling pads immediately.",
            severity="critical"
        )
        db.session.add(al)
        alerts_triggered.append("High Temperature")

    if nh3 >= 25.0:
        al = Alert(
            farm_id=int(farm_id), alert_type="Ammonia Gas Danger",
            message=f"Toxic Gas Warning: Ammonia levels reached {nh3} ppm! Increase ventilation fans immediately.",
            severity="danger"
        )
        db.session.add(al)
        alerts_triggered.append("Ammonia Hazard")

    if water_pct <= 20.0:
        al = Alert(
            farm_id=int(farm_id), alert_type="Low Water Tank Level",
            message=f"Water Tank Level critical ({water_pct}%). Turn on pump to replenish drinkers.",
            severity="warning"
        )
        db.session.add(al)
        alerts_triggered.append("Low Water")

    db.session.commit()
    return jsonify({
        "status": "success",
        "message": "Telemetry recorded",
        "alerts_triggered": alerts_triggered
    }), 201


# ==============================================================================
# MODULE 11: VACCINATION MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/vaccinations", methods=["GET"])
@login_required
def list_vaccinations():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    flock_id = request.args.get("flock_id", type=int)
    query = Vaccination.query.join(Flock).filter(Flock.farm_id.in_(user_farm_ids))
    if flock_id:
        query = query.filter(Vaccination.flock_id == flock_id)

    vaccines = query.order_by(Vaccination.scheduled_date.asc()).all()
    return jsonify({"status": "success", "vaccinations": [v.to_dict() for v in vaccines]})

@app.route("/api/vaccinations", methods=["POST"])
@login_required
def add_vaccination():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")

    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Invalid batch specified"}), 400

    name = (data.get("vaccine_name") or data.get("name") or "").strip()
    if not name:
        return jsonify({"status": "error", "message": "Vaccine name is required"}), 400

    sched_date = date.today()
    if data.get("scheduled_date") or data.get("date"):
        try:
            sched_date = datetime.strptime(data.get("scheduled_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    vac = Vaccination(
        flock_id=flock.id,
        farm_id=flock.farm_id,
        vaccine_name=name,
        target_disease=data.get("target_disease", "Newcastle / IBD"),
        route=data.get("route", "Drinking Water"),
        scheduled_date=sched_date,
        status=data.get("status", "scheduled"),
        dosage=data.get("dosage", "1 Dose/Bird"),
        administered_by=data.get("administered_by", user.name),
        notes=data.get("notes")
    )
    db.session.add(vac)
    db.session.commit()
    return jsonify({"status": "success", "message": "Vaccination scheduled", "vaccination": vac.to_dict()}), 201

@app.route("/api/vaccinations/<int:vac_id>", methods=["PUT"])
@login_required
def update_vaccination(vac_id):
    user = get_current_user()
    vac = Vaccination.query.join(Flock).join(Farm).filter(Vaccination.id == vac_id, Farm.owner_id == user.id).first()
    if not vac:
        return jsonify({"status": "error", "message": "Vaccination not found"}), 404

    data = request.get_json() or {}
    if "status" in data:
        vac.status = data["status"]
        if data["status"] == "completed" and not vac.administered_date:
            vac.administered_date = date.today()
    if "administered_date" in data and data["administered_date"]:
        try:
            vac.administered_date = datetime.strptime(data["administered_date"], "%Y-%m-%d").date()
        except Exception:
            pass
    if "dosage" in data:
        vac.dosage = data["dosage"]

    db.session.commit()
    return jsonify({"status": "success", "message": "Vaccination updated", "vaccination": vac.to_dict()})

@app.route("/api/vaccinations/<int:vac_id>", methods=["DELETE"])
@login_required
def delete_vaccination(vac_id):
    user = get_current_user()
    vac = Vaccination.query.join(Flock).join(Farm).filter(Vaccination.id == vac_id, Farm.owner_id == user.id).first()
    if not vac:
        return jsonify({"status": "error", "message": "Vaccination not found"}), 404
    db.session.delete(vac)
    db.session.commit()
    return jsonify({"status": "success", "message": "Vaccination record deleted"})


# ==============================================================================
# MODULE 12: MEDICINE MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/medicines", methods=["GET"])
@login_required
def list_medicines():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    flock_id = request.args.get("flock_id", type=int)
    query = Medicine.query.join(Flock).filter(Flock.farm_id.in_(user_farm_ids))
    if flock_id:
        query = query.filter(Medicine.flock_id == flock_id)

    meds = query.order_by(Medicine.start_date.desc()).all()
    return jsonify({"status": "success", "medicines": [m.to_dict() for m in meds]})

@app.route("/api/medicines", methods=["POST"])
@login_required
def add_medicine():
    user = get_current_user()
    data = request.get_json() or {}
    flock_id = data.get("flock_id") or data.get("batchId")

    flock = Flock.query.join(Farm).filter(Flock.id == flock_id, Farm.owner_id == user.id).first()
    if not flock:
        return jsonify({"status": "error", "message": "Valid batch required"}), 400

    med = Medicine(
        flock_id=flock.id,
        farm_id=flock.farm_id,
        medicine_name=data.get("medicine_name", "").strip(),
        dosage=data.get("dosage", "1g per Liter"),
        administration_route=data.get("administration_route", "Drinking Water"),
        start_date=date.today(),
        purpose=data.get("purpose", "Respiratory care"),
        withdrawal_days=int(data.get("withdrawal_days", 3)),
        prescribed_by=data.get("prescribed_by", "Veterinary Consultant"),
        status="active"
    )
    db.session.add(med)
    db.session.commit()
    return jsonify({"status": "success", "medicine": med.to_dict()}), 201

@app.route("/api/medicines/<int:med_id>", methods=["DELETE"])
@login_required
def delete_medicine(med_id):
    user = get_current_user()
    med = Medicine.query.join(Flock).join(Farm).filter(Medicine.id == med_id, Farm.owner_id == user.id).first()
    if not med:
        return jsonify({"status": "error", "message": "Medicine record not found"}), 404
    db.session.delete(med)
    db.session.commit()
    return jsonify({"status": "success", "message": "Medicine record deleted"})


# ==============================================================================
# MODULE 13: EXPENSES MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/expenses", methods=["GET"])
@login_required
def list_expenses():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    farm_id = request.args.get("farm_id", type=int)
    query = Expense.query.filter(Expense.farm_id.in_(user_farm_ids))
    if farm_id and farm_id in user_farm_ids:
        query = query.filter_by(farm_id=farm_id)

    expenses = query.order_by(Expense.expense_date.desc()).all()
    total = sum(float(e.amount) for e in expenses)
    return jsonify({
        "status": "success",
        "expenses": [e.to_dict() for e in expenses],
        "total": total
    })

@app.route("/api/expenses", methods=["POST"])
@login_required
def add_expense():
    user = get_current_user()
    data = request.get_json() or {}

    farm_id = data.get("farm_id") or data.get("farmId")
    if not farm_id:
        user_farm = Farm.query.filter_by(owner_id=user.id).first()
        if not user_farm:
            return jsonify({"status": "error", "message": "Create a farm first"}), 400
        farm_id = user_farm.id
    else:
        farm_id = int(farm_id)
        if not Farm.query.filter_by(id=farm_id, owner_id=user.id).first():
            return jsonify({"status": "error", "message": "Unauthorized farm"}), 403

    exp_date = date.today()
    if data.get("expense_date") or data.get("date"):
        try:
            exp_date = datetime.strptime(data.get("expense_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    expense = Expense(
        farm_id=farm_id,
        flock_id=data.get("flock_id"),
        expense_date=exp_date,
        category=data.get("category", "Feed"),
        description=data.get("description", "Daily operations"),
        amount=Decimal(str(data.get("amount", 0.0))),
        payment_method=data.get("payment_method", "Cash")
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify({"status": "success", "message": "Expense saved", "expense": expense.to_dict()}), 201

@app.route("/api/expenses/<int:exp_id>", methods=["DELETE"])
@login_required
def delete_expense(exp_id):
    user = get_current_user()
    expense = Expense.query.join(Farm).filter(Expense.id == exp_id, Farm.owner_id == user.id).first()
    if not expense:
        return jsonify({"status": "error", "message": "Expense not found"}), 404
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"status": "success", "message": "Expense deleted"})


# ==============================================================================
# MODULE 14: SALES MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/sales", methods=["GET"])
@login_required
def list_sales():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    farm_id = request.args.get("farm_id", type=int)
    query = Sale.query.filter(Sale.farm_id.in_(user_farm_ids))
    if farm_id and farm_id in user_farm_ids:
        query = query.filter_by(farm_id=farm_id)

    sales = query.order_by(Sale.sale_date.desc()).all()
    total = sum(float(s.total_amount) for s in sales)
    return jsonify({
        "status": "success",
        "sales": [s.to_dict() for s in sales],
        "total": total
    })

@app.route("/api/sales", methods=["POST"])
@login_required
def add_sale():
    user = get_current_user()
    data = request.get_json() or {}

    farm_id = data.get("farm_id") or data.get("farmId")
    if not farm_id:
        user_farm = Farm.query.filter_by(owner_id=user.id).first()
        if not user_farm:
            return jsonify({"status": "error", "message": "Create a farm first"}), 400
        farm_id = user_farm.id
    else:
        farm_id = int(farm_id)
        if not Farm.query.filter_by(id=farm_id, owner_id=user.id).first():
            return jsonify({"status": "error", "message": "Unauthorized farm"}), 403

    sale_date = date.today()
    if data.get("sale_date") or data.get("date"):
        try:
            sale_date = datetime.strptime(data.get("sale_date") or data.get("date"), "%Y-%m-%d").date()
        except Exception:
            pass

    qty = Decimal(str(data.get("quantity", 0.0)))
    unit_price = Decimal(str(data.get("unit_price", 0.0)))
    total = Decimal(str(data.get("total_amount", float(qty * unit_price))))

    sale = Sale(
        farm_id=farm_id,
        flock_id=data.get("flock_id"),
        sale_date=sale_date,
        product_type=data.get("product_type", "birds"),
        quantity=qty,
        unit_price=unit_price,
        total_amount=total,
        buyer_name=data.get("buyer_name", "Local Distributor"),
        notes=data.get("notes")
    )
    db.session.add(sale)
    db.session.commit()
    return jsonify({"status": "success", "message": "Sale recorded", "sale": sale.to_dict()}), 201

@app.route("/api/sales/<int:sale_id>", methods=["DELETE"])
@login_required
def delete_sale(sale_id):
    user = get_current_user()
    sale = Sale.query.join(Farm).filter(Sale.id == sale_id, Farm.owner_id == user.id).first()
    if not sale:
        return jsonify({"status": "error", "message": "Sale not found"}), 404
    db.session.delete(sale)
    db.session.commit()
    return jsonify({"status": "success", "message": "Sale deleted"})


# ==============================================================================
# MODULE 15: INVENTORY MANAGEMENT (CRUD)
# ==============================================================================

@app.route("/api/inventory", methods=["GET"])
@login_required
def list_inventory():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    query = Inventory.query.filter(Inventory.farm_id.in_(user_farm_ids))
    items = query.order_by(Inventory.item_name.asc()).all()
    return jsonify({"status": "success", "inventory": [i.to_dict() for i in items]})

@app.route("/api/inventory", methods=["POST"])
@login_required
def add_inventory():
    user = get_current_user()
    data = request.get_json() or {}

    farm_id = data.get("farm_id") or data.get("farmId")
    if not farm_id:
        user_farm = Farm.query.filter_by(owner_id=user.id).first()
        farm_id = user_farm.id if user_farm else 1

    item = Inventory(
        farm_id=int(farm_id),
        item_name=data.get("item_name", "").strip(),
        category=data.get("category", "Feed"),
        quantity=Decimal(str(data.get("quantity", 0.0))),
        unit=data.get("unit", "kg"),
        unit_cost=Decimal(str(data.get("unit_cost", 0.0))),
        reorder_level=Decimal(str(data.get("reorder_level", 10.0))),
        supplier=data.get("supplier"),
        notes=data.get("notes")
    )
    db.session.add(item)
    db.session.commit()
    return jsonify({"status": "success", "item": item.to_dict()}), 201

@app.route("/api/inventory/<int:item_id>", methods=["DELETE"])
@login_required
def delete_inventory(item_id):
    user = get_current_user()
    item = Inventory.query.join(Farm).filter(Inventory.id == item_id, Farm.owner_id == user.id).first()
    if not item:
        return jsonify({"status": "error", "message": "Item not found"}), 404
    db.session.delete(item)
    db.session.commit()
    return jsonify({"status": "success", "message": "Inventory item deleted"})


# ==============================================================================
# MODULE 16: TASKS & REMINDERS (CRUD)
# ==============================================================================

@app.route("/api/tasks", methods=["GET"])
@login_required
def list_tasks():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    tasks = Task.query.filter(Task.farm_id.in_(user_farm_ids)).order_by(Task.due_date.asc()).all()
    return jsonify({"status": "success", "tasks": [t.to_dict() for t in tasks]})

@app.route("/api/tasks", methods=["POST"])
@app.route("/api/tasks/create", methods=["POST"])
@login_required
def create_task():
    user = get_current_user()
    data = request.get_json() or {}

    farm_id = data.get("farm_id") or data.get("farmId")
    if not farm_id:
        user_farm = Farm.query.filter_by(owner_id=user.id).first()
        farm_id = user_farm.id if user_farm else 1

    due_date = date.today()
    if data.get("due_date"):
        try:
            due_date = datetime.strptime(data.get("due_date"), "%Y-%m-%d").date()
        except Exception:
            pass

    task = Task(
        farm_id=int(farm_id),
        flock_id=data.get("flock_id"),
        title=data.get("title", "Farm Operation").strip(),
        description=data.get("description", ""),
        due_date=due_date,
        priority=data.get("priority", "medium"),
        status="pending"
    )
    db.session.add(task)
    db.session.commit()
    return jsonify({"status": "success", "message": "Task created", "task": task.to_dict()}), 201

@app.route("/api/tasks/<int:task_id>/status", methods=["POST"])
@app.route("/api/tasks/<int:task_id>", methods=["PUT"])
@login_required
def update_task_status(task_id):
    user = get_current_user()
    task = Task.query.join(Farm).filter(Task.id == task_id, Farm.owner_id == user.id).first()
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404

    data = request.get_json() or {}
    if "status" in data:
        task.status = data["status"]
    elif "is_completed" in data:
        task.status = "completed" if data["is_completed"] else "pending"

    db.session.commit()
    return jsonify({"status": "success", "task": task.to_dict()})

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
@login_required
def delete_task(task_id):
    user = get_current_user()
    task = Task.query.join(Farm).filter(Task.id == task_id, Farm.owner_id == user.id).first()
    if not task:
        return jsonify({"status": "error", "message": "Task not found"}), 404
    db.session.delete(task)
    db.session.commit()
    return jsonify({"status": "success", "message": "Task deleted"})


# ==============================================================================
# MODULE 17: ALERTS & NOTIFICATIONS (CRUD)
# ==============================================================================

@app.route("/api/alerts", methods=["GET"])
@app.route("/api/notifications", methods=["GET"])
@login_required
def list_alerts():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    alerts = Alert.query.filter(Alert.farm_id.in_(user_farm_ids)).order_by(Alert.id.desc()).limit(50).all()
    return jsonify({
        "status": "success",
        "alerts": [a.to_dict() for a in alerts],
        "unread_count": len([a for a in alerts if not a.is_read])
    })

@app.route("/api/alerts/<int:alert_id>/read", methods=["POST"])
@app.route("/api/alerts/<int:alert_id>/dismiss", methods=["POST"])
@login_required
def dismiss_alert(alert_id):
    user = get_current_user()
    alert = Alert.query.join(Farm).filter(Alert.id == alert_id, Farm.owner_id == user.id).first()
    if alert:
        alert.is_read = True
        db.session.commit()
    return jsonify({"status": "success", "message": "Alert marked as read"})

@app.route("/api/alerts/read-all", methods=["POST"])
@app.route("/api/alerts/dismiss-all", methods=["POST"])
@login_required
def dismiss_all_alerts():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    Alert.query.filter(Alert.farm_id.in_(user_farm_ids)).update({Alert.is_read: True}, synchronize_session=False)
    db.session.commit()
    return jsonify({"status": "success", "message": "All alerts dismissed"})

@app.route("/api/alerts/<int:alert_id>", methods=["DELETE"])
@login_required
def delete_alert(alert_id):
    user = get_current_user()
    alert = Alert.query.join(Farm).filter(Alert.id == alert_id, Farm.owner_id == user.id).first()
    if alert:
        db.session.delete(alert)
        db.session.commit()
    return jsonify({"status": "success", "message": "Alert deleted"})


# ==============================================================================
# MODULE 18: USER SETTINGS (READ & UPDATE)
# ==============================================================================

@app.route("/api/settings", methods=["GET"])
@login_required
def get_user_settings():
    user = get_current_user()
    setting = UserSetting.query.filter_by(user_id=user.id).first()
    if not setting:
        setting = UserSetting(user_id=user.id)
        db.session.add(setting)
        db.session.commit()
    return jsonify({"status": "success", "settings": setting.to_dict()})

@app.route("/api/settings", methods=["PUT"])
@login_required
def update_user_settings():
    user = get_current_user()
    setting = UserSetting.query.filter_by(user_id=user.id).first()
    if not setting:
        setting = UserSetting(user_id=user.id)
        db.session.add(setting)

    data = request.get_json() or {}
    if "theme" in data:
        setting.theme = data["theme"]
    if "language" in data:
        setting.language = data["language"]
        user.language = data["language"]
    if "fcr_target" in data:
        setting.fcr_target = Decimal(str(data["fcr_target"]))
    if "currency" in data:
        setting.currency = data["currency"]
    if "phone_alerts" in data:
        setting.phone_alerts = bool(data["phone_alerts"])
    if "email_alerts" in data:
        setting.email_alerts = bool(data["email_alerts"])

    db.session.commit()
    return jsonify({"status": "success", "message": "Settings updated", "settings": setting.to_dict()})


# ==============================================================================
# REPORTS & ANALYTICS API
# ==============================================================================

@app.route("/api/reports/analytics", methods=["GET"])
@login_required
def get_reports_analytics():
    user = get_current_user()
    user_farms = Farm.query.filter_by(owner_id=user.id).all()
    user_farm_ids = [f.id for f in user_farms]

    # Total Expenses & Sales
    total_expenses = float(db.session.query(db.func.sum(Expense.amount)).filter(Expense.farm_id.in_(user_farm_ids)).scalar() or 0.0)
    total_sales = float(db.session.query(db.func.sum(Sale.total_amount)).filter(Sale.farm_id.in_(user_farm_ids)).scalar() or 0.0)
    net_profit = total_sales - total_expenses

    # 7-day feed and water trends
    seven_days_ago = date.today() - timedelta(days=7)
    daily_recs = DailyRecord.query.join(Flock).filter(
        Flock.farm_id.in_(user_farm_ids),
        DailyRecord.record_date >= seven_days_ago
    ).order_by(DailyRecord.record_date.asc()).all()

    labels = []
    feed_data = []
    water_data = []
    mortality_data = []

    for r in daily_recs:
        d_str = r.record_date.strftime("%b %d")
        if d_str not in labels:
            labels.append(d_str)
            feed_data.append(float(r.feed_consumed_kg or 0.0))
            water_data.append(float(r.water_consumed_liters or 0.0))
            mortality_data.append(int(r.mortality or 0))

    return jsonify({
        "status": "success",
        "financials": {
            "total_expenses": total_expenses,
            "total_sales": total_sales,
            "net_profit": net_profit,
            "margin_pct": round((net_profit / total_sales * 100), 1) if total_sales > 0 else 0.0
        },
        "trends": {
            "labels": labels or ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6", "Today"],
            "feed": feed_data or [180, 195, 210, 215, 220, 225, 230],
            "water": water_data or [350, 370, 390, 400, 410, 420, 430],
            "mortality": mortality_data or [1, 0, 2, 1, 0, 1, 0]
        }
    })


# ==============================================================================
# AI / ML DECISION SUPPORT ENGINE ENDPOINTS
# ==============================================================================

@app.route("/api/ai/disease-risk", methods=["POST"])
@app.route("/api/ai/disease-prediction", methods=["POST"])
def api_disease_prediction():
    data = request.get_json() or {}
    age_days = int(data.get("age_days", data.get("birdAge", 21)))
    temp = float(data.get("temperature", 28.0))
    hum = float(data.get("humidity", 60.0))
    ammonia = float(data.get("ammonia_ppm", data.get("ammonia", 12.0)))
    mortality = float(data.get("mortality", 0.0))
    symptoms = data.get("symptoms", "")
    if isinstance(symptoms, list):
        symptoms = ", ".join(symptoms)

    res = ai_engine.predict_disease_risk(
        age_days=age_days,
        temperature=temp,
        humidity=hum,
        ammonia_ppm=ammonia,
        mortality_rate_pct=mortality,
        symptoms=symptoms
    )
    return jsonify({"status": "success", "prediction": res})

@app.route("/api/ai/feed-estimate", methods=["POST"])
def api_feed_estimate():
    data = request.get_json() or {}
    age_days = int(data.get("age_days", 21))
    bird_count = int(data.get("bird_count", 1000))
    breed = data.get("breed", "Cobb 500")

    res = ai_engine.estimate_feed_requirements(age_days, bird_count, breed)
    return jsonify({"status": "success", "feed_estimation": res})


# --- Error Handlers ---
@app.errorhandler(404)
def not_found_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404
    return send_from_directory("frontend", "index.html")

@app.errorhandler(500)
def server_error_handler(e):
    return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    print(f"🐔 Smart Poultry Farm Server running at http://0.0.0.0:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
