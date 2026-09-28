-- =============================================================================
-- Telecom Customer Churn - Data Quality & Analytics Validation Queries
-- Target Database: MariaDB / MySQL
-- Table: customer_churn
-- =============================================================================

USE telecom_db;

-- 1. Total Record Count Validation (Expected ~7,043 rows)
SELECT COUNT(*) AS total_records_loaded 
FROM customer_churn;

-- 2. Primary Key Uniqueness Check (Must return 0 duplicate records)
SELECT customer_id, COUNT(*) AS duplicate_count
FROM customer_churn
GROUP BY customer_id
HAVING COUNT(*) > 1;

-- 3. Null / Missing Value Check in Critical Columns
SELECT 
    COUNT(CASE WHEN customer_id IS NULL OR customer_id = '' THEN 1 END) AS null_customer_id,
    COUNT(CASE WHEN tenure_months IS NULL THEN 1 END) AS null_tenure,
    COUNT(CASE WHEN monthly_charges IS NULL THEN 1 END) AS null_monthly_charges,
    COUNT(CASE WHEN total_charges IS NULL THEN 1 END) AS null_total_charges,
    COUNT(CASE WHEN churn_flag IS NULL OR churn_flag = '' THEN 1 END) AS null_churn_flag
FROM customer_churn;

-- 4. Overall Churn Distribution (Count & Churn Rate %)
SELECT 
    churn_flag,
    COUNT(*) AS customer_count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM customer_churn), 2) AS percentage
FROM customer_churn
GROUP BY churn_flag;

-- 5. Churn Rate by Contract Type
SELECT 
    contract_type,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn_flag = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN churn_flag = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges
FROM customer_churn
GROUP BY contract_type
ORDER BY churn_rate_pct DESC;

-- 6. Churn Rate by Internet Service Provider Type
SELECT 
    internet_service,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN churn_flag = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(SUM(CASE WHEN churn_flag = 'Yes' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 2) AS churn_rate_pct
FROM customer_churn
GROUP BY internet_service
ORDER BY churn_rate_pct DESC;

-- 7. Monthly Revenue Exposure from Churned Customers
SELECT 
    churn_flag,
    ROUND(SUM(monthly_charges), 2) AS total_monthly_revenue,
    ROUND(AVG(monthly_charges), 2) AS avg_monthly_charges,
    ROUND(SUM(total_charges), 2) AS total_historical_charges
FROM customer_churn
GROUP BY churn_flag;
