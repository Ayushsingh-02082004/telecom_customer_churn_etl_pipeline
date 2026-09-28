FROM apache/airflow:3.3.1

USER airflow

RUN mkdir -p /opt/airflow/.ssh && chmod 700 /opt/airflow/.ssh

RUN pip install --no-cache-dir apache-airflow-providers-ssh
