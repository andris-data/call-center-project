import pandas as pd
import numpy as np
import random
import uuid
import hashlib
import os
from datetime import datetime, timedelta

# -----------------------------------------------
# CONFIG
# -----------------------------------------------
OUTPUT_PATH = r"C:\Users\andrej.ristikj\PycharmProjects\callcenter\call-center-project\data\training\synthetic_call_data.csv"
NUM_RECORDS = 550000
START_DATE  = datetime(2025, 11, 21)
END_DATE    = datetime(2026, 1,  1)
RANDOM_SEED = 42

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

print("=" * 60)
print("SYNTHETIC CALL CENTER DATA GENERATOR")
print("=" * 60)

# -----------------------------------------------
# REFERENCE DATA
# -----------------------------------------------

CLIENTS = [
    {"code": "Client_01", "name": "Orthopaedic Practice",    "weight": 12},
    {"code": "Client_02", "name": "Orthopaedic Institute",   "weight": 9},
    {"code": "Client_03", "name": "Care Network",            "weight": 8},
    {"code": "Client_04", "name": "Care Center",             "weight": 7},
    {"code": "Client_05", "name": "Allied Associates",       "weight": 7},
    {"code": "Client_06", "name": "Medical Imaging",         "weight": 5},
    {"code": "Client_07", "name": "Health System",           "weight": 5},
    {"code": "Client_08", "name": "Medical Group",           "weight": 5},
    {"code": "Client_09", "name": "Care Network B",          "weight": 5},
    {"code": "Client_10", "name": "Health System B",         "weight": 4},
    {"code": "Client_11", "name": "Health Center",           "weight": 4},
    {"code": "Client_12", "name": "Hospital",                "weight": 4},
    {"code": "Client_13", "name": "Health Collective",       "weight": 3},
    {"code": "Client_14", "name": "Orthopaedic Associates",  "weight": 2},
    {"code": "Client_15", "name": "Practice Consultants",    "weight": 2},
    {"code": "Client_16", "name": "Oncology Network",        "weight": 2},
    {"code": "Client_17", "name": "Medical Imaging B",       "weight": 2},
    {"code": "CCC",       "name": "CCC General",             "weight": 8},
]

client_codes   = [c["code"]   for c in CLIENTS]
client_names   = [c["name"]   for c in CLIENTS]
client_weights = [c["weight"] for c in CLIENTS]
total_weight   = sum(client_weights)
client_probs   = [w / total_weight for w in client_weights]

QUEUE_TYPES = ["General", "After Hours", "Callback", "Scheduling", "Billing"]
COMPANIES   = ["AGT1", "AGT2", "AGT3", "AGT4"]
TEAMS       = ["Team A", "Team B", "Team C", "Team D", "Team E"]
GROUPS      = ["Group 1", "Group 2", "Group 3"]

FIRST_NAMES = [
    "Emma","Liam","Olivia","Noah","Ava","Elijah","Sophia","James",
    "Isabella","Oliver","Mia","Benjamin","Charlotte","Lucas","Amelia",
    "Mason","Harper","Ethan","Evelyn","Aiden","Sarah","Michael",
    "Jessica","David","Emily","Daniel","Ashley","Christopher","Amanda",
    "Matthew","Stephanie","Andrew","Melissa","Joshua","Nicole"
]
LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller",
    "Davis","Wilson","Anderson","Taylor","Thomas","Jackson","White",
    "Harris","Martin","Thompson","Young","Robinson","Lewis","Foster",
    "Walker","Hall","Allen","Wright","Scott","Green","Baker",
    "Adams","Nelson","Carter","Mitchell","Perez","Roberts","Turner"
]

def make_agent_name():
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

AGENT_POOL = []
seen_names = set()
while len(AGENT_POOL) < 80:
    name = make_agent_name()
    if name not in seen_names:
        seen_names.add(name)
        AGENT_POOL.append({
            "name":      name,
            "email":     name.lower().replace(" ", ".") + "@callcenter-agency.com",
            "company":   random.choice(COMPANIES),
            "team":      random.choice(TEAMS),
            "group":     random.choice(GROUPS),
            "routing":   random.choice(["General Routing", "Dedicated Routing",
                                        "After Hours Routing"]),
        })

CALL_TYPES = {
    "InboundHandledCall":  0.87,
    "Abandoned":           0.083,
    "Callback":            0.044,
    "TransferHandledCall": 0.003,
}
call_type_names   = list(CALL_TYPES.keys())
call_type_weights = list(CALL_TYPES.values())

