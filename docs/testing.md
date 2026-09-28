# Telecom Customer Churn - Testing & Quality Assurance Plan

## 1. Overview
This document specifies the testing strategy, validation queries, and automated checks implemented across the Telecom Customer Churn ETL pipeline to guarantee data correctness, schema integrity, and pipeline resilience.

---

## 2. Testing Levels

### A. Unit Testing (Airflow DAG Integrity)
* **Objective:** Ensure the Airflow DAG compiles without syntax errors, circular dependencies, or missing operator dependencies before deployment.
* **Tool:** `pytest` + `apache-airflow`
* **Test Implementation:** Located at `tests/test_dag_integrity.py`
  ```python
  from airflow.models import DagBag

  def test_dag_integrity():
      dag_bag = DagBag(dag_folder="airflow/dags", include_examples=False)
      assert len(dag_bag.import_errors) == 0, f"Import errors detected: {dag_bag.import_errors}"
      assert "telecom_churn_etl" in dag_bag.dags
      dag = dag_bag.get_dag("telecom_churn_etl")
      assert len(dag.tasks) == 4
  ```

### B. Integration Testing (End-to-End Orchestration)
* **Objective:** Verify that Airflow in Docker connects to the Windows host OpenSSH endpoint, validates prerequisites, launches `Pan.bat`, and completes cleanly.
* **Verification Steps:**
  1. Trigger DAG manually via Airflow UI (`http://localhost:8080`) or CLI:
     ```bash
     docker compose exec airflow-worker airflow dags trigger telecom_churn_etl
     ```
  2. Inspect task logs for `check_pdi_prerequisites` and `run_pentaho_etl`.
  3. Verify exit code `0` and proper termination of the PDI Java runtime.

### C. Data Quality & Assertion Testing
* **Objective:** Ensure no corrupted rows, empty IDs, or dropped records exist in the target warehouse.
* **Validation Queries (`sql/validation_queries.sql`):**
  * **Row Count Assertion:** Verify loaded rows equal source records (~7,043 rows).
  * **Primary Key Uniqueness:** Assert 0 duplicates on `customer_id`.
  * **Null Rate Verification:** Verify 0 nulls across mandatory fields (`customer_id`, `tenure_months`, `monthly_charges`, `total_charges`, `churn_flag`).
  * **Business Rule Validation:** Verify `monthly_charges >= 0`, `total_charges >= 0`, and `churn_flag IN ('Yes', 'No')`.

### D. Resilience & Retry Testing
* **Objective:** Verify Airflow's retry policy under network or file locking exceptions.
* **Simulated Fault:**
  * Temporarily rename `Transformation 1.ktr` to trigger prerequisite failure.
* **Expected Result:**
  * Task transitions to `FAILED` then immediately to `UP_FOR_RETRY`.
  * Airflow waits 1.5 minutes (90 seconds).
  * Task initiates Retry 1.
  * Restoring the file causes Retry 1 to succeed without manual pipeline restart.

---


