import pandas as pd
import sqlite3
import os

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
CLEANED_PATH = r"C:\Users\andrej.ristikj\PycharmProjects\callcenter\call-center-project\data\training\Call_data_cleaned.csv"
DB_PATH      = r"C:\Users\andrej.ristikj\PycharmProjects\callcenter\call-center-project\data\training\call_center.db"

print("=" * 60)
print("CREATING SQL TRAINING DATABASE")
print("=" * 60)

# -----------------------------------------------
# LOAD CLEANED CSV
# -----------------------------------------------

print("\n[1/4] Loading cleaned data...")
df = pd.read_csv(CLEANED_PATH)
print(f" Loaded {len(df):,} rows")

# -----------------------------------------------
# KEEP ONLY USEFUL COLUMNS FOR SQL PRACTICE
# -----------------------------------------------

print("\n[2/4] Selecting columns for training database...")
cols = cols = [
    'contact_id',
    'date',
    'ctr_init_tstamp_tz',
    'call_types',
    'dispositions',
    'queue',
    'client_code',
    'agent_full_name',
    'agent_hierarchy_1_name',
    'agent_hierarchy_2_name',
    'agent_hierarchy_3_name',
    'handled_by_agent',
    'is_abandoned',
    'is_handled',
    'handle_time_s',
    'hold_duration_s',
    'acw_duration_s',
    'tlk_duration_s',
    'queue_duration',
    'call_hour',
    'call_dow',
    'ctr_init_method',
    'routing_profile_name',
    'vm',
]

# only keep columns that exist

cols = [c for c in cols if c in df.columns]
df = df[cols]
print(f" Selected {len(cols)} columns")

# -----------------------------------------------
# ANONYMISE SENSITIVE COLUMNS
# -----------------------------------------------

print("\n[3/4] Anonymising sensitive data...")

# mask customer phone numbers - not needed fo SQL practice
if 'customer_addr_val' in df.columns:
    df['cust_addr_val'] = 'REDACTED'

# keep agent names - useful for SQL exercises
# but hash contact_id to break any PII linkage

import hashlib
if 'contact_id' in df.columns:
    df['contact_id'] = df['contact_id'].apply(
        lambda x: hashlib.md5(str(x).encode()).hexdigest()[:12]
        if pd.notna(x) else None
    )
    print(" contact_id hashed")

print(" Sensitive columns anonymised")

# -----------------------------------------------
# WRITE TO SQLITE
# -----------------------------------------------

print("\n[4/4] Writing to SQLite database...")
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

conn = sqlite3.connect(DB_PATH)
df.to_sql(
    name='contacts',
    con=conn,
    if_exists='replace',
    index=False
)

conn.close()



print(f"      Database created: {DB_PATH}")
print(f"      Table name: contacts")
print(f"      Rows: {len(df):,}")
print(f"      Columns: {len(df.columns)}")

print("\n" + "=" * 60)
print("DATABASE READY")
print("=" * 60)
print("""
  Connect in PyCharm:
  1. View → Tool Windows → Database
  2. Click + → Data Source → SQLite
  3. Point to your .db file
  4. Click Test Connection → OK

  Or run SQL via Python:
  import sqlite3
  conn = sqlite3.connect(DB_PATH)
  df = pd.read_sql('SELECT * FROM contacts LIMIT 10', conn)
""")

