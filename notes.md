# Data Dictionary & Notes

## Client Codes
| Code          | Full Name                        | Notes                    |
|---------------|----------------------------------|--------------------------|
| BEA           | Beacon Orthopaedics & Spine      | Largest client           |
| PFIT          | TBC — possibly IT services       | High handle times        |
| OHJOI         | TBC                              |                          |
| WCC           | TBC                              |                          |
| ACC           | TBC                              |                          |
| ClientUnknown | Unknown client                   | Needs investigation      |

## Data Quality Notes
- Handle times capped at 3600s (1 hour) in cleaner.py
- 380 unique dispositions — normalisation ongoing
- Timezone differences per client — to be resolved later
- PFIT shows unusually high handle times — needs investigation