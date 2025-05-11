-- Users Table: Stores all system users (drivers, mechanics, regulators, analysts)
CREATE TABLE users (
    user_id        UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    full_name      VARCHAR(255) NOT NULL,
    email          VARCHAR(255) UNIQUE NOT NULL,
    phone_number   VARCHAR(20) UNIQUE NOT NULL,
    user_type      ENUM('driver', 'mechanic', 'regulator', 'analyst') NOT NULL,
    password_hash  TEXT NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vehicles Table: Each vehicle is uniquely identified by the Veepeak OBD-II dongle ID
CREATE TABLE vehicles (
    vehicle_id   VARCHAR(50) PRIMARY KEY,
    driver_id    UUID UNIQUE NOT NULL,
    make         VARCHAR(100) NOT NULL,
    model        VARCHAR(100) NOT NULL,
    year         INT CHECK (year > 1900 AND year <= EXTRACT(YEAR FROM CURRENT_DATE)),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (driver_id) REFERENCES users(user_id) ON DELETE CASCADE
);

-- Mechanics’ Access Requests: Mechanics must request and receive approval from the driver
CREATE TABLE mechanic_requests (
    request_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    mechanic_id   UUID NOT NULL,
    vehicle_id    VARCHAR(50) NOT NULL,
    status        ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    requested_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at   TIMESTAMP,
    FOREIGN KEY (mechanic_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE,
    UNIQUE (mechanic_id, vehicle_id)
);

-- Emissions Data: Collected from the OBD-II device in real-time
CREATE TABLE emissions_data (
    data_id       UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id    VARCHAR(50) NOT NULL,
    timestamp     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    co2_level     FLOAT CHECK (co2_level >= 0),
    nox_level     FLOAT CHECK (nox_level >= 0),
    hc_level      FLOAT CHECK (hc_level >= 0),
    engine_load   FLOAT CHECK (engine_load >= 0 AND engine_load <= 100),
    fuel_rate     FLOAT CHECK (fuel_rate >= 0),
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- Compliance Reports: Generated for regulatory bodies to assess emissions compliance
CREATE TABLE compliance_reports (
    report_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id   VARCHAR(50) NOT NULL,
    report_date  DATE DEFAULT CURRENT_DATE,
    status       ENUM('compliant', 'non-compliant') NOT NULL,
    comments     TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- Anomaly Detection Logs: Logs AI-detected anomalies in emissions behavior
CREATE TABLE anomaly_logs (
    anomaly_id   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    vehicle_id   VARCHAR(50) NOT NULL,
    detected_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    issue        TEXT NOT NULL,
    severity     ENUM('low', 'medium', 'high', 'critical') NOT NULL,
    FOREIGN KEY (vehicle_id) REFERENCES vehicles(vehicle_id) ON DELETE CASCADE
);

-- Aggregated Analytics: Stores anonymized, aggregated emissions data for research
CREATE TABLE emissions_analytics (
    record_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    region       VARCHAR(100) NOT NULL,
    avg_co2      FLOAT CHECK (avg_co2 >= 0),
    avg_nox      FLOAT CHECK (avg_nox >= 0),
    avg_hc       FLOAT CHECK (avg_hc >= 0),
    sample_size  INT CHECK (sample_size > 0),
    report_date  DATE DEFAULT CURRENT_DATE
);

-- Indexes for optimizing queries
CREATE INDEX idx_emissions_vehicle ON emissions_data(vehicle_id);
CREATE INDEX idx_compliance_vehicle ON compliance_reports(vehicle_id);
CREATE INDEX idx_anomalies_vehicle ON anomaly_logs(vehicle_id);
