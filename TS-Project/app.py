from flask import Flask, render_template, request, redirect, url_for, session, send_file
import csv
import datetime
from io import StringIO

exact_time = datetime.datetime.now()
time_to_save = ""
for i, j in enumerate(str(exact_time)):
    if i >= 20:
        break
    else:    
        if j in " -.:":
            continue
        else:
            time_to_save += j

app = Flask(__name__)
app.secret_key = 'blah'

users = {
    'user1': {'password': 'pass1'},
    'user2': {'password': 'pass2'}
}

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = users.get(username)
        if user and user['password'] == password:
            session['user'] = username
            return redirect(url_for('create_timetable'))
        else:
            error = 'Invalid username or password'
            return render_template('login.html', error=error)
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/timetable/create')
def create_timetable():
    if 'user' not in session:
        return redirect(url_for('login'))
    timetable = session.get('timetable', [])
    return render_template('timetable_form.html', timetable=timetable)

@app.route('/timetable/save', methods=['POST'])
def save_timetable():
    if 'user' not in session:
        return redirect(url_for('login'))
    timetable_data = []
    for key, value in request.form.items():
        if key.startswith('day_'):
            index = key.split('_')[1]
            day = value
            time = request.form.get(f'time_{index}')
            subject = request.form.get(f'subject_{index}')
            teacher = request.form.get(f'teacher_{index}', '')
            if time and subject and day:
                timetable_data.append({'day': day, 'time': time, 'subject': subject, 'teacher': teacher})
    session['timetable'] = timetable_data
    return redirect(url_for('view_timetable'))

@app.route('/timetable/view')
def view_timetable():
    if 'user' not in session:
        return redirect(url_for('login'))
    timetable_data = session.get('timetable', [])
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

    return render_template('timetable_display.html', timetable_data=sorted_timetable, days_order=days_order)

@app.route('/timetable/export')
def export_timetable():
    if 'user' not in session:
        return redirect(url_for('login'))
    timetable_data = session.get('timetable', [])
    if not timetable_data:
        return "No timetable data to export."

    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(['Day', 'Time Slot', 'Subject', 'Teacher'])  # Write header

    for entry in timetable_data:
        cw.writerow([entry['day'], entry['time'], entry['subject'], entry['teacher']])

    output = si.getvalue()
    si.seek(0)

    return send_file(si, mimetype='text/csv', as_attachment=True, download_name=f'timetable{time_to_save}.csv')

@app.route('/timetable/import_export')
def import_export():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('timetable_import_export.html')

@app.route('/timetable/import', methods=['POST'])
def import_timetable():
    if 'user' not in session:
        return redirect(url_for('login'))

    if 'csv_file' not in request.files:
        return "No file part"
    file = request.files['csv_file']
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

        session['timetable'] = imported_timetable
        return redirect(url_for('view_timetable'))
    else:
        return "Please upload a CSV file."

if __name__ == '__main__':
    app.run(debug=True, port=5005)