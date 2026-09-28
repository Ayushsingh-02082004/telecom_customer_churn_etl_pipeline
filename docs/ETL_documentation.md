# Telecom Customer Churn - ETL Pipeline Documentation

## 1. Executive Summary
This document outlines the architecture, data flow, transformation rules, and operational lifecycle of the **Telecom Customer Churn ETL Pipeline**. The system automates data ingestion from raw telecom billing and subscriber files, applies data cleansing and normalization via **Pentaho Data Integration (PDI)**, orchestrates the workflow using **Apache Airflow in Docker**, stores curated records in a **MariaDB** relational warehouse, and exposes metrics via **Power BI**.

---

## 2. Architecture & Data Flow

```
┌─────────────────────────────────┐
│     Raw Data (CSV Source)       │
│    Telco-Customer-Churn.csv     │
└────────────────┬────────────────┘
                 │
                 ▼
┌────────────────────────────────────────────────────────┐
│        Orchestration Layer (Apache Airflow)            │
│  - Task 1: Container Source CSV Validation             │
│  - Task 2: Host PDI & File Prerequisite Validation    │
│  - Task 3: SSH Execution of Pentaho Pan.bat (Retries)  │
│  - Task 4: Pipeline Completion Notification            │
└────────────────┬───────────────────────────────────────┘
                 │ (Triggers via OpenSSH)
                 ▼
┌────────────────────────────────────────────────────────┐
│         Transformation Engine (Pentaho PDI)            │
│  - CSV File Input & Schema Enforcement                 │
│  - String Trimming & Null Value Imputation             │
│  - Data Type Normalization (Float parsing)             │
│  - Feature Engineering & Standardized Column Renaming  │
└────────────────┬───────────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│       Curated Relational DB     │
│   MariaDB Table: customer_churn │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│     Reporting & Analytics       │
│   Power BI Executive Dashboard  │
└─────────────────────────────────┘
```

---

## 3. Transformation Rules (PDI Transformation: `Transformation 1.ktr`)

1. **Extraction (`CSV file input`)**:
   * Reads the raw 7,043 subscriber records.
   * Enforces field delimiters, character encoding (`UTF-8`), and header parsing.
2. **String Operations & Normalization**:
   * Trims leading/trailing whitespace across customer identifier and category strings.
   * Standardizes case for category values (`Yes`/`No`, service names).
3. **Null Handling & Type Conversion**:
   * Empty string entries in `TotalCharges` (occurring on new accounts with tenure = 0) are converted to `0.00`.
   * Formats numeric fields (`tenure_months`, `monthly_charges`, `total_charges`) to standard SQL-compatible numeric types.
4. **Column Standardization**:
   * Renames camelCase source headers to snake_case target schema (`customerID` -> `customer_id`, `MonthlyCharges` -> `monthly_charges`, `Churn` -> `churn_flag`).
5. **Loading (`Table output`)**:
   * Commits transformed records in batches (batch size: 1,000) into `customer_churn`.
   * Truncates table prior to load to ensure clean idempotency during scheduled refreshes.

---

## 4. Orchestration & Resilience (Airflow DAG: `telecom_churn_dag.py`)

* **Execution Schedule**: Triggered on-demand or configured for periodic scheduled runs.
* **Pre-flight Health Checks**:
  * `check_source_csv`: Validates that the input data exists inside the Airflow container volume.
  * `check_pdi_prerequisites`: Executes a PowerShell test over SSH verifying `Pan.bat`, `Transformation 1.ktr`, and host CSV exist before starting.
* **Failure Handling & Retries**:
  * Configured with `retries: 2` and `retry_delay: timedelta(minutes=1.5)`.
  * If a transient SSH network hiccup or temporary file lock occurs, Airflow sets state to `UP_FOR_RETRY` and waits 90 seconds before retrying.
* **Timeout Controls**: 10-minute task timeout (`cmd_timeout=600`) prevents runaway or hanging processes.

---

## 5. Target Schema & Data Serving

The target MariaDB table `customer_churn` stores customer attributes indexed by `churn_flag`, `contract_type`, and `tenure_months` for optimized SQL query performance and fast analytical slicing in Power BI.
