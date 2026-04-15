import pandas as pd
import re
import os


# Config

INPUT_PATH  = r"C:\Users\andrej.ristikj\PycharmProjects\callcenter\call-center-project\data\raw\Call_data.csv"
OUTPUT_PATH = r"C:\Users\andrej.ristikj\PycharmProjects\callcenter\call-center-project\data\training\Call_data_cleaned.csv"

print("="* 60)
print("CALL CENTER DATA CLEANER")
print("=" * 60)

# LOAD

print("\n[1/8] Loading raw data...")
df = pd.read_csv(INPUT_PATH)
print(f" Loaded {len(df):,} rows, {len(df.columns)} columns")


# -----------------------------------------------
# STEP 1 Drop Blank Column
# -----------------------------------------------



print("\n[2/8] Dropping blank column...")
blank_cols = [c for c in df.columns if str(c).strip() == '']
df = df.drop(columns=blank_cols)
print(f" Dropped {len(blank_cols)} blank columns")
print(f" Columns remaining: {len(df.columns)}")


# -----------------------------------------------
# STEP 2 Standardise column names
# -----------------------------------------------



print("\n[3/8] Standardising column names...")
df.columns = (
    df.columns.str.strip()
    .str.lower()
    .str.replace(' ', '_')
    .str.replace(r'[^a-z0-9_]', '', regex=True)
)
print(" Column names cleaned:")
for col in df.columns:
    print(f"   -{col}")


# -----------------------------------------------
# STEP 3 PARSE TIMESTAMPS
# -----------------------------------------------



print("\n[4/8] Parsing timestamp columns...")
timestamp_cols = ['ctr_init_tstamp_tz',
    'acw_end_tstamp_tz',
    'acw_start_tstamp_tz',
    'conn_to_ac_tstamp_tz',
    'conn_to_agent_tstamp_tz',
    'dequeue_tstamp_tz',
    'disc_tstamp_tz',
    'enqueue_tstamp_tz',
    'transfer_complete_time_tz',
]
for col in timestamp_cols:
    if col in df.columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        print(f" Parsed: {col}")

# parse date column
if 'date' in df.columns:
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    print(f" Parsed: date")


# -----------------------------------------------
# STEP 4 - CLEAN NUMERIC COLUMNS
# -----------------------------------------------



print("\n[5/8] Cleaning numeric columns... ")
numeric_cols = [
    'handle_time_s',
    'hold_duration_s',
    'acw_duration_s',
    'tlk_duration_s',
    'queue_duration',
]
for col in numeric_cols:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

# cap impossible handle times at 1 hour

if 'handle_time_s' in df.columns:
    before = (df['handle_time_s'] > 3600).sum()
    df['handle_time_s'] = df['handle_time_s'].clip(upper=3600)
    print(f" Capped {before} handle times exceeding 3600s")

print(" Numeric columns cleaned")


# -----------------------------------------------
# Step 5 CLEAN DISPOSITIONS
# -----------------------------------------------


print("\n[6/8] Normalising dispositions...")

def clean_disposition(val):
    if pd.isna(val):
        return None
    # remove newline characters
    val = str(val).replace('\n', '').replace('\r', '').strip()
    val = val.strip()
    return val

