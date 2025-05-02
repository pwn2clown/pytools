from flask import Flask, session, render_template, redirect, request, jsonify
import os, sys

#  Local sdk path for now
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../yatangaki-sdk-py')))
from db import init_db_conn, db_basepath
from db.http_db import HttpDb, HttpLogsFilterBuilder

app = Flask(__name__)
app.secret_key = "issou"

def is_project_loaded():
    return "current_project" in session.keys() and HttpDb.has_project_loaded()

@app.route("/", methods=["GET", "POST"])
def index():
    if is_project_loaded():
        return redirect("/logs")
      
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

    inspected_packet = None
    inspected_packet_id = None
    try:
        print(request.args.get("packet_id"))
        inspected_packet_id = int(request.args.get("packet_id"))
        inspected_packet = HttpDb.get_row_by_id(inspected_packet_id)
    except Exception as e:
        print(f"bad packet id format: {e}")

    return render_template(
            "logs.html",
            session=session,
            logs=HttpDb.select(),
            inspected_packet_id=inspected_packet_id,
            inspected_packet=inspected_packet
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
    HttpDb.load_project(session["current_project"])
    return redirect("/logs")

if __name__ == '__main__':
    #  Single threaded mode to avoid mutli thread issues with sqlite connections
    app.run(debug=True, threaded=False)
