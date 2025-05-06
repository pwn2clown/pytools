import threading
import json
from pathlib import Path

from flask import Flask, session, render_template, redirect, request, jsonify
from sqlalchemy import select
from bs4 import BeautifulSoup

#  Local sdk path for now
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../yatangaki-sdk-py')))
from db.http_db import *

from .proxy import project_name, proxy_entrypoint
from .plugins import *

app = Flask(__name__)
app.secret_key = "issou"

def is_project_loaded():
    return "current_project" in session.keys()

@app.route("/project", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        db_basedir = db_basepath()
        if not db_basedir.exists():
            db_basedir.mkdir(parents=True)

        return render_template(
                "index.html",
                available_projects=[d.name for d in db_basedir.iterdir() if d.is_dir()]
            )
    elif request.method == "POST":
        session["current_project"] = request.form["project"]
        return redirect("/logs")

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

@app.route("/templates")
def templates():
    return render_template(
            "template_editor.html"
        )

@app.route("/editor")
def editor():
    return render_template(
            "request_editor.html"
        )

@app.route("/plugins", methods=["GET", "POST"])
def plugins():
    config_dir = Path(os.environ["HOME"]) / ".yatangaki" / "plugins"

    plugins = []

    for plugin in [d for d in config_dir.iterdir() if d.is_dir()]:
        try:
            f = open(f"{plugin}/plugin.json", "r")
            plugin_config = json.loads(f.read())
            f.close()

            plugins.append(Plugin("test", plugin_config))
            print(f"plugin {plugin} loaded successfully")
        except Exception as e:
            print(f"failed to load template: {e}")

    return render_template(
            "plugins.html",
            plugins=plugins
        )

@app.route("/issues")
def issues():
    return render_template(
            "issues.html"
        )

if __name__ == '__main__':
    """
    pxy_task = threading.Thread(target=proxy_entrypoint)
    pxy_task.daemon = True
    pxy_task.start()
    """
    app.run(debug=True)
