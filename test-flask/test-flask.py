import flask as f
from flask_bootstrap import Bootstrap5 

app = f.Flask('__name__')
boot = Bootstrap5(app)
#ui = FlaskUI(app=app,server='flask')

@app.route('/')
@app.route('/login', methods=['GET','POST'])
def login () :
    if f.request.method == 'POST' :
        username = f.request.form['username']
        password = f.request.form['password']
        if username == 't' and password=='t' :
            return(f.url_for('success'))
        else :
            return f.redirect(f.url_for('login_error'))
    return f.render_template('login.html')

@app.route('/login_error', methods=['GET','POST'])
def login_error () :
    if f.request.method == 'POST' :
        username = f.request.form['username']
        password = f.request.form['password']
        if username == 't' and password=='t' :
            return f.redirect(f.url_for('success'))
        else :
            return f.redirect(f.url_for('login_error'))
    return f.render_template('login_error.html')

@app.route('/success')
def success():
    return "Login Successful"
