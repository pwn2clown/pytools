from flask import Flask, session, render_template, redirect, request, jsonify
from flask_executor import Executor
from sqlalchemy import select
from bs4 import BeautifulSoup

#  Local sdk path for now
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../yatangaki-sdk-py')))
from db.http_db import *
from .proxy import start_proxy

app = Flask(__name__)
app.secret_key = "issou"
executor = Executor(app)

def is_project_loaded():
    return "current_project" in session.keys()

@app.route("/", methods=["GET", "POST"])
def index():
    session = {}
    db_basedir = db_basepath()
    if not db_basedir.exists():
        db_basedir.mkdir(parents=True)

    return render_template(
            "index.html",
            available_projects=[d.name for d in db_basedir.iterdir() if d.is_dir()]
        )

@app.route("/logs", methods=["GET", "POST"])
def logs():
    if not is_project_loaded():
        return redirect("/")

    inspected_request = None
    inspected_packet_id = None
    requets = None
    prettified_body = ""

    try:
        db_session = httpdb(session["current_project"])

        if request.args.get("packet_id"):
            inspected_packet_id = int(request.args.get("packet_id"))
            stmt = select(HttpRequest).where(HttpRequest.id == inspected_packet_id)
            inspected_request = db_session.execute(stmt).one()[0]
            
            #  prettify response
            if inspected_request.response:
                for header in inspected_request.response.headers:
                    if header.key.lower() == "content-type" and\
                            "text/html" in header.value.lower():

                        soup = BeautifulSoup(inspected_request.response.body, "html.parser")
                        prettified_body = soup.prettify() 

        stmt = select(HttpRequest).limit(25)
        requests = db_session.execute(stmt).all()

    except Exception as e:
        print(f"bad packet id format: {e}")

    return render_template(
            "logs.html",
            session=session,
            requests=requests,
            prettified_body=prettified_body,
            inspected_request=inspected_request,
            inspected_packet_id=inspected_packet_id,
        )

@app.route("/templates", methods=["POST"])
def templates():
    packet_id = 99
    return jsonify({ "packet_id": packet_id }), 200

@app.route("/editor", methods=["POST", "GET"])
def editor():
    packet_id = 99
    return jsonify({ "packet_id": packet_id }), 200

@app.route("/plugins", methods=["POST"])
def plugins():
    packet_id = 99
    return jsonify({ "packet_id": packet_id }), 200

@app.route("/issues", methods=["POST"])
def issues():
    packet_id = 99
    return jsonify({ "packet_id": packet_id }), 200

@app.route('/project', methods=['POST'])
def select_project():
    session["current_project"] = request.form["project"]
    executor.submit(start_proxy, 9000, httpdb(session["current_project"]))
    return redirect("/logs")

if __name__ == '__main__':
    app.run(debug=True)
