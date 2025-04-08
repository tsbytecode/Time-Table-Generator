#=====================================================================================================================================
#Imports
#=====================================================================================================================================

import flask as f
import csv
import datetime
from io import StringIO, BytesIO
import os

app = f.Flask(__name__)
app.secret_key = 'blah'

#=====================================================================================================================================
#Sample accounts data
#=====================================================================================================================================

CSV_FILENAME = 'users.csv'
users = {}
reset_tokens = {}

def load_users_from_csv():
    users.clear()
    try:
        with open(CSV_FILENAME, 'r', newline='') as csvfile:
            reader = csv.reader(csvfile)
            next(reader, None)  # Skip the header row if it exists
            for row in reader:
                if len(row) == 2:
                    username, password = row
                    users[username] = password
    except FileNotFoundError:
        pass  # It's okay if the file doesn't exist yet

def save_user_to_csv(username, password):
    with open(CSV_FILENAME, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not os.path.exists(CSV_FILENAME) or os.path.getsize(CSV_FILENAME) == 0:
            writer.writerow(['username', 'password'])  # Write header if the file is new or empty
        writer.writerow([username, password])

load_users_from_csv()  # Load users when the application starts

#=====================================================================================================================================
#Main pages
#=====================================================================================================================================

#Home page --> Login page

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if f.request.method == 'POST':
        username = f.request.form['username']
        password = f.request.form['password']
        if username in users:
            if users[username] == password:
                f.session['user'] = username
                return f.redirect(f.url_for('create_timetable'))
            else:
                error = "Incorrect password."  # Specific error for wrong password
                return f.render_template('login.html', login_error=error)
        else:
            error = "User does not exist."  # Specific error for non-existent user
            return f.render_template('login.html', login_error=error)
    return f.render_template('login.html')

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
            save_user_to_csv(new_username, new_password)  # Save the new user to CSV
            f.session['user'] = new_username
            return f.redirect(f.url_for('create_timetable'))
    return f.render_template('register.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if f.request.method == 'POST':
        email = f.request.form['email']
        # In this simplified example, we'll use the username as a proxy for email for demonstration
        if email in users:
            # Generate a simple reset token (insecure in real app!)
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
            # In this simplified example, we'll use the username as the key
            for username, stored_email in users.items():
                if stored_email == email:
                    users[username] = new_password # Reset the password (insecure in real app!)
                    save_all_users_to_csv()
                    del reset_tokens[token]
                    return f.redirect(f.url_for('login'))
            return f.render_template('message.html', message="Password reset successful. You can now log in.")

    return f.render_template('reset_password_form.html', token=token)

def save_all_users_to_csv():
    with open(CSV_FILENAME, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['username', 'password'])  # Write header
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

    sorted_timetable = dict(sorted(structured_timetable.items()))

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
        header = next(reader, None)  # Skip header if present

        imported_timetable = []
        for row in reader:
            if len(row) == 4:
                day, time, subject, teacher = row
                imported_timetable.append({'day': day, 'time': time, 'subject': subject, 'teacher': teacher})
            elif len(row) == 3: # Handle cases without teacher
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

#=====================================================================================================================================
#App run
#=====================================================================================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5005)