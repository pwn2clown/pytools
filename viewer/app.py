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

    return render_template(
            "logs.html",
            session=session,
            logs=HttpDb.select()
        )

@app.route("/api/logs/full_packet/<packet_id>")
def full_packet(packet_id: int):
    try:
        packet = HttpDb.get_row_by_id(packet_id)
        return jsonify({
                "req": packet.to_dict()
            }), 200
    except Exception as e:
        print(f"packet no found for id {packet_id}: {e}")
        return jsonify({}), 404

@app.route('/project', methods=['POST'])
def select_project():
    session["current_project"] = request.form["project"]
    HttpDb.load_project(session["current_project"])
    return redirect("/logs")

if __name__ == '__main__':
    app.run(debug=True)
