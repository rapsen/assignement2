from flask import Flask, render_template
from datetime import datetime

from config import *
from controller import controller

# Create the flask application instance
app = Flask(__name__)


@app.route("/")
@app.route("/dashboard")
@app.route("/dashboard/<string:id>")
def dashboard_(id: str = controller.id):
    return render_template("dashboard.html", **controller.dashboard(id))


@app.route("/historic", methods=["GET", "POST"])
@app.route("/historic/<string:id>", methods=["GET", "POST"])
def historic(id: str = controller.id) -> str:
    return render_template("historic.html", **controller.historic(id))


@app.route("/alarms", methods=["GET", "POST"])
@app.route("/alarms/<string:id>", methods=["GET", "POST"])
def alarms(id: str = controller.id) -> str:
    return render_template("alarms.html", **controller.alarms(id))


# """ Backend for Web UI"""
#
# @app.route("/api/historic/")
# def historicdata():
#     # data = {"deviceId": "rob1", "state": "READY", "time": 1669476872}
#     inputdata = m.getRobEffBetTime("rob1", 1669476872, 1669812579)
#     data = json.dumps(inputdata)
#     return data
#
#
# @app.route("/api/realstate/")
# def realtimestate():
#     # data = {"deviceId": "rob1", "state": "READY", "time": 1669476872}
#     inputdata = m.getlaststate("rob2")
#     data = json.dumps(inputdata)
#     return data


@app.template_filter()
def timestamp2date(value, format="%d/%m/%y, %H:%M:%S"):
    # Convert to Helsinki timezone
    return datetime.fromtimestamp(value+60*60*2).strftime(format)