# map messy values to clean standard categories
DISPOSITION_MAP = {
    # appointments
    'appointment - confirm':            'Appointment - Confirm',
    'appointment - confirmed':          'Appointment - Confirm',
    'appointment confirmation':         'Appointment - Confirm',
    'appointment confirmation\n\n':     'Appointment - Confirm',
    'appt. confirmation':               'Appointment - Confirm',
    'appt confirmation':                'Appointment - Confirm',
    'appt. confirmation\n\n':           'Appointment - Confirm',
    # cancellations
    'appointment - cancel':             'Appointment - Cancel',
    'appointment - cancelled':          'Appointment - Cancel',
    'cancelled appointment':            'Appointment - Cancel',
    'canceled appt.':                   'Appointment - Cancel',
    'canceled appt':                    'Appointment - Cancel',
    'canceled appt.\n\n':               'Appointment - Cancel',
    'appointment - cancel/no reschedule':'Appointment - Cancel',
    # reschedules
    'appointment - reschedule':         'Appointment - Reschedule',
    'appointment - rescheduled':        'Appointment - Reschedule',
    'appointment reschedule':           'Appointment - Reschedule',
    'appointment reschedules':          'Appointment - Reschedule',
    'rescheduled appt':                 'Appointment - Reschedule',
    'rescheduled appt.':                'Appointment - Reschedule',
    'rescheduled appt.\n\n':            'Appointment - Reschedule',
    # hang ups
    'hang up':                          'Hang Up',
    'hang up\n\n':                      'Hang Up',
    'hang up/wrong number':             'Hang Up',
    'wrong number/hang up':             'Hang Up',
    'wrong number':                     'Hang Up',
    # general information
    'general information':              'General Information',
    'general information\n\n':          'General Information',
    'general inquiry':                  'General Information',
    'general inquiry*':                 'General Information',
    'general directions/information':   'General Information',
    'general practice information':     'General Information',
    'practice information':             'General Information',
}

disp_col = next((c for c in df.columns
                 if c in ['dispositions', 'disposition']), None)

if disp_col:
    # first clean whitespace and newlines
    df[disp_col] = df[disp_col].apply(clean_disposition)
    # then apply the mapping
    df[disp_col] = df[disp_col].str.lower().map(
        lambda x: DISPOSITION_MAP.get(x, x) if pd.notna(x) else x
    )
    unique_before = df[disp_col].nunique()
    print(f" Unique dispositions after cleaning: {unique_before}")

# -----------------------------------------------
# STEP 6 - ADD DERIVED COLUMNS
# -----------------------------------------------


print("\n[7/8] Adding derived columns...")


# was the call abandoned
if 'call_types' in df.columns:
    df['is_abandoned'] = df['call_types'] == 'Abandoned'
    print( " Added: is_abandoned")

# was the call handled by an agent
if 'handled_by_agent' in df.columns:
    df['is_handled'] = df['handled_by_agent'].notna()
    print(" Added: is_handled")

# extract hour of day from call start
if 'ctr_init_tstamp_tz' in df.columns:
    df['call_hour'] = pd.to_datetime(
        df['ctr_init_tstamp_tz'], errors='coerce'
    ).dt.hour
    df['call_dow'] = pd.to_datetime(
        df['ctr_init_tstamp_tz'], errors='coerce'
    ).dt.day_name()
    print("      Added: call_hour, call_dow")

# extract client code from queue name e.g. [006] (BEA) > BEA
if 'queue' in df. columns:
    df['client_code'] = df['queue'].str.extract(r'\(([^)]+)\)')
    df['client_code'] = df['client_code'].fillna('ClientUnknown')
    print(" Added: client_code")

# -----------------------------------------------
# STEP 7 — SAVE
# -----------------------------------------------

print("\n[8/8] Saving cleaned file...")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f" Saved to: {OUTPUT_PATH}")

# -----------------------------------------------
# SUMMARY
# -----------------------------------------------


print("\n" + "=" * 60)
print("CLEANING SUMMARY")
print("=" * 60)
print(f"  Rows:              {len(df):,}")
print(f"  Columns:           {len(df.columns)}")
print(f"  Is abandoned:      {df['is_abandoned'].sum():,}"
      if 'is_abandoned' in df.columns else "")
print(f"  Is handled:        {df['is_handled'].sum():,}"
      if 'is_handled' in df.columns else "")
print(f"\n  Client breakdown:")
if 'client_code' in df.columns:
    print(df['client_code'].value_counts().to_string())
print("\n  Call hour distribution (all hours):")
if 'call_hour' in df.columns:
    hourly = df['call_hour'].value_counts().sort_index()
    for hour, count in hourly.items():
        bar = '█' * (count // 2000)
        print(f"    {hour:02d}:00  {count:>6,}  {bar}")
print("=" * 60)
print("COMPLETE")
print("=" * 60)

