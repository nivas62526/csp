# 🐔 Smart Poultry Farm Management and Monitoring System

A complete full-stack, multi-tenant agricultural IoT and AI precision management web application for commercial and domestic poultry farms. Accessible seamlessly across **Desktop, Laptop, Android phones, and iPhones** through a single unified URL.

---

## 🌟 System Architecture & Capabilities

### 1. Technology Stack
- **Backend**: Python 3.8+ / Flask 3.1, Flask-SQLAlchemy, Flask-JWT-Extended, Flask-Cors, Gunicorn
- **Frontend**: Responsive Bootstrap 5, Bootstrap Icons, Chart.js, HTML5/CSS3/Vanilla JS (No build step required; lightweight and ultra-fast on mobile devices)
- **Database**: MySQL 8.0+ (Production cloud database), with automatic SQLite fallback for local testing
- **Authentication**: Secure Mobile Number & Password authentication using PBKDF2/SHA-256 password hashing and JWT token authorization (**No OTP required**)
- **Data Privacy**: Multi-tenant architecture ensuring **strict user data isolation** (User A never sees or modifies User B's farms, flocks, feed, eggs, or finances)

---

## 📊 Complete 18 Core Relational Database Modules

| # | Table / Module | Description | CRUD Status |
|---|----------------|-------------|-------------|
| 1 | **Users** (`users`) | Farmer accounts with mobile, email, password hash, role | Full Support |
| 2 | **Farms** (`farms`) | Poultry facilities, location, housing capacity, sheds | Full Support |
| 3 | **Flocks / Batches** (`flocks`) | Batches (Broiler, Layer, Cobb 500), age, counts | Full Support |
| 4 | **Birds** (`birds`) | Individual / shed-level tagging, weight, health status | Full Support |
| 5 | **Feed Records** (`feed_records`) | Feed consumption (kg), feed types, supplier, costs | Full Support |
| 6 | **Water Records** (`water_records`) | Daily water consumption (Liters), pH, water source | Full Support |
| 7 | **Egg Production** (`egg_records`) | Eggs collected, sold, damaged, and price per egg | Full Support |
| 8 | **Mortality Tracking** (`mortality_records`) | Bird mortality & culls with auto-deduction from flock | Full Support |
| 9 | **Weight Records** (`weight_records`) | Sample bird weights, average weight, uniformity % | Full Support |
| 10 | **Environment Records** (`environment_records`) | Real-time IoT temperature, humidity, ammonia, water level | Full Support |
| 11 | **Vaccinations** (`vaccinations`) | Vaccination schedules (LaSota, Gumboro, Marek's), status | Full Support |
| 12 | **Medicines** (`medicines`) | Antibiotics & supplements, dosages, withdrawal days | Full Support |
| 13 | **Expenses** (`expenses`) | Categorized operational costs (Chicks, Feed, Power, Labor) | Full Support |
| 14 | **Sales** (`sales`) | Revenue logs (Broilers, Layers, Eggs, Manure, Culled) | Full Support |
| 15 | **Inventory** (`inventory`) | Feed bags, medications, equipment, reorder alerts | Full Support |
| 16 | **Tasks & Reminders** (`tasks`) | Farm chores, due dates, priority, completion toggles | Full Support |
| 17 | **Notifications & Alerts** (`alerts`, `notifications`) | IoT threshold triggers, mortality spike alarms | Full Support |
| 18 | **User Settings** (`user_settings`) | Language (English/Telugu), currency, target FCR, alerts | Full Support |

---

## 🚀 Local Development Setup

### 1. Prerequisites
- Python 3.8+ installed (tested on Python 3.11)
- Git installed (optional)

### 2. Quick Launch
Run the automated Windows batch script:
```cmd
start.bat
```
Or run directly via command line:
```bash
# 1. Initialize schema and tables
python -c "from app import app, db; ctx = app.app_context(); ctx.push(); db.create_all(); print('Database Ready!')"

# 2. Start Flask server
python app.py
```
Open your browser at: **`http://localhost:5000`**

### 3. Running Automated Tests
To verify user registration without OTP, login, multi-tenant isolation, and CRUD operations across all 18 modules:
```bash
python test_full_system.py
```

---

## 🌐 Production Cloud Deployment Guide

Follow these steps to deploy your Smart Poultry Farm system online so your father and colleagues can access it from their laptops, iPhones, and Android phones using one public link.

---

### Step 1: Upload Project to GitHub

1. Open a terminal in `D:\csp`:
   ```bash
   git init
   git add .
   git commit -m "Complete Smart Poultry Farm System full-stack release"
   ```
2. Create a new repository on [GitHub](https://github.com/new) named `smart-poultry-farm`.
3. Push your repository:
   ```bash
   git remote add origin https://github.com/YOUR_GITHUB_USERNAME/smart-poultry-farm.git
   git branch -M main
   git push -u origin main
   ```

---

### Step 2: Create Free Cloud-Hosted MySQL Database

You can use any cloud MySQL provider (such as **Aiven**, **Railway**, or **Clever Cloud**):

#### Using Aiven for MySQL (Recommended - Free Tier):
1. Sign up at [Aiven.io](https://aiven.io/).
2. Click **Create Service** &rarr; Select **MySQL**.
3. Choose the **Free Plan** &rarr; Select the region closest to you &rarr; Click **Create Service**.
4. Once running, copy the **Service URI** from the Aiven overview panel:
   `mysql://avnadmin:YOUR_PASSWORD@your-mysql-host.aivencloud.com:PORT/defaultdb?ssl-mode=REQUIRED`
5. You can create database `smart_poultry` or use the default database.

---

### Step 3: Deploy Flask Backend to Render

1. Sign up at [Render.com](https://render.com/).
2. Click **New +** &rarr; Select **Web Service**.
3. Connect your GitHub repository `smart-poultry-farm`.
4. Configure the settings:
   - **Name**: `smart-poultry-app`
   - **Region**: Oregon or Singapore
   - **Branch**: `main`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`
   - **Instance Type**: `Free`
5. Under **Environment Variables**, add:
   - `FLASK_DEBUG`: `False`
   - `SECRET_KEY`: `(click generate or paste a random 32-character string)`
   - `JWT_SECRET_KEY`: `(click generate or paste a random string)`
   - `DATABASE_URL`: `mysql+pymysql://avnadmin:YOUR_PASSWORD@your-mysql-host.aivencloud.com:PORT/smart_poultry`
     *(Note: Ensure prefix is `mysql+pymysql://`)*
6. Click **Deploy Web Service**.
7. Render will build and deploy your app. You will receive a public URL such as:
   `https://smart-poultry-app.onrender.com`

---

### Step 4: Accessing the Live Application

Because Flask serves the modern, mobile-responsive frontend directly from `/frontend`:
- **Desktop/Laptop View**: `https://smart-poultry-app.onrender.com/dashboard.html`
- **Mobile View**: `https://smart-poultry-app.onrender.com/` (or `/login.html`)
- **Direct Login**: `https://smart-poultry-app.onrender.com/login.html`
- **Direct Register**: `https://smart-poultry-app.onrender.com/register.html`

Both desktop and mobile devices connect to the exact same cloud database in real time!

---

### Optional Step 5: Hosting Frontend Separately on Vercel

If you prefer hosting the static frontend on Vercel:
1. Sign up at [Vercel.com](https://vercel.com/).
2. Import your GitHub repository `smart-poultry-farm`.
3. In `frontend/assets/js/api.js`, set:
   ```javascript
   window.API_BASE_URL = "https://smart-poultry-app.onrender.com";
   ```
4. Click **Deploy**. Vercel will host your static frontend, and all REST API calls will communicate securely with your Render Flask backend.

---

## 🔒 Security Features
- **PBKDF2 Password Hashing**: Passwords are never stored in plaintext.
- **JWT Authentication**: Industry-standard JSON Web Tokens for stateless API access.
- **SQL Injection Prevention**: SQLAlchemy parameterized queries protect every query.
- **Multi-Tenant Ownership Verification**: Every API verifies that the requested entity belongs to the logged-in user.
- **CORS Protection**: Secure origin control enabled.
