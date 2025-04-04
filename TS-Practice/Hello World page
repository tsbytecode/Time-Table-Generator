from flask import Flask, redirect, url_for

app = Flask(__name__)
username = ""

@app.route("/")
def home():
    return "Hello World"

@app.route("/<name>")
def user(name):
    username = name
    if username != "me":
        return redirect(url_for("home"))
    else:
        return "Admin Entrance"

if __name__ == "__main__":
    app.run()