#=====================================================================================================================================
#Imports
#=====================================================================================================================================

import flask as f
import csv
from io import StringIO, BytesIO
import os
import requests
import json
import sqlite3 as sql

app = f.Flask(__name__)
app.secret_key = 'code'

#=====================================================================================================================================
#users sql
#=====================================================================================================================================

reset_tokens = {}

class UserDBManager:
    def __init__(self, path):
        try:
            self.conn = sql.connect(path, check_same_thread=False)
            self.conn.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    userid TEXT,
                    level TEXT,
                    password TEXT,
                    PRIMARY KEY(userid, level)
                )
            """)
            self.conn.commit()
            print("Successfully connected to the database and ensured 'users' table exists.")
        except sql.Error as e:
            print(f"Database connection error: {e}")
            self.conn = None

    def get_password(self, userid):
        if not self.conn:
            print('conn failed')
            return (None, False)
        try:
            cursor = self.conn.execute("SELECT password FROM users WHERE userid = ?", (userid,))
            results = cursor.fetchall()
            if results:
                print(results, results[0][0])
                return (results[0][0], True)
            else:
                print(userid,results)
                return (None, False)
        except sql.Error as e:
            print(f"Error fetching password: {e}")
            return (None, False)

    def add_user(self, userid, level, password):
        if not self.conn:
            return False
        try:
            self.conn.execute("INSERT INTO users (userid, level, password) VALUES (?, ?, ?)", (userid, level, password))
            self.conn.commit()
            print(f"User '{userid}' added successfully.")
            return True
        except sql.IntegrityError:
            print(f"Error: User '{userid}' with level '{level}' already exists.")
            return False
        except sql.Error as e:
            print(f"Error adding user: {e}")
            return False

    def change_password(self, userid, new_password):
        if not self.conn:
            return False
        try:
            cursor = self.conn.execute("UPDATE users SET password = ? WHERE userid = ?", (new_password, userid))
            self.conn.commit()
            if cursor.rowcount > 0:
                print(f"Password for user '{userid}' changed successfully.")
                return True
            else:
                print(f"Error: User '{userid}' not found.")
                return False
        except sql.Error as e:
            print(f"Error changing password: {e}")
            return False

    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")

userdb_path = "users.db"
userdb = UserDBManager(userdb_path)

#=====================================================================================================================================
#sql lite 
#=====================================================================================================================================

BASE_URL = "http://localhost:8080"

timetabledb = sql.connect('x.db',check_same_thread=False)


def create_assignment(teacher_id: str, class_id: str, periods_needed: int,subject:str):
    url = f"{BASE_URL}/assignments"
    payload = {
        "teacher_id": teacher_id,
        "class_id": class_id,
        "periods_needed": int(periods_needed),
        "subject" : subject
    }
    headers = {"Content-Type": "application/json"}
    print(payload)

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def generate_timetable(class_id: str):
    url = f"{BASE_URL}/generate-class"
    payload = {"class_id": class_id}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}


#=====================================================================================================================================
#Main pages
#=====================================================================================================================================

#Home page --> Login page

@app.route('/', methods=['GET', 'POST'])
def home():    
    f.session.pop('user', None)
    return f.redirect(f.url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user' not in f.session:       
        if f.request.method == 'POST':
            username = f.request.form['username']
            password = f.request.form['password']
            userdata = userdb.get_password(username)
            print(userdata)
            if userdata[1]:
                if userdata[0] == password:
                    f.session['user'] = username
                    return f.redirect(f.url_for('create_timetable'))
                else:
                    return f.render_template('login.html', login_error = "Incorrect Password")
            else:
                return f.render_template('login.html', login_error = "User does not exist")
        return f.render_template('login.html')
    else:
        return f.redirect(f.url_for('create_timetable'))

#-----------------------------------------------------------------------------------------------------------------------------------

@app.route('/register', methods=['GET', 'POST'])
def register():
    if f.request.method == 'POST':
        new_username = f.request.form['new_username']
        new_password = f.request.form['new_password']
        confirm_password = f.request.form['confirm_password']
        userdata = userdb.get_password(new_username)
        if userdata[1]:
            error = "Username already exists."
            return f.render_template('register.html', register_error=error)
        elif new_password != confirm_password:
            error = "Passwords do not match."
            return f.render_template('register.html', register_error=error)
        elif len(new_password) < 6:
            error = "Password must be at least 6 characters long."
            return f.render_template('register.html', register_error=error)
        else:
            userdb.add_user(new_username,'admin',new_password)
            f.session['user'] = new_username
            return f.redirect(f.url_for('create_timetable'))
    return f.render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if f.request.method == 'POST':
        email = f.request.form['email']
        userdata = userdb.get_password(email)
        if userdata[1]:
            token = os.urandom(16).hex()
            reset_tokens[token] = email
            message = f"A password reset link has been sent to the (simulated) email address: {email}. The link is: {f.url_for('reset_password', token=token, _external=True)}"
            return f.render_template('forgot_password.html', forgot_password_message=message)
        else:
            error = "Username (as email proxy) not found."
            return f.render_template('forgot_password.html', forgot_password_error=error)
    return f.render_template('forgot_password.html')

@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if token not in reset_tokens:
        return f.render_template('message.html', message="Invalid or expired reset link.")
    email = reset_tokens[token]
    if f.request.method == 'POST':
        new_password = f.request.form['new_password']
        confirm_password = f.request.form['confirm_password']
        if new_password != confirm_password:
            return f.render_template('reset_password_form.html', token=token, error="Passwords do not match.")
        elif len(new_password) < 6:
            return f.render_template('reset_password_form.html', token=token, error="Password must be at least 6 characters long.")
        else:
            userdb.change_password(email,new_password=new_password)
            del reset_tokens[token]
            return f.redirect(f.url_for('login'))
        return f.render_template('message.html', message="Password reset successful. You can now log in.")

    return f.render_template('reset_password_form.html', token=token)


#-----------------------------------------------------------------------------------------------------------------------------------

#Logout

@app.route('/logout')
def logout():
    f.session.clear()
    return f.redirect(f.url_for('login'))

#-----------------------------------------------------------------------------------------------------------------------------------

#Create timetable

@app.route('/timetable/create')
def create_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    timetable = f.session.get('timetable', [])
    return f.render_template('timetable_form.html', timetable=timetable)

#-----------------------------------------------------------------------------------------------------------------------------------

#Save timetable

@app.route('/timetable/save', methods=['POST'])
def save_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    timetable_data = []
    for key, value in f.request.form.items():
        if key.startswith('day_'):
            index = key.split('_')[1]
            day = value
            time = f.request.form.get(f'time_{index}')
            subject = f.request.form.get(f'subject_{index}')
            teacher = f.request.form.get(f'teacher_{index}', '')
            if time and subject and day:
                timetable_data.append({
                    'day': day,
                    'time': time,
                    'subject': subject,
                    'teacher': teacher
                    })
    f.session['timetable'] = timetable_data
    return f.redirect(f.url_for('view_timetable'))

#Auto Create timetable

@app.route('/timetable/autocreate')
def auto_create_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    timetable = f.session.get('timetable', [])
    return f.render_template('timetable_form_auto.html', timetable=timetable)


#-----------------------------------------------------------------------------------------------------------------------------------
# Auto Save timetable


# Helper function to convert app's day format to DB's day format
def convert_day_to_db(day_name):
    day_map = {
        'Monday': 'mon',
        'Tuesday': 'tue',
        'Wednesday': 'wed',
        'Thursday': 'thu',
        'Friday': 'fri'
    }
    return day_map.get(day_name, '')

# Helper function to convert app's time format to DB's period number
def convert_time_to_periodno(time_slot):
    period_map = {
        '8:50 - 9:30': 1,
        '9:30 - 10:10': 2,
        '10:20 - 11:00': 3,
        '11:00 - 11:40': 4,
        '11:40 - 12:20': 5,
        '12:50 - 13:30': 6,
        '13:30 - 14:10': 7,
        '14:10 - 14:50': 8,
        '14:50 - 15:30': 9
    }
    return period_map.get(time_slot, 0)


@app.route('/timetable/save_timetable_to_db', methods=['POST'])
def save_timetable_to_db():
    cls = f.request.form.get('class')
        # Make sure the user is logged in and there is a timetable in the session
    if 'user' not in f.session or 'timetable' not in f.session:
        return f.redirect(f.url_for('login'))

    cursor = timetabledb.cursor()
    
    # Get the timetable from the session
    imported_timetable = f.session.get('timetable', [])
    if not imported_timetable:
        print("No timetable data found in session.", 400)   
    
    # Clear existing data for the class to prevent duplicates
    cursor.execute("DELETE FROM periods WHERE classID = ?", (cls,))

    # Insert new timetable data
    for period in imported_timetable:
        db_day = convert_day_to_db(period.get('day'))
        db_period_no = convert_time_to_periodno(period.get('time'))
        
        # Ensure data is valid before insertion
        if not all([db_day, db_period_no]):
            # Skip invalid periods or handle the error as needed
            continue

        teacherid = ''
        if not period.get('teacherid') :
            if not period.get('subject') :
                teacherid = 'na'
            else :
                teacherid = period.get('subject')
        else :
            teacherid = period.get(teacherid)

        cursor.execute(
            "INSERT INTO periods (classID, day, periodno, subject, teacherid) VALUES (?, ?, ?, ?, ?)",
            (cls, db_day, db_period_no, period.get('subject'), teacherid)
        )

    timetabledb.commit()
    
    return f.redirect(f.url_for('view_timetable'))

    


@app.route('/timetable/get_timetable', methods=['POST'])
def get_timetable_from_db():
    cls = f.request.form.get('class')
    timetabledb.row_factory = sql.Row
    timetable_query = """
    SELECT
        CASE day
            WHEN 'mon' THEN 'Monday'
            WHEN 'tue' THEN 'Tuesday'
            WHEN 'wed' THEN 'Wednesday'
            WHEN 'thu' THEN 'Thursday'
            WHEN 'fri' THEN 'Friday'
            ELSE 'Unknown'
        END AS day,
        CASE periodno
            WHEN 1 THEN '8:50 - 9:30'
            WHEN 2 THEN '9:30 - 10:10'
            WHEN 3 THEN '10:20 - 11:00'
            WHEN 4 THEN '11:00 - 11:40'
            WHEN 5 THEN '11:40 - 12:20'
            WHEN 6 THEN '12:50 - 13:30'
            WHEN 7 THEN '13:30 - 14:10'
            WHEN 8 THEN '14:10 - 14:50'
            WHEN 9 THEN '14:50 - 15:30'
        END AS time,
        teacherid
    FROM periods
    WHERE classID = ?
    ORDER BY day, periodno
    """
    
    cursor = timetabledb.execute(timetable_query, (cls,))
    imported_timetable = []
    
    for row in cursor.fetchall():
        imported_timetable.append({
            'day': row['day'],
            'time': row['time'],
            'subject': row['teacherid'],
            'teacher': row['teacherid']
        })
    
    
    f.session['timetable'] = imported_timetable
    return f.redirect(f.url_for('view_timetable'))



@app.route('/timetable/autosave', methods=['POST'])
def auto_save_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    cls = ''
    for key, value in f.request.form.items():
        if key.startswith('teacher_'):
            index = key.split('_')[1]
            teacher = value
            subject = f.request.form.get(f'subject_{index}')
            num_class = f.request.form.get(f'num_classes_{index}')
            print(create_assignment(teacher,cls,num_class,subject))            
        elif key.startswith('class_name') :
            cls = value.strip()
    
    print(generate_timetable(cls))

    timetabledb.row_factory = sql.Row
    timetable_query = """
    SELECT
        CASE day
            WHEN 'mon' THEN 'Monday'
            WHEN 'tue' THEN 'Tuesday'
            WHEN 'wed' THEN 'Wednesday'
            WHEN 'thu' THEN 'Thursday'
            WHEN 'fri' THEN 'Friday'
            ELSE 'Unknown'
        END AS day,
        CASE periodno
            WHEN 1 THEN '8:50 - 9:30'
            WHEN 2 THEN '9:30 - 10:10'
            WHEN 3 THEN '10:20 - 11:00'
            WHEN 4 THEN '11:00 - 11:40'
            WHEN 5 THEN '11:40 - 12:20'
            WHEN 6 THEN '12:50 - 13:30'
            WHEN 7 THEN '13:30 - 14:10'
            WHEN 8 THEN '14:10 - 14:50'
            WHEN 9 THEN '14:50 - 15:30'
        END AS time,
        teacherid,
        subject
    FROM periods
    WHERE classID = ?
    ORDER BY day, periodno
    """
    
    cursor = timetabledb.execute(timetable_query, (cls,))
    imported_timetable = []
    
    for row in cursor.fetchall():
        imported_timetable.append({
            'day': row['day'],
            'time': row['time'],
            'subject': row['subject'],
            'teacher': row['teacherid']
        })
    
    
    print(imported_timetable)

    # Store the retrieved data in the session
    f.session['timetable'] = imported_timetable

    return f.redirect(f.url_for('view_timetable'))
    
    # Redirect to the view timetable page
   


def getTimetables() :
    query = "SELECT DISTINCT classID from periods"
    cursor = timetabledb.execute(query)
    classes = []
    for loop in cursor.fetchall() :
        classes.append(loop[0])
    return classes

#-----------------------------------------------------------------------------------------------------------------------------------

#View timetable

@app.route('/timetable/view')
def view_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    timetable_data = f.session.get('timetable', [])
    structured_timetable = {}
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

    for entry in timetable_data:
        time = entry['time']
        day = entry['day']
        subject = entry['subject']
        teacher = entry['teacher']
        if time not in structured_timetable:
            structured_timetable[time] = {}
        structured_timetable[time][day] = f"{subject} ({teacher})" if teacher else subject

    sorted_timetable = dict(structured_timetable.items())

    return f.render_template('timetable_display.html', timetable_data=sorted_timetable, days_order=days_order)

#-----------------------------------------------------------------------------------------------------------------------------------

#Export timetable

@app.route('/timetable/export')
def export_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    timetable_data = f.session.get('timetable', [])
    if not timetable_data:
        return "No timetable data to export."

    si = StringIO()
    writer = csv.writer(si)
    writer.writerow(['Day', 'Time Slot', 'Subject', 'Teacher'])

    for entry in timetable_data:
        writer.writerow([entry['day'], entry['time'], entry['subject'], entry['teacher']])

    output = si.getvalue().encode("utf-8")
    bio = BytesIO(output)
    bio.seek(0)

    return f.send_file(bio, mimetype='text/csv', as_attachment=True, download_name='timetable.csv')
#-----------------------------------------------------------------------------------------------------------------------------------

#Import and export control

@app.route('/timetable/import_export')
def import_export():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    return f.render_template('timetable_import_export.html')

#-----------------------------------------------------------------------------------------------------------------------------------

#Import timetable

@app.route('/timetable/import', methods=['POST'])
def import_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))

    if 'csv_file' not in f.request.files:
        return "No file part"
    file = f.request.files['csv_file']
    if file.filename == '':
        return "No selected file"
    if file and file.filename.endswith('.csv'):
        csv_data = file.stream.read().decode('utf-8')
        si = StringIO(csv_data)
        reader = csv.reader(si)
        header = next(reader, None)

        imported_timetable = []
        for row in reader:
            if len(row) == 4:
                day, time, subject, teacher = row
                imported_timetable.append({'day': day, 'time': time, 'subject': subject, 'teacher': teacher})
            elif len(row) == 3:
                day, time, subject = row
                imported_timetable.append({'day': day, 'time': time, 'subject': subject, 'teacher': ''})
            else:
                return "Invalid CSV format: Each row should have 3 or 4 columns (Day, Time Slot, Subject, Teacher)."

        f.session['timetable'] = imported_timetable
        return f.redirect(f.url_for('view_timetable'))
    else:
        return "Please upload a CSV file."
    
@app.route('/timetable/import')
def timetable_import():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    return f.render_template('timetable_import.html')

#-----------------------------------------------------------------------------------------------------------------------------------

#Creators page

@app.route('/creators')
def the_creators():
    return f.render_template('creators.html')

#=====================================================================================================================================
#App run
#=====================================================================================================================================

if __name__ == '__main__':
    app.run(debug = True, port = 5005)