from app.login import bp
import flask as f

users = {}

def validate_registration(username, email, password, confirm_password):
    errors = {}
    if not username:
        errors['username'] = 'Username is required.'
    if not email:
        errors['email'] = 'Email is required.'
    elif '@' not in email:
        errors['email'] = 'Invalid email address.'
    if not password:
        errors['password'] = 'Password is required.'
    elif password != confirm_password:
        errors['confirm_password'] = 'Passwords must match.'
    return errors

def validate_login(username, password):
    errors = {}
    if not username:
        errors['username'] = 'Username is required.'
    if not password:
        errors['password'] = 'Password is required.'
    return errors

def validate_forgot_password(email):
    errors = {}
    if not email:
        errors['email'] = 'Email is required.'
    elif '@' not in email:
        errors['email'] = 'Invalid email address.'
    return errors

def userExists(username,email,): 
    if username in users or email in [u['email'] for u in users.values()]:
        return True
    else :
        return False

@bp.route('/login/<action>', methods=['GET','POST'])
def login(action='login') :
    if action == 'register' :
        if f.request.method == 'POST' :
            username = f.request.form.get('username')
            email = f.request.form.get('email')
            password = f.request.form.get('password')
            confirm_password = f.request.form.get('confirm_password')
            registration_errors = validate_registration(username, email, password, confirm_password)
            if registration_errors == {} :
                if userExists(username,email) :
                    f.flash('Username or email already exists.', 'danger')
                else:
                    users[username] = {'email': email, 'password': password} # In real app, hash the password!
                    f.flash('Registration successful! Please log in.', 'success')
                    return f.redirect(f.url_for('login', action='login'))
        return f.render_template('login.html', action=action, registration_errors=registration_errors)

    elif action == 'login' :
        if f.request.method == 'POST':
            username = f.request.form.get('username')
            password = f.request.form.get('password')
            login_errors = validate_login(username, password)

            if not login_errors:
                if username in users and users[username]['password'] == password: 
                    f.flash(f'Login successful, {username}!', 'success')
                else:
                    f.flash('Invalid username or password.', 'danger')
        return f.render_template('login.html', action=action, login_errors=login_errors)
    
    elif action == 'forgot_password':
        if f.request.method == 'POST':
            email = f.request.form.get('email')
            forgot_password_errors = validate_forgot_password(email)

            if not forgot_password_errors:
                user_found = False
                for user in users.values():
                    if user['email'] == email:
                        f.flash('A password reset link has been sent to your email address.', 'info')
                        user_found = True
                        break
                if not user_found:
                    f.flash('Email address not found.', 'warning')
        return f.render_template('login.html', action=action, forgot_password_errors=forgot_password_errors)
    
    else:
        return f.redirect(f.url_for('login', action='login'))