DISPOSITIONS = [
    ("Contact Care Support",         0.13),
    ("Appointment",                  0.10),
    ("Contact Office Support",       0.08),
    ("General Information",          0.06),
    ("Administrative Call",          0.04),
    ("Hang Up",                      0.04),
    ("Appointment - Confirm",        0.03),
    ("Appointment - Reschedule",     0.03),
    ("Appointment - Cancel",         0.02),
    ("General Inquiry",              0.02),
    ("Appointment - Schedule",       0.02),
    ("Medical Records",              0.02),
    ("Billing",                      0.02),
    ("Phone Triage",                 0.02),
    ("New Patient",                  0.02),
    ("Refill Request",               0.02),
    ("Contact Provider",             0.01),
    ("Nurse Triage",                 0.01),
    ("Wrong Number",                 0.01),
    ("Queue Call Back No Answer",    0.01),
    ("Return Call",                  0.01),
    ("Scheduling",                   0.01),
    ("Results",                      0.01),
    ("Other",                        0.06),
]
disp_names   = [d[0] for d in DISPOSITIONS]
disp_weights = [d[1] for d in DISPOSITIONS]
disp_total   = sum(disp_weights)
disp_probs   = [w / disp_total for w in disp_weights]

INIT_METHODS = {"INBOUND": 0.92, "CALLBACK": 0.044, "API": 0.036}
init_names   = list(INIT_METHODS.keys())
init_probs   = list(INIT_METHODS.values())

# -----------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------

def random_date_between(start, end):
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))


def hour_weight(hour):
    weights = {
        0:1, 1:1, 2:1, 3:1, 4:1, 5:1, 6:1,
        7:2, 8:10, 9:52, 10:110, 11:112,
        12:118, 13:116, 14:112, 15:110,
        16:100, 17:80, 18:40, 19:23,
        20:13, 21:10, 22:7, 23:5
    }
    return weights.get(hour, 1)


def pick_hour():
    hours   = list(range(24))
    weights = [hour_weight(h) for h in hours]
    total   = sum(weights)
    probs   = [w / total for w in weights]
    return np.random.choice(hours, p=probs)


def make_timestamp(base_date, hour):
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return datetime(
        base_date.year, base_date.month, base_date.day,
        hour, minute, second
    )


def make_durations(call_type):
    if call_type == "Abandoned":
        queue_s  = random.randint(10, 600)
        handle_s = 0
        hold_s   = 0
        acw_s    = 0
        talk_s   = 0
    elif call_type == "Callback":
        queue_s  = 0
        talk_s   = random.randint(60, 480)
        hold_s   = random.randint(0, 60)
        acw_s    = random.randint(60, 180)
        handle_s = talk_s + hold_s + acw_s
    else:
        queue_s  = int(np.random.exponential(180))
        queue_s  = min(queue_s, 1200)
        talk_s   = int(np.random.exponential(240))
        talk_s   = max(30, min(talk_s, 3600))
        hold_s   = random.randint(0, 120) if random.random() < 0.2 else 0
        acw_s    = int(np.random.exponential(90))
        acw_s    = max(0, min(acw_s, 600))
        handle_s = talk_s + hold_s + acw_s
    return queue_s, handle_s, hold_s, acw_s, talk_s


def hash_id(val):
    return hashlib.md5(str(val).encode()).hexdigest()[:12]


# -----------------------------------------------
# GENERATE DATES WITH REALISTIC DAILY VOLUMES
# -----------------------------------------------
print("\n[1/4] Planning date distribution...")

all_dates = []
current = START_DATE
while current <= END_DATE:
    dow = current.weekday()
    if dow < 5:
        weight = random.randint(18000, 33000)
    else:
        weight = random.randint(400, 2000)
    all_dates.append((current, weight))
    current += timedelta(days=1)

total_w     = sum(w for _, w in all_dates)
date_counts = []
assigned    = 0
for i, (dt, w) in enumerate(all_dates):
    if i == len(all_dates) - 1:
        count = NUM_RECORDS - assigned
    else:
        count = round(NUM_RECORDS * w / total_w)
    date_counts.append((dt, count))
    assigned += count

print(f"      {len(all_dates)} days planned")
print(f"      Total records to generate: {NUM_RECORDS:,}")

# -----------------------------------------------
# GENERATE RECORDS
# -----------------------------------------------
print("\n[2/4] Generating records...")

rows            = []
total_generated = 0

