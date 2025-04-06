#====================================================================================================================================
#Imports
#====================================================================================================================================

import flask as f
import csv
import datetime
from io import StringIO
import flask_wtf as fw
import wtforms as w
from flask_bootstrap import Bootstrap5


app = f.Flask(__name__)
app.secret_key = 'blah'
bootstrap = Bootstrap5(app)


#====================================================================================================================================
#Converting date and time from import to version to save as export names for csv
#====================================================================================================================================

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


#====================================================================================================================================
#Sample accounts data
#====================================================================================================================================
users = {
    'user1': {'password': 'pass1'},
    'user2': {'password': 'pass2'}
        }


#====================================================================================================================================
#Main pages
#====================================================================================================================================

#Home page --> Login page

class RegistrationForm(fw.FlaskForm):
    username = w.StringField('Username', validators=[w.validators.DataRequired()])
    email = w.StringField('Email', validators=[w.validators.DataRequired(), w.validators.Email()])
    password = w.PasswordField('Password', validators=[w.validators.DataRequired(), w.validators.EqualTo('confirm_password', message='Passwords must match')])
    confirm_password = w.PasswordField('Confirm Password', validators=[w.validators.DataRequired()])
    submit = w.SubmitField('Register')

class LoginForm(fw.FlaskForm):
    username = w.StringField('Username', validators=[w.validators.DataRequired()])
    password = w.PasswordField('Password', validators=[w.validators.DataRequired()])
    submit = w.SubmitField('Login')

class ForgotPasswordForm(fw.FlaskForm):
    email = w.StringField('Email', validators=[w.validators.DataRequired(), w.validators.Email()])
    submit = w.SubmitField('Request Password Reset')

@app.route('/login/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data
        password = form.password.data
        if username in users or email in [u['email'] for u in users.values()]:
            f.flash('Username or email already exists.', 'danger')
        else:
            users[username] = {'email': email, 'password': password} # In real app, hash the password!
            f.flash('Registration successful! Please log in.', 'success')
            return f.redirect(f.url_for('login.login'))
    return f.render_template('login.html', form=form, action='register')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in users and users[username]['password'] == password: # In real app, compare hashed passwords!
            f.flash(f'Login successful, {username}!', 'success')
            return f.redirect(f.url_for('home')) # Redirect to your main application's home route
        else:
            f.flash('Invalid username or password.', 'danger')
    return f.render_template('login.html', form=form, action='login')

@app.route('/login/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    form = ForgotPasswordForm()
    if form.validate_on_submit():
        email = form.email.data
        user_found = False
        for user in users.values():
            if user['email'] == email:
                # In a real app, you'd generate a reset token, save it, and send an email
                f.flash('A password reset link has been sent to your email address.', 'info')
                user_found = True
                break
        if not user_found:
            f.flash('Email address not found.', 'warning')
    return f.render_template('login.html', form=form, action='forgot_password')

@app.route('/')
def index():
    return f.redirect(f.url_for('login'))

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if f.request.method == 'POST':
#         username = f.request.form['username']
#         password = f.request.form['password']
#         user = users.get(username)
#         if user and user['password'] == password:
#             f.session['user'] = username
#             return f.redirect(f.url_for('create_timetable'))
#         else:
#             error = 'Invalid username or password'
#             return f.render_template('login.html', error=error)
#     return f.render_template('login.html')

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
    cw = csv.writer(si)
    cw.writerow(['Day', 'Time Slot', 'Subject', 'Teacher'])  # Write header

    for entry in timetable_data:
        cw.writerow([entry['day'], entry['time'], entry['subject'], entry['teacher']])

    output = si.getvalue()
    si.seek(0)

    return f.send_file(si, mimetype='text/csv', as_attachment=True, download_name=f'timetable{time_to_save}.csv')

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
    

#====================================================================================================================================
#App run
#====================================================================================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5005)