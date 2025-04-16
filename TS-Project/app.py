#=====================================================================================================================================
#Imports
#=====================================================================================================================================

import flask as f
import csv
from io import StringIO, BytesIO
import os
import random

app = f.Flask(__name__)
app.secret_key = 'blah'
timetable_data = {}

#=====================================================================================================================================
#Sample accounts data
#=====================================================================================================================================

csv_file_name = 'users.csv'
users = {}
current_user = []

def load_users_from_csv():
    users.clear()
    try:
        with open(csv_file_name, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)
            for row in reader:
                if len(row) == 3:
                    username, password, acc_type = row
                    users[username] = [password, acc_type]
    except FileNotFoundError:
        pass

def save_user_to_csv(username, password, acc_type = "admin"):
    with open(csv_file_name, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not os.path.exists(csv_file_name) or os.path.getsize(csv_file_name) == 0:
            writer.writerow(['username', 'password', 'status']) 
        writer.writerow([username, password, acc_type])

load_users_from_csv()

#=====================================================================================================================================
#Main pages
#=====================================================================================================================================

#Home page --> Login page

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    f.session.pop('user', None)
    if 'user' not in f.session:       
        if f.request.method == 'POST':
            username = f.request.form['username']
            password = f.request.form['password']
            if username in users:
                if users[username][0] == password:
                    f.session['user'] = username
                    f.session['acc_type'] = users[username][1]
                    if f.session['acc_type'] == "admin":
                        return f.redirect(f.url_for('create_timetable'))
                    else:
                        return f.redirect(f.url_for('view_timetable'))
                else:
                    error = "Incorrect password." 
                    return f.render_template('login.html', login_error=error)
            else:
                error = "User does not exist."
                return f.render_template('login.html', login_error=error)
        return f.render_template('login.html')
    else: 
        return f.redirect(f.url_for('view_timetable'))

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
            users[new_username][0] = new_password
            save_user_to_csv(new_username, new_password)
            f.session['user'] = new_username
            if f.session['acc_type'] == "admin":
                return f.redirect(f.url_for('create_timetable'))
            else:
                return f.redirect(f.url_for('view_timetable'))
    return f.render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    return f.redirect(f.url_for('login'))

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
    if f.session['acc_type'] == "admin":
        timetable = f.session.get('timetable', [])
        return f.render_template('timetable_form.html', timetable=timetable)
    else:
        return f.redirect(f.url_for('view_timetable'))

#-----------------------------------------------------------------------------------------------------------------------------------

#Save timetable

@app.route('/timetable/save', methods=['POST'])
def save_timetable():
    if 'user' not in f.session:
        return f.redirect(f.url_for('login'))
    if f.session['acc_type'] == "admin":
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
    else:
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

@app.route('/creators')
def the_creators():
    return f.render_template('creators.html')

@app.route('/generate')
def generate():
    days_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    timetable_data = {}
    time_order = ["8:50 - 9:30", "9:50 - 10:10", "10:20 - 11:00", "11:00 - 11:40", "11:40 - 12:20", "12:50 - 1:30", "1:30 - 2:10", "2:10 - 2:50", "2:50 - 3:30"]
    subjects = ["Math", "English", "Chemistry", "Physics", "Art", "Music", "Biology", "Computer Science", "Dance", "Sports", "Volleyball", "MSA"]
    for time in time_order:  
        timetable_data[time] = {}  
        for day in days_order:
            timetable_data[time][day] = subjects[random.randint(0, 11)]
    f.session['timetable'] = timetable_data
    return f.render_template('timetable_display.html', days_order=days_order, timetable_data=timetable_data)
    

#=====================================================================================================================================
#App run
#=====================================================================================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5005)