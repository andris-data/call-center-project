# Call Center Data Engineering Project

End-to-end data pipeline built on AWS, designed for contact center
analytics at scale.

## The business problem

Contact centers generate large volumes of raw event data — inbound
calls, abandoned calls, callbacks, agent interactions. This data
arrives in inconsistent formats with data quality issues and needs
to be transformed into reliable analytics that operations teams can
act on every morning.

This pipeline solves that problem end to end.

## What the pipeline does

- Ingests raw AWS Connect contact records from S3
- Cleans and standardises data using PySpark on AWS Glue
- Validates output quality using Athena before loading
- Loads into Redshift and transforms using dbt models
- Runs automatically every night via Apache Airflow on MWAA
- Alerts the team if anything breaks

## Architecture

Raw S3 → Glue ETL → Processed S3 → Athena validation
→ Redshift → dbt models → Power BI dashboards

## Tech stack

| Layer           | Tool                      |
|-----------------|---------------------------|
| Ingestion       | AWS Glue + PySpark        |
| Storage         | Amazon S3 (data lake)     |
| Validation      | Amazon Athena             |
| Warehouse       | Amazon Redshift           |
| Transformation  | dbt                       |
| Orchestration   | Apache Airflow (MWAA)     |
| Language        | Python 3.x / SQL          |
| Infrastructure  | Terraform (planned)       |
| Version control | Git / GitHub              |

## Data

This project uses a synthetic dataset generated to mirror the
structure of real AWS Connect contact center exports.

- 550,000 contact records
- 18 client queues
- 41-day date range (Nov 2025 - Jan 2026)
- Realistic call volume patterns by hour and day of week
- 8.3% abandonment rate
- 80 synthetic agents across multiple hierarchy levels

The generator script is at scripts/generate_synthetic_data.py
Run it to regenerate the full dataset from scratch.

## Implementation status

| Component             | Status         | Notes                                        |
|-----------------------|----------------|----------------------------------------------|
| Data profiling        | Complete       | profiler.py - 550k rows analysed             |
| Data cleaning         | Complete       | cleaner.py - standardised, derived columns   |
| Synthetic data gen    | Complete       | generate_synthetic_data.py                   |
| SQL analytics models  | Complete       | Level 1-5 exercises, real business questions |
| AWS Glue PySpark job  | In progress    | Script written, pending deployment           |
| dbt models            | In progress    | Model layer being designed                   |
| Airflow DAG           | Planned        | Phase 4                                      |
| Terraform             | Planned        | Phase 5                                      |

## SQL models built

Queries that answer real operational questions.
Each becomes a dbt model in Phase 3:

- Total call volume per client ranked by busiest
- Call type breakdown per client — inbound vs abandoned vs callback
- Hourly call distribution — identifying peak staffing hours
- Daily abandonment rate per client — operational SLA monitoring
- Weekly volume trends — identifying seasonal patterns
- Long call analysis — handle time over 30 minutes

## Key engineering decisions

**Why Parquet over CSV** — 10x compression, columnar reads mean
Athena only scans relevant columns, partition pruning reduces
query cost by skipping irrelevant date folders.

**Why dbt for transformation** — version controlled SQL, automatic
dependency resolution, built-in data quality tests, and
auto-generated documentation. Transformations are reviewable
like any other code.

**Why Airflow over cron** — dependency management between tasks,
automatic retries, failure alerting, and a UI for monitoring
pipeline runs. Cron has none of these.

**Two-zone S3 architecture** — raw zone is immutable, processed
zone holds clean Parquet. Bad transformation logic never
corrupts source data.

## Project phases

- [x] Phase 1 — Local environment setup
- [x] Phase 1 — Data profiling and cleaning scripts
- [x] Phase 1 — Advanced SQL exercises Levels 1-5
- [x] Phase 1 — Synthetic data generator
- [ ] Phase 2 — AWS S3 + Glue + PySpark pipeline
- [ ] Phase 3 — dbt transformation models
- [ ] Phase 4 — Airflow orchestration
- [ ] Phase 5 — Terraform + AWS certification + portfolio polish

## Repository structure

call-center-project/
├── scripts/
│   ├── profiler.py                  # data profiling
│   ├── cleaner.py                   # data cleaning and standardisation
│   ├── create_training_db.py        # SQLite training database
│   └── generate_synthetic_data.py   # synthetic data generator
├── sql/
│   ├── level1_exercises.sql         # foundations
│   └── level2_exercises.sql         # aggregations and date functions
├── notes.md                         # data dictionary and engineering notes
└── README.md

## Author

Andrej Ristikj
Data Analyst transitioning to Data Engineer
AWS - Python - SQL - dbt - Airflow