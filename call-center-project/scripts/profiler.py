import pandas as pd

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
FILE_PATH = r"C:\Users\andrej.ristikj\PycharmProjects\callcenter\call-center-project\data\raw\Call_data.csv"

# -----------------------------------------------
# LOAD
# -----------------------------------------------
print("=" * 60)
print("CALL CENTER DATA PROFILER")
print("=" * 60)

df = pd.read_csv(FILE_PATH)

# -----------------------------------------------
# BASIC SHAPE
# -----------------------------------------------
print(f"\n BASIC INFO")
print(f"   Rows:     {len(df):,}")
print(f"   Columns:  {len(df.columns)}")

# -----------------------------------------------
# COLUMN NAMES
# -----------------------------------------------
print(f"\n COLUMNS")
for col in df.columns:
    print(f"   - {col}")

# -----------------------------------------------
# NULL CHECK
# -----------------------------------------------
print(f"\n NULL VALUES")
nulls = df.isnull().sum()
nulls_found = nulls[nulls > 0]
if len(nulls_found) == 0:
    print("   No nulls found")
else:
    for col, count in nulls_found.items():
        pct = count / len(df) * 100
        print(f"   {col:<40} {count:>6,} nulls ({pct:.1f}%)")

# -----------------------------------------------
# DUPLICATE CHECK
# -----------------------------------------------
dupes = df.duplicated().sum()
print(f"\n DUPLICATES")
print(f"   Duplicate rows: {dupes:,}")

# -----------------------------------------------
# DISPOSITION BREAKDOWN
# -----------------------------------------------
print(f"\n DISPOSITION BREAKDOWN")
# find the disposition column regardless of case
disp_col = next((c for c in df.columns if c.lower() == 'dispositions'
                 or c.lower() == 'disposition'), None)
if disp_col:
    print(df[disp_col].value_counts().to_string())
else:
    print("   Column not found")
# -----------------------------------------------
# CALL TYPES
# -----------------------------------------------
print(f"\n CALL TYPES")
if 'Call Types' in df.columns:
    print(df['Call Types'].value_counts().to_string())
else:
    print("   Column 'Call Types' not found")

# -----------------------------------------------
# DATE RANGE
# -----------------------------------------------
print(f"\n DATE RANGE")
if 'Date' in df.columns:
    df['Date'] = pd.to_datetime(df['Date'])
    print(f"   From: {df['Date'].min().date()}")
    print(f"   To:   {df['Date'].max().date()}")
    print(f"   Days: {(df['Date'].max() - df['Date'].min()).days}")
else:
    print("   Column 'Date' not found")

# -----------------------------------------------
# HANDLE TIME
# -----------------------------------------------
print(f"\n HANDLE TIME STATS (seconds)")
if 'Handle Time (s)' in df.columns:
    ht = pd.to_numeric(df['Handle Time (s)'], errors='coerce').dropna()
    print(f"   Min:    {ht.min():.0f}s")
    print(f"   Max:    {ht.max():.0f}s")
    print(f"   Avg:    {ht.mean():.0f}s")
    print(f"   Median: {ht.median():.0f}s")
else:
    print("   Column 'Handle Time (s)' not found")

# -----------------------------------------------
# QUEUE BREAKDOWN
# -----------------------------------------------
print(f"\n TOP QUEUES")
if 'queue' in df.columns:
    print(df['queue'].value_counts().head(10).to_string())
else:
    print("   Column 'queue' not found")


# -----------------------------------------------
# DATA QUALITY FLAGS
# -----------------------------------------------
print(f"\n DATA QUALITY FLAGS")

# impossible handle times
if 'Handle Time (s)' in df.columns:
    ht = pd.to_numeric(df['Handle Time (s)'], errors='coerce')
    impossible = (ht > 14400).sum()  # more than 4 hours
    print(f"   Handle time > 4 hours:  {impossible:,} rows  ← needs capping")

# blank column names
blank_cols = [c for c in df.columns if str(c).strip() == '']
print(f"   Blank column names:     {len(blank_cols)}  ← needs dropping")

# contact_id nulls
if 'contact_id' in df.columns:
    id_nulls = df['contact_id'].isnull().sum()
    print(f"   Null contact_ids:       {id_nulls:,}")

# -----------------------------------------------
# MULTI-CLIENT BREAKDOWN
# -----------------------------------------------
print(f"\n TOP 10 QUEUES BY VOLUME")
if 'queue' in df.columns:
    queue_stats = df.groupby('queue').agg(
        total_calls=('queue', 'count')
    ).sort_values('total_calls', ascending=False).head(10)
    print(queue_stats.to_string())

print("\n" + "=" * 60)
print("PROFILE COMPLETE")
print("=" * 60)
