from flask import Flask, render_template, request

from config import *
from controller import controller, mqtt, socket
from model import model

# Create the flask application
app = Flask(__name__)

app.config['MQTT_BROKER_URL'] = BROKER_HOSTNAME
app.config['MQTT_BROKER_PORT'] = BROKER_PORT
app.config['MQTT_KEEPALIVE'] = 60
app.config['MQTT_TLS_ENABLED'] = False


@app.route("/")
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    id = request.form['id'] if request.method == "POST" else None
    id, state, time, status = controller.dashboard(id)
    print(id, state, time, status)
    return render_template("dashboard.html", id=id, state=state, time=time, status=status, robots=model.robots)


@app.route("/historic")
def historic() -> str:
    id, robots = controller.historic()
    return render_template("historic.html", id=id, robots=model.robots)


@app.route("/alarms")
def alarms() -> str:
    id = controller.alarms()
    return render_template("alarms.html", id=id)
