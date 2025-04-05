import flask as f
from flask_bootstrap import Bootstrap5

app = f.Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'  # Replace with a strong secret key
bootstrap = Bootstrap5(app)

if __name__ == '__main__':
    from login import loginbp
else:
    from .login import loginbp

app.register_blueprint(loginbp, url_prefix='/login')

@app.route('/')
def index():
    return f.redirect(f.url_for('login.login'))

if __name__ == '__main__':
    app.run(debug=True)