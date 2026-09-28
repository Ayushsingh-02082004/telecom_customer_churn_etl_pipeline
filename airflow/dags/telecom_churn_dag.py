from datetime import timedelta
import pendulum

from airflow.sdk import DAG
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.ssh.operators.ssh import SSHOperator


PDI_PAN_PATH = r"D:\Python ETL\pdi-ce-10.2.0.0-222\pdi-ce-10.2.0.0-222\data-integration\Pan.bat"
TRANSFORMATION_PATH = r"D:\Python ETL\telecom-customer-churn\pentaho\transformations\Transformation 1.ktr"
PDI_SOURCE_CSV_PATH = r"D:\Python ETL\telecom-customer-churn\data\Telco-Customer-Churn.csv"

CHECK_PDI_PREREQUISITES_COMMAND = rf'''powershell.exe -NoProfile -NonInteractive -Command "$required = @('{PDI_PAN_PATH}', '{TRANSFORMATION_PATH}', '{PDI_SOURCE_CSV_PATH}'); $missing = $required | Where-Object {{ -not (Test-Path -LiteralPath $_ -PathType Leaf) }}; if ($missing) {{ $missing | ForEach-Object {{ Write-Error \"Missing required PDI file: $_\" }}; exit 1 }}; Write-Output 'PDI prerequisites found successfully.'; exit 0"'''

RUN_PENTAHO_COMMAND = rf'''powershell.exe -NoProfile -NonInteractive -Command "& '{PDI_PAN_PATH}' '/file:{TRANSFORMATION_PATH}'; exit $LASTEXITCODE"'''


with DAG(
    dag_id="telecom_churn_etl",
    schedule=None,
    start_date=pendulum.datetime(2026, 1, 1, tz="Asia/Kolkata"),
    catchup=False,
    default_args={
        "retries": 2,
        "retry_delay": timedelta(minutes=1.5),
    },
    tags=["telecom", "churn", "pentaho", "etl"],
) as dag:

    check_source_csv = BashOperator(
        task_id="check_source_csv",
        bash_command="test -f '/opt/airflow/data/Telco-Customer-Churn.csv' && echo 'Airflow source CSV found successfully.'",
    )

    check_pdi_prerequisites = SSHOperator(
        task_id="check_pdi_prerequisites",
        ssh_conn_id="windows_ssh",
        command=CHECK_PDI_PREREQUISITES_COMMAND,
        cmd_timeout=60,
    )

    run_pentaho_etl = SSHOperator(
        task_id="run_pentaho_etl",
        ssh_conn_id="windows_ssh",
        command=RUN_PENTAHO_COMMAND,
        cmd_timeout=600,
    )

    pipeline_success = BashOperator(
        task_id="pipeline_success",
        bash_command=(
            "echo 'Telecom Customer Churn ETL completed successfully.'"
        ),
    )

    check_source_csv >> check_pdi_prerequisites >> run_pentaho_etl >> pipeline_success
