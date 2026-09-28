-- =============================================================================
-- Telecom Customer Churn - Database DDL Script
-- Target Database: MariaDB / MySQL
-- Table: customer_churn
-- =============================================================================

CREATE DATABASE IF NOT EXISTS telecom_db;
USE telecom_db;

DROP TABLE IF EXISTS customer_churn;

CREATE TABLE customer_churn (
    customer_id         VARCHAR(50)     NOT NULL,
    gender              VARCHAR(20),
    senior_citizen      TINYINT(1),
    has_partner         VARCHAR(10),
    has_dependents      VARCHAR(10),
    tenure_months       INT,
    phone_service       VARCHAR(10),
    multiple_lines      VARCHAR(30),
    internet_service    VARCHAR(30),
    online_security     VARCHAR(30),
    online_backup       VARCHAR(30),
    device_protection   VARCHAR(30),
    tech_support        VARCHAR(30),
    streaming_tv        VARCHAR(30),
    streaming_movies    VARCHAR(30),
    contract_type       VARCHAR(30),
    paperless_billing   VARCHAR(10),
    payment_method      VARCHAR(50),
    monthly_charges     DECIMAL(10, 2),
    total_charges       DECIMAL(10, 2),
    churn_flag          VARCHAR(10),
    created_at          TIMESTAMP       DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (customer_id),
    INDEX idx_churn (churn_flag),
    INDEX idx_contract (contract_type),
    INDEX idx_tenure (tenure_months)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