for base_date, count in date_counts:
    for _ in range(count):

        call_type   = np.random.choice(call_type_names, p=call_type_weights)
        client_idx  = np.random.choice(len(client_codes), p=client_probs)
        client_code = client_codes[client_idx]

        queue_type = random.choice(QUEUE_TYPES)
        if client_code == "CCC":
            queue = "CCC General"
        else:
            queue = f"[{str(client_idx+1).zfill(3)}]({client_code}) {queue_type}"

        if call_type in ("InboundHandledCall", "Callback", "TransferHandledCall"):
            agent        = random.choice(AGENT_POOL)
            agent_name   = agent["name"]
            agent_email  = agent["email"]
            company      = agent["company"]
            team         = agent["team"]
            group        = agent["group"]
            routing      = agent["routing"]
        else:
            agent_name   = None
            agent_email  = None
            company      = None
            team         = None
            group        = None
            routing      = None

        hour     = pick_hour()
        ctr_init = make_timestamp(base_date, hour)
        queue_s, handle_s, hold_s, acw_s, talk_s = make_durations(call_type)

        enqueue_ts     = ctr_init + timedelta(seconds=random.randint(5, 30))
        dequeue_ts     = enqueue_ts + timedelta(seconds=queue_s)
        conn_agent_ts  = dequeue_ts if call_type != "Abandoned" else None
        disc_ts        = dequeue_ts + timedelta(seconds=handle_s) if handle_s else dequeue_ts
        acw_start      = disc_ts if acw_s else None
        acw_end        = disc_ts + timedelta(seconds=acw_s) if acw_s else None

        if call_type == "Abandoned":
            disposition = None
        else:
            disposition = np.random.choice(disp_names, p=disp_probs)

        contact_id   = hash_id(uuid.uuid4())
        is_abandoned = call_type == "Abandoned"
        is_handled   = call_type != "Abandoned"
        handled_flag = "NonZeroInteractions" if is_handled else "ZeroInteractions"
        call_hour    = hour
        call_dow     = base_date.strftime("%A")

        rows.append({
            "contact_id":              contact_id,
            "date":                    base_date.strftime("%Y-%m-%d"),
            "ctr_init_tstamp_tz":      ctr_init.strftime("%Y-%m-%d %H:%M:%S"),
            "enqueue_tstamp_tz":       enqueue_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "dequeue_tstamp_tz":       dequeue_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "conn_to_agent_tstamp_tz": conn_agent_ts.strftime("%Y-%m-%d %H:%M:%S") if conn_agent_ts else None,
            "disc_tstamp_tz":          disc_ts.strftime("%Y-%m-%d %H:%M:%S"),
            "acw_start_tstamp_tz":     acw_start.strftime("%Y-%m-%d %H:%M:%S") if acw_start else None,
            "acw_end_tstamp_tz":       acw_end.strftime("%Y-%m-%d %H:%M:%S") if acw_end else None,
            "call_types":              call_type,
            "dispositions":            disposition,
            "queue":                   queue,
            "client_code":             client_code,
            "ctr_init_method":         np.random.choice(init_names, p=init_probs),
            "agent_full_name":         agent_name,
            "handled_by_agent":        agent_email,
            "agent_hierarchy_1_name":  company,
            "agent_hierarchy_2_name":  team,
            "agent_hierarchy_3_name":  group,
            "routing_profile_name":    routing,
            "handle_time_s":           handle_s if handle_s else None,
            "hold_duration_s":         hold_s if hold_s else None,
            "acw_duration_s":          acw_s if acw_s else None,
            "tlk_duration_s":          talk_s if talk_s else None,
            "queue_duration":          queue_s,
            "is_abandoned":            is_abandoned,
            "is_handled":              is_handled,
            "call_hour":               call_hour,
            "call_dow":                call_dow,
            "handled":                 handled_flag,
            "vm":                      None,
        })

    total_generated += count
    if total_generated % 50000 == 0:
        print(f"      Generated {total_generated:,} / {NUM_RECORDS:,} records...")

print(f"      Done — {total_generated:,} records generated")

# -----------------------------------------------
# BUILD DATAFRAME AND SAVE
# -----------------------------------------------
print("\n[3/4] Building dataframe...")
df = pd.DataFrame(rows)
print(f"      Shape: {df.shape}")

print("\n[4/4] Saving to CSV...")
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
df.to_csv(OUTPUT_PATH, index=False)
print(f"      Saved: {OUTPUT_PATH}")

# -----------------------------------------------
# VALIDATION
# -----------------------------------------------
print("\n" + "=" * 60)
print("VALIDATION SUMMARY")
print("=" * 60)
print(f"  Total rows:          {len(df):,}")
print(f"  Date range:          {df['date'].min()} to {df['date'].max()}")
print(f"\n  Call type breakdown:")
print(df['call_types'].value_counts().to_string())
print(f"\n  Client breakdown (top 5):")
print(df['client_code'].value_counts().head(5).to_string())
print(f"\n  Abandonment rate:    {df['is_abandoned'].mean()*100:.1f}%")
print(f"  Avg handle time:     {df['handle_time_s'].mean():.0f}s")
print(f"  Busiest hour:        {df['call_hour'].value_counts().idxmax()}:00")
print("=" * 60)
print("COMPLETE — synthetic data ready")
print("=" * 60)