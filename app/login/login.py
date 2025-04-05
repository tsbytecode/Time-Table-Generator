import flask as f
import flask_wtf as fw
import wtforms as w
from . import loginbp

# Dummy user data (replace with a database in a real application)
users = {}

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

@loginbp.route('/register', methods=['GET', 'POST'])
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

@loginbp.route('/', methods=['GET', 'POST'])
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

@loginbp.route('/forgot-password', methods=['GET', 'POST'])
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