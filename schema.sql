-- ==============================================================================
-- SMART POULTRY PRECISION FARM MANAGEMENT SYSTEM
-- Target Database: MySQL 8.0+
-- Database Name: smart_poultry
-- Complete 18 Relational Tables + Triggers + Indexes
-- ==============================================================================

CREATE DATABASE IF NOT EXISTS smart_poultry
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_poultry;

-- Drop existing triggers to allow idempotent execution
DROP TRIGGER IF EXISTS trg_daily_records_after_insert;
DROP TRIGGER IF EXISTS trg_daily_records_after_update;
DROP TRIGGER IF EXISTS trg_mortality_after_insert;

-- ------------------------------------------------------------------------------
-- 1. Table: users
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NULL UNIQUE,
    phone VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('farmer', 'veterinarian', 'admin') NOT NULL DEFAULT 'farmer',
    mobile_verified BOOLEAN NOT NULL DEFAULT TRUE,
    account_status ENUM('pending', 'active', 'suspended') NOT NULL DEFAULT 'active',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    specialization VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_users_phone (phone),
    INDEX idx_users_email (email),
    INDEX idx_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 2. Table: farms
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS farms (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT NOT NULL,
    farm_name VARCHAR(150) NOT NULL,
    location VARCHAR(255) NULL,
    address TEXT NULL,
    total_capacity INT NOT NULL DEFAULT 5000,
    farm_type VARCHAR(50) NOT NULL DEFAULT 'Broiler',
    farm_size VARCHAR(100) NULL DEFAULT '2 Acres',
    established_date DATE NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_farms_owner FOREIGN KEY (owner_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT chk_farms_capacity CHECK (total_capacity >= 0),
    INDEX idx_farms_owner (owner_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 3. Table: flocks
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS flocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    batch_number VARCHAR(100) NOT NULL,
    bird_type VARCHAR(100) NOT NULL DEFAULT 'Broiler',
    breed VARCHAR(100) NOT NULL DEFAULT 'Cobb 500',
    initial_bird_count INT NOT NULL DEFAULT 1000,
    current_bird_count INT NOT NULL DEFAULT 1000,
    arrival_date DATE NOT NULL,
    expected_sale_date DATE NULL,
    target_weight_kg DECIMAL(6, 2) NOT NULL DEFAULT 2.00,
    status ENUM('active', 'sold', 'closed') NOT NULL DEFAULT 'active',
    health_status VARCHAR(50) NOT NULL DEFAULT 'Good',
    risk_level VARCHAR(20) NOT NULL DEFAULT 'Low',
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_flocks_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT uq_farm_batch UNIQUE (farm_id, batch_number),
    CONSTRAINT chk_initial_bird_count CHECK (initial_bird_count >= 0),
    CONSTRAINT chk_current_bird_count CHECK (current_bird_count >= 0),
    INDEX idx_flocks_farm_status (farm_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 4. Table: birds
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS birds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    tag_number VARCHAR(50) NULL,
    shed_name VARCHAR(100) NOT NULL DEFAULT 'Shed 1',
    cage_or_pen VARCHAR(100) NULL,
    current_weight_kg DECIMAL(6, 3) NOT NULL DEFAULT 0.000,
    health_status VARCHAR(50) NOT NULL DEFAULT 'Healthy',
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_birds_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    INDEX idx_birds_flock (flock_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 5. Table: feed_records
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS feed_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    farm_id INT NULL,
    record_date DATE NOT NULL,
    feed_type VARCHAR(100) NOT NULL DEFAULT 'Broiler Starter',
    quantity_kg DECIMAL(8, 2) NOT NULL,
    unit_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_cost DECIMAL(12, 2) NOT NULL DEFAULT 0.00,
    supplier VARCHAR(150) NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feed_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT fk_feed_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT chk_feed_qty CHECK (quantity_kg >= 0),
    CONSTRAINT chk_feed_cost CHECK (total_cost >= 0),
    INDEX idx_feed_flock_date (flock_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 6. Table: water_records
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS water_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    farm_id INT NULL,
    record_date DATE NOT NULL,
    quantity_liters DECIMAL(8, 2) NOT NULL,
    water_source VARCHAR(100) NULL DEFAULT 'Borewell',
    temperature_celsius DECIMAL(5, 2) NULL,
    ph_level DECIMAL(4, 2) NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_water_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT fk_water_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT chk_water_qty CHECK (quantity_liters >= 0),
    INDEX idx_water_flock_date (flock_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 7. Table: egg_records
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS egg_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    farm_id INT NULL,
    record_date DATE NOT NULL,
    eggs_produced INT NOT NULL DEFAULT 0,
    eggs_sold INT NOT NULL DEFAULT 0,
    damaged_eggs INT NOT NULL DEFAULT 0,
    selling_price_per_egg DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_egg_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT fk_egg_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT chk_egg_prod CHECK (eggs_produced >= 0),
    CONSTRAINT chk_egg_sold CHECK (eggs_sold >= 0),
    CONSTRAINT chk_egg_dam CHECK (damaged_eggs >= 0),
    INDEX idx_egg_flock_date (flock_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 8. Table: mortality_records
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS mortality_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    farm_id INT NULL,
    record_date DATE NOT NULL,
    mortality_count INT NOT NULL DEFAULT 1,
    culls_count INT NOT NULL DEFAULT 0,
    suspected_cause VARCHAR(255) NULL DEFAULT 'Natural / Unknown',
    symptoms TEXT NULL,
    disposal_method VARCHAR(100) NULL DEFAULT 'Composting',
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_mort_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT fk_mort_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT chk_mort_cnt CHECK (mortality_count >= 0),
    CONSTRAINT chk_culls_cnt CHECK (culls_count >= 0),
    INDEX idx_mortality_flock_date (flock_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 9. Table: weight_records
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS weight_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    farm_id INT NULL,
    record_date DATE NOT NULL,
    sample_size INT NOT NULL DEFAULT 10,
    average_weight_kg DECIMAL(6, 3) NOT NULL,
    target_weight_kg DECIMAL(6, 3) NOT NULL DEFAULT 2.000,
    uniformity_percentage DECIMAL(5, 2) NULL DEFAULT 85.00,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_weight_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT fk_weight_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT chk_weight_sample CHECK (sample_size > 0),
    CONSTRAINT chk_weight_avg CHECK (average_weight_kg >= 0),
    INDEX idx_weight_flock_date (flock_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 10. Table: environment_records
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS environment_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    flock_id INT NULL,
    recorded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    temperature_celsius DECIMAL(5, 2) NOT NULL,
    humidity_percentage DECIMAL(5, 2) NOT NULL,
    ammonia_ppm DECIMAL(5, 2) NOT NULL DEFAULT 0.00,
    water_level_pct DECIMAL(5, 2) NULL DEFAULT 100.00,
    feed_level_pct DECIMAL(5, 2) NULL DEFAULT 100.00,
    source VARCHAR(50) NOT NULL DEFAULT 'IoT_Sensor',
    notes TEXT NULL,
    CONSTRAINT fk_env_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT fk_env_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL,
    CONSTRAINT chk_env_humidity CHECK (humidity_percentage >= 0.00 AND humidity_percentage <= 100.00),
    CONSTRAINT chk_env_ammonia CHECK (ammonia_ppm >= 0.00),
    INDEX idx_env_farm_time (farm_id, recorded_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 11. Table: vaccinations
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS vaccinations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    farm_id INT NULL,
    vaccine_name VARCHAR(150) NOT NULL,
    target_disease VARCHAR(150) NULL,
    route VARCHAR(100) NOT NULL DEFAULT 'Drinking Water',
    scheduled_date DATE NOT NULL,
    administered_date DATE NULL,
    status ENUM('scheduled', 'completed', 'overdue', 'cancelled') NOT NULL DEFAULT 'scheduled',
    dosage VARCHAR(100) NULL,
    administered_by VARCHAR(150) NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_vac_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT fk_vac_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    INDEX idx_vac_flock_date (flock_id, scheduled_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 12. Table: medicines
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS medicines (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    farm_id INT NULL,
    medicine_name VARCHAR(150) NOT NULL,
    dosage VARCHAR(100) NOT NULL,
    administration_route VARCHAR(100) NOT NULL DEFAULT 'Drinking Water',
    start_date DATE NOT NULL,
    end_date DATE NULL,
    purpose VARCHAR(255) NULL,
    withdrawal_days INT NOT NULL DEFAULT 0,
    prescribed_by VARCHAR(150) NULL,
    status ENUM('active', 'completed') NOT NULL DEFAULT 'active',
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_med_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT fk_med_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    INDEX idx_med_flock (flock_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 13. Table: expenses
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    flock_id INT NULL,
    expense_date DATE NOT NULL,
    category VARCHAR(100) NOT NULL,
    description VARCHAR(255) NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_method VARCHAR(50) NOT NULL DEFAULT 'Cash',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_expense_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT fk_expense_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL,
    CONSTRAINT chk_expense_amount CHECK (amount >= 0.00),
    INDEX idx_expense_farm_date (farm_id, expense_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 14. Table: sales
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sales (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    flock_id INT NULL,
    sale_date DATE NOT NULL,
    product_type VARCHAR(50) NOT NULL DEFAULT 'birds',
    quantity DECIMAL(10, 2) NOT NULL,
    unit_price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    total_amount DECIMAL(12, 2) NOT NULL,
    buyer_name VARCHAR(150) NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_sales_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT fk_sales_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL,
    CONSTRAINT chk_sales_qty CHECK (quantity >= 0.00),
    CONSTRAINT chk_sales_amount CHECK (total_amount >= 0.00),
    INDEX idx_sales_farm_date (farm_id, sale_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 15. Table: inventory
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    item_name VARCHAR(150) NOT NULL,
    category VARCHAR(100) NOT NULL,
    quantity DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    unit VARCHAR(50) NOT NULL DEFAULT 'kg',
    unit_cost DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    reorder_level DECIMAL(10, 2) NOT NULL DEFAULT 10.00,
    supplier VARCHAR(150) NULL,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_inventory_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT chk_inventory_qty CHECK (quantity >= 0.00),
    INDEX idx_inventory_farm (farm_id, category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 16. Table: tasks
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    flock_id INT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT NULL,
    due_date DATE NOT NULL,
    status ENUM('pending', 'in_progress', 'completed', 'cancelled') NOT NULL DEFAULT 'pending',
    priority ENUM('low', 'medium', 'high', 'urgent') NOT NULL DEFAULT 'medium',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_tasks_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT fk_tasks_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL,
    INDEX idx_tasks_farm_status (farm_id, status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 17. Table: notifications
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    farm_id INT NULL,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    severity VARCHAR(50) NOT NULL DEFAULT 'info',
    notification_type VARCHAR(100) NOT NULL DEFAULT 'system',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    link VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notif_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    CONSTRAINT fk_notif_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    INDEX idx_notif_user_unread (user_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- 18. Table: user_settings
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user_settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    theme VARCHAR(20) NOT NULL DEFAULT 'light',
    language VARCHAR(10) NOT NULL DEFAULT 'en',
    fcr_target DECIMAL(4, 2) NOT NULL DEFAULT 1.60,
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    phone_alerts BOOLEAN NOT NULL DEFAULT TRUE,
    email_alerts BOOLEAN NOT NULL DEFAULT TRUE,
    auto_refresh_seconds INT NOT NULL DEFAULT 30,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_settings_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Supplementary Table: daily_records
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS daily_records (
    id INT AUTO_INCREMENT PRIMARY KEY,
    flock_id INT NOT NULL,
    record_date DATE NOT NULL,
    opening_birds INT NOT NULL DEFAULT 0,
    mortality INT NOT NULL DEFAULT 0,
    culls INT NOT NULL DEFAULT 0,
    closing_birds INT NOT NULL DEFAULT 0,
    average_weight_kg DECIMAL(6, 3) NOT NULL DEFAULT 0.000,
    feed_consumed_kg DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    water_consumed_liters DECIMAL(8, 2) NOT NULL DEFAULT 0.00,
    eggs_produced INT NOT NULL DEFAULT 0,
    notes TEXT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_daily_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE CASCADE,
    CONSTRAINT uq_flock_record_date UNIQUE (flock_id, record_date),
    INDEX idx_daily_flock_date (flock_id, record_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Supplementary Table: alerts
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    farm_id INT NOT NULL,
    flock_id INT NULL,
    alert_type VARCHAR(100) NOT NULL,
    message TEXT NOT NULL,
    severity ENUM('info', 'warning', 'danger', 'critical') NOT NULL DEFAULT 'warning',
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_alerts_farm FOREIGN KEY (farm_id) REFERENCES farms(id) ON DELETE CASCADE,
    CONSTRAINT fk_alerts_flock FOREIGN KEY (flock_id) REFERENCES flocks(id) ON DELETE SET NULL,
    INDEX idx_alerts_farm_unread (farm_id, is_read)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- Supplementary Table: otp_verifications
-- ------------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS otp_verifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    otp_hash VARCHAR(255) NOT NULL,
    expires_at DATETIME NOT NULL,
    attempts INT NOT NULL DEFAULT 0,
    is_used BOOLEAN NOT NULL DEFAULT FALSE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_otp_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_otp_user_lookup (user_id, is_used, expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ------------------------------------------------------------------------------
-- TRIGGERS
-- ------------------------------------------------------------------------------
DELIMITER //

CREATE TRIGGER trg_daily_records_after_insert
AFTER INSERT ON daily_records
FOR EACH ROW
BEGIN
    UPDATE flocks
    SET current_bird_count = GREATEST(0, NEW.closing_birds)
    WHERE id = NEW.flock_id;
END;
//

CREATE TRIGGER trg_daily_records_after_update
AFTER UPDATE ON daily_records
FOR EACH ROW
BEGIN
    UPDATE flocks
    SET current_bird_count = GREATEST(0, NEW.closing_birds)
    WHERE id = NEW.flock_id;
END;
//

CREATE TRIGGER trg_mortality_after_insert
AFTER INSERT ON mortality_records
FOR EACH ROW
BEGIN
    UPDATE flocks
    SET current_bird_count = GREATEST(0, current_bird_count - (NEW.mortality_count + NEW.culls_count))
    WHERE id = NEW.flock_id;
END;
//

DELIMITER ;
