import random
import json
import os
from tabulate import tabulate

# ---------------- CONFIG ----------------
CLASSES = 3       # number of classes
DAYS = 5          # Mon-Fri
PERIODS = 9       # periods per day
MAX_PER_DAY = 3   # max periods of a subject per day

subjects_weekly = {
    "Math": 7,
    "Chemistry": 7,
    "Physics": 7,
    "English": 5,
    "Computers": 7,
    "Art": 1,
    "Music": 2,
    "Dance": 2,
    "MSA": 2,
    "Sports": 5
}

# ---------------- COLOR HANDLING ----------------
RESET = "\033[0m"
COLOR_FILE = "subject_colors.json"

def random_bg_rgb():
    r = random.randint(50, 200)  # slightly muted so text is readable
    g = random.randint(50, 200)
    b = random.randint(50, 200)
    return f"\033[48;2;{r};{g};{b}m"

def load_colors():
    if os.path.exists(COLOR_FILE):
        with open(COLOR_FILE, "r") as f:
            return json.load(f)
    return {}

def save_colors(colors):
    with open(COLOR_FILE, "w") as f:
        json.dump(colors, f)

# Load or create colors
colors = load_colors()
for sub in subjects_weekly:
    if sub not in colors:
        colors[sub] = random_bg_rgb()
save_colors(colors)

# -------------- GENERATOR ----------------
def generate_timetable():
    class_subjects_left = {c: dict(subjects_weekly) for c in range(CLASSES)}
    timetable = {c: [["" for _ in range(PERIODS)] for _ in range(DAYS)] for c in range(CLASSES)}
    
    for day in range(DAYS):
        teachers_busy = [set() for _ in range(PERIODS)]
        daily_counts = {c: {sub: 0 for sub in subjects_weekly} for c in range(CLASSES)}
        
        for period in range(PERIODS):
            for c in range(CLASSES):
                possible_subjects = [
                    s for s in subjects_weekly
                    if class_subjects_left[c][s] > 0
                    and daily_counts[c][s] < MAX_PER_DAY
                    and s not in teachers_busy[period]
                ]
                
                if not possible_subjects:
                    return None
                
                subject = random.choice(possible_subjects)
                timetable[c][day][period] = subject
                class_subjects_left[c][subject] -= 1
                daily_counts[c][subject] += 1
                teachers_busy[period].add(subject)
    
    return timetable

# -------------- MAIN LOOP ----------------
attempts = 0
while True:
    attempts += 1
    timetable = generate_timetable()
    if timetable:
        print(f"\n✅ Generated successfully in {attempts} attempt(s)\n")
        break

# -------------- PRETTY PRINT -------------
days_names = ["Mon", "Tue", "Wed", "Thu", "Fri"]

def colorize_bg(sub):
    # Background color + black text
    return f"{colors.get(sub, '')}\033[30m {sub:^10} {RESET}"

for c in range(CLASSES):
    table_data = []
    for d in range(DAYS):
        table_data.append([days_names[d]] + [colorize_bg(sub) for sub in timetable[c][d]])
    
    headers = ["Day"] + [f"P{p+1}" for p in range(PERIODS)]
    print(f"\n📚 Class {c+1} Timetable")
    print(tabulate(table_data, headers=headers, tablefmt="fancy_grid"))
