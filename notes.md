# Data Dictionary and Engineering Notes

## Client Codes

| Code          | Type                   | Notes                               |
|---------------|------------------------|-------------------------------------|
| Client_01     | Orthopaedic practice   | Largest client — 63,375 calls       |
| Client_02     | Orthopaedic institute  | 11.1% abandonment — high risk       |
| Client_03     | Care network           | 43,716 calls                        |
| Client_04     | Care center            | Best performer — 2.4% abandonment   |
| Client_05     | Allied associates      | 35,979 calls                        |
| Client_06     | Medical imaging        | 28,751 calls                        |
| Client_07     | Health system          | 28,616 calls                        |
| Client_08     | Medical group          | 25,683 calls                        |
| Client_09     | Care network           | 25,207 calls                        |
| Client_10     | Health system          | 20,807 calls                        |
| Client_11     | Health center          | 18,829 calls                        |
| Client_12     | Hospital               | 18,591 calls                        |
| Client_13     | Health collective      | 17,171 calls                        |
| Client_14     | Orthopaedic associates | 11,817 calls                        |
| Client_15     | Practice consultants   | 11,808 calls                        |
| Client_16     | Oncology network       | 10,788 calls                        |
| Client_17     | Medical imaging        | 10,485 calls                        |
| Client_18     | TBC                    | Unusually high handle times         |
| ClientUnknown | Unknown                | 40,705 calls — needs investigation  |
| Client_19     | General queue          | No specific client                  |

---

## Call Types

| Call Type           | Count   | Description                                   |
|---------------------|---------|-----------------------------------------------|
| InboundHandledCall  | 478,211 | Standard inbound call handled by an agent     |
| Abandoned           | 45,438  | Caller hung up before reaching an agent       |
| Callback            | 24,625  | Customer chose callback option from queue     |
| TransferHandledCall | 1,695   | Call transferred to another agent or queue    |
| APIHandledCall      | 31      | Programmatically handled call                 |

---

## Key Metrics

| Metric                   | Value   | Notes                                      |
|--------------------------|---------|--------------------------------------------|
| Overall abandonment rate | 8.3%    | Industry threshold is 5% — above average  |
| Peak hour                | 12:00   | 11.8% of daily volume                      |
| Worst abandonment day    | Dec 1st | 19.8% — serious operational problem        |
| Busiest week             | Week 48 | Highest call volume and abandonment        |
| Avg handle time          | 317s    | Approximately 5.3 minutes per call         |
| Max handle time capped   | 3,600s  | 93 records capped in cleaner               |

---

## Data Quality Issues Found

| Issue                         | Severity | Resolution                                   |
|-------------------------------|----------|----------------------------------------------|
| Blank column name             | Low      | Dropped in cleaner.py Step 2                 |
| Handle times over 4 hours     | Medium   | Capped at 3,600s in cleaner.py               |
| 300+ disposition variants     | High     | Partial normalisation in cleaner.py Step 5   |
| Newline chars in dispositions | Medium   | Stripped in cleaner.py Step 5                |
| Different timezones per client| Medium   | Flagged — to be resolved in Phase 2          |
| ClientUnknown — 40,705 rows   | Medium   | Queue has no client code — investigate       |

---

## Column Reference

| Column                  | Type      | Description                                    |
|-------------------------|-----------|------------------------------------------------|
| contact_id              | VARCHAR   | Unique identifier per contact — hashed         |
| date                    | DATE      | Date of the call                               |
| ctr_init_tstamp_tz      | TIMESTAMP | Exact time call was initiated                  |
| call_types              | VARCHAR   | InboundHandledCall / Abandoned / Callback etc  |
| dispositions            | VARCHAR   | Outcome code entered by agent                  |
| queue                   | VARCHAR   | Full queue name including client code          |
| client_code             | VARCHAR   | Extracted from queue name                      |
| agent_full_name         | VARCHAR   | Agent who handled the call — null if abandoned |
| agent_hierarchy_1_name  | VARCHAR   | Company level                                  |
| agent_hierarchy_2_name  | VARCHAR   | Team level                                     |
| agent_hierarchy_3_name  | VARCHAR   | Group level                                    |
| handle_time_s           | INTEGER   | Total handle time in seconds — capped at 3,600 |
| hold_duration_s         | INTEGER   | Time caller was on hold                        |
| acw_duration_s          | INTEGER   | After call work time in seconds                |
| tlk_duration_s          | INTEGER   | Talk time in seconds                           |
| queue_duration          | INTEGER   | Time caller waited in queue                    |
| is_abandoned            | BOOLEAN   | True if call was abandoned                     |
| is_handled              | BOOLEAN   | True if call reached an agent                  |
| call_hour               | INTEGER   | Hour of day call started 0-23                  |
| call_dow                | VARCHAR   | Day of week — Monday through Sunday            |

---

## Engineering Notes

**Timezone issue** — different clients operate in different timezones.
call_hour is currently extracted from raw timestamps without timezone
conversion. Hourly distribution may be slightly inaccurate across
clients. To be resolved in Phase 2 Glue job using a
client-to-timezone mapping table.

**Disposition normalisation** — 380 unique disposition values remain
after initial cleaning. Further normalisation needed. A full mapping
table will be built in dbt as a seed file in Phase 3.

**ClientUnknown** — 40,705 calls have no extractable client code.
These appear to come from a general queue that predates the client
code naming convention. Needs investigation.

**Client_18 investigation** — this client shows unusually high handle
times consistently hitting the 60-minute cap. Could be complex case
type, training issue, or data quality problem. Flag for ops review.

---

## Decisions Log

| Date    | Decision                         | Reason                                       |
|---------|----------------------------------|----------------------------------------------|
| Phase 1 | Cap handle time at 3,600s        | 93 records had impossible values             |
| Phase 1 | Extract client_code from queue   | Enables per-client analysis                  |
| Phase 1 | Hash contact_id                  | Remove PII linkage risk                      |
| Phase 1 | Exclude customer phone numbers   | Not needed for analysis                      |
| Phase 1 | Use synthetic data for portfolio | Protects company data, cleaner story         |
| Phase 1 | Anonymise client codes           | Protect company and client confidentiality   |