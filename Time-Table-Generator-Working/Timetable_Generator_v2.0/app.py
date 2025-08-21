#=====================================================================================================================================
#Imports
#=====================================================================================================================================

import flask as f
import csv
import datetime
from io import StringIO, BytesIO
import os
import requests
import json
import sqlite3 as sql

app = f.Flask(__name__)
app.secret_key = 'code'

#=====================================================================================================================================
#Sample accounts data
#=====================================================================================================================================

CSV_FILENAME = r"Time-Table-Generator-Working\Timetable_Generator_v2.0\users.csv"
users = {}
reset_tokens = {}

def load_users_from_csv():
    users.clear()
    try:
        with open(CSV_FILENAME, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                if len(row) == 2:
                    username, password = row
                    users[username] = password
    except FileNotFoundError:
        pass

def save_user_to_csv(username, password):
    with open(CSV_FILENAME, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not os.path.exists(CSV_FILENAME) or os.path.getsize(CSV_FILENAME) == 0:
            writer.writerow(['username', 'password']) 
        writer.writerow([username, password])

load_users_from_csv()

#=====================================================================================================================================
#sql lite 
#=====================================================================================================================================


# The base URL for the Go API server. Change this if the server is running on a different port or host.
BASE_URL = "http://localhost:8080"

def create_assignment(teacher_id: str, class_id: str, periods_needed: int,subject:str) -> dict:
    """
    Sends a POST request to the /assignments endpoint to create a new assignment.

    Args:
        teacher_id (str): The ID of the teacher.
        class_id (str): The ID of the class.
        periods_needed (int): The number of periods required for the assignment.

    Returns:
        dict: A dictionary containing the JSON response from the API.
    """
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
        response.raise_for_status()  # This will raise an HTTPError if the response status is 4xx or 5xx
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def generate_timetable(class_id: str) -> dict:
    """
    Sends a POST request to the /generate-class endpoint to generate a timetable.

    Args:
        class_id (str): The ID of the class for which to generate the timetable.

    Returns:
        dict: A dictionary containing the JSON response from the API.
    """
    url = f"{BASE_URL}/generate-class"
    payload = {"class_id": class_id}
    headers = {"Content-Type": "application/json"}

    try:
        response = requests.post(url, data=json.dumps(payload), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": str(e)}

def output_timetable_csv(class_id: str, filename: str) -> dict:
    """
    Sends a POST request to the /output-csv endpoint to generate a CSV file on the server.

    Args:
        class_id (str): The ID of the class whose timetable to output.
        filename (str): The name of the file to save the CSV to on the server.

    Returns:
        dict: A dictionary containing the JSON response from the API.
    """
    url = f"{BASE_URL}/output-csv"
    payload = {
        "class_id": class_id,
        "filename": filename
    }
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
            if username in users:
                if users[username] == password:
                    f.session['user'] = username
                    return f.redirect(f.url_for('create_timetable'))
                else:
                    error = "Incorrect password." 
                    return f.render_template('login.html', login_error=error)
            else:
                error = "User does not exist."
                return f.render_template('login.html', login_error=error)
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

        if new_username in users:
            error = "Username already exists."
            return f.render_template('register.html', register_error=error)
        elif new_password != confirm_password:
            error = "Passwords do not match."
            return f.render_template('register.html', register_error=error)
        elif len(new_password) < 6:
            error = "Password must be at least 6 characters long."
            return f.render_template('register.html', register_error=error)
        else:
            users[new_username] = new_password
            save_user_to_csv(new_username, new_password)
            f.session['user'] = new_username
            return f.redirect(f.url_for('create_timetable'))
    return f.render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if f.request.method == 'POST':
        email = f.request.form['email']
        if email in users:
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
            for username, stored_email in users.items():
                if stored_email == email:
                    users[username] = new_password
                    save_all_users_to_csv()
                    del reset_tokens[token]
                    return f.redirect(f.url_for('login'))
            return f.render_template('message.html', message="Password reset successful. You can now log in.")

    return f.render_template('reset_password_form.html', token=token)

def save_all_users_to_csv():
    with open(CSV_FILENAME, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['username', 'password'])
        for username, password in users.items():
            writer.writerow([username, password])

#-----------------------------------------------------------------------------------------------------------------------------------

#Logout

@app.route('/logout')
def logout():
    f.session.pop('user', None)
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
                timetable_data.append({'day': day, 'time': time, 'subject': subject, 'teacher': teacher})
    f.session['timetable'] = timetable_data
    return f.redirect(f.url_for('view_timetable'))

# auto Create timetable

@app.route('/timetable/autocreate')
def auto_create_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    timetable = f.session.get('timetable', [])
    return f.render_template('timetable_form_auto.html', timetable=timetable)

#-----------------------------------------------------------------------------------------------------------------------------------

# autoSave timetable

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

    print(os.path.abspath(os.getcwd())+'/algo/x.db')
    conn = sql.connect(os.path.abspath(os.getcwd())+'/algo/x.db')
    conn.row_factory = sql.Row  # This allows you to access columns by name
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
    
    cursor = conn.execute(timetable_query, (cls,))
    imported_timetable = []
    
    for row in cursor.fetchall():
        imported_timetable.append({
            'day': row['day'],
            'time': row['time'],
            'subject': row['teacherid'],
            'teacher': row['teacherid']
        })
    
    conn.close()
    
    print(imported_timetable)

    # Store the retrieved data in the session
    f.session['timetable'] = imported_timetable
    
    # Redirect to the view timetable page
    return f.redirect(f.url_for('view_timetable'))


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
    app.run(debug=True, port=5005)