from flask import Flask, render_template

app = Flask(__name__)

@app.route("/")
def root() -> str:
    return render_template("web.html")

@app.route("/dashboard")
def dashboard() -> str:
    return render_template("dashboard.html")

@app.route("/historic")
def historic() -> str:
    return render_template("historic.html")

@app.route("/alarms")
def alarms() -> str:
    return render_template("alarms.html")