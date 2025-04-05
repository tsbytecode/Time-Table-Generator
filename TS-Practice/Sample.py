import flask

app = flask.Flask(__name__)

@app.route("/")
def home_page():
    return flask.render_template("home_page.html")

@app.route("/login/")
def login_page(method = ["POST", "GET"]):
    return flask.render_template("login_page.html")

if __name__ == "__main__":
    app.run(debug = True)