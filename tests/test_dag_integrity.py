from datetime import timedelta
import os
import pytest
from airflow.models import DagBag

# Dynamically locate the dags directory
CANDIDATE_PATH_1 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "airflow", "dags"))
CANDIDATE_PATH_2 = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "dags"))

DAG_FOLDER = CANDIDATE_PATH_1 if os.path.isdir(CANDIDATE_PATH_1) else CANDIDATE_PATH_2
DAG_ID = "telecom_churn_etl"


@pytest.fixture(scope="session")
def dag_bag():
    """Load all DAGs from the dags folder into a DagBag once for the entire test session."""
    return DagBag(dag_folder=DAG_FOLDER, include_examples=False)


def test_dag_import_errors(dag_bag):
    """1. Verify that there are zero import or syntax errors across all DAG files."""
    assert len(dag_bag.import_errors) == 0, f"Import errors detected: {dag_bag.import_errors}"


def test_dag_exists_and_attributes(dag_bag):
    """2. Verify that the telecom_churn_etl DAG exists and has correct core settings."""
    assert DAG_ID in dag_bag.dags, f"DAG '{DAG_ID}' was not found in {DAG_FOLDER}"
    dag = dag_bag.get_dag(DAG_ID)
    
    assert dag is not None
    assert dag.catchup is False
    assert "telecom" in dag.tags
    assert "pentaho" in dag.tags


def test_dag_retry_configuration(dag_bag):
    """3. Verify that the retry resilience policy (retries=2, retry_delay=1.5m) is properly enforced."""
    dag = dag_bag.get_dag(DAG_ID)
    
    assert dag.default_args.get("retries") == 2, "Default retries must be set to 2"
    assert dag.default_args.get("retry_delay") == timedelta(minutes=1.5), (
        "Retry delay must be set to 1.5 minutes (90 seconds)"
    )


def test_dag_task_count_and_ids(dag_bag):
    """4. Verify that all 4 required pipeline tasks exist with the expected task IDs."""
    dag = dag_bag.get_dag(DAG_ID)
    expected_task_ids = {
        "check_source_csv",
        "check_pdi_prerequisites",
        "run_pentaho_etl",
        "pipeline_success",
    }
    actual_task_ids = set(dag.task_dict.keys())
    assert actual_task_ids == expected_task_ids, (
        f"Mismatch in tasks. Expected: {expected_task_ids}, Found: {actual_task_ids}"
    )


def test_dag_task_topology(dag_bag):
    """5. Verify the strict linear dependency execution order:
    check_source_csv >> check_pdi_prerequisites >> run_pentaho_etl >> pipeline_success
    """
    dag = dag_bag.get_dag(DAG_ID)
    
    t1 = dag.get_task("check_source_csv")
    t2 = dag.get_task("check_pdi_prerequisites")
    t3 = dag.get_task("run_pentaho_etl")
    t4 = dag.get_task("pipeline_success")

    assert t2 in t1.downstream_list, "check_pdi_prerequisites must be downstream of check_source_csv"
    assert t3 in t2.downstream_list, "run_pentaho_etl must be downstream of check_pdi_prerequisites"
    assert t4 in t3.downstream_list, "pipeline_success must be downstream of run_pentaho_etl"


def test_ssh_tasks_configuration(dag_bag):
    """6. Verify SSHOperator tasks point to 'windows_ssh' connection and have safe timeouts."""
    dag = dag_bag.get_dag(DAG_ID)
    
    check_prereq = dag.get_task("check_pdi_prerequisites")
    run_pentaho = dag.get_task("run_pentaho_etl")
    
    assert check_prereq.ssh_conn_id == "windows_ssh"
    assert check_prereq.cmd_timeout == 60
    
    assert run_pentaho.ssh_conn_id == "windows_ssh"
    assert run_pentaho.cmd_timeout == 600
