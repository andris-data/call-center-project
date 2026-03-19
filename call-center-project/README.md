# Call Center Data Engineering Project

End-to-end data pipeline built on real AWS Connect call center data,
as part of my transition from Data Analyst to Data Engineer.

## What this project builds
A fully automated pipeline that takes raw AWS Connect contact records,
cleans and transforms them, loads them into a data warehouse, and makes
them available for reporting — running automatically every night with
zero manual steps.

## Tech stack
| Layer          | Tool                        |
|----------------|-----------------------------|
| Ingestion      | AWS Glue + PySpark          |
| Storage        | AWS S3 (data lake)          |
| Warehouse      | Amazon Redshift             |
| Transformation | dbt                         |
| Orchestration  | Apache Airflow (MWAA)       |
| Language       | Python 3.x / SQL            |
| Infrastructure | Terraform                   |

## Data source
AWS Connect contact center records including inbound calls, callbacks,
agent handling, queue times, and disposition outcomes.

## Project phases
- [x] Phase 1 — Local environment setup + Python foundations
- [ ] Phase 2 — AWS S3 + Glue + PySpark ingestion pipeline
- [ ] Phase 3 — dbt transformation models in Redshift
- [ ] Phase 4 — Airflow orchestration (MWAA)
- [ ] Phase 5 — Polish, certify, portfolio ready

## Project status
Phase 1 — Week 1 — Environment setup complete

## Author
Your Name — Data Analyst transitioning to Data Engineer