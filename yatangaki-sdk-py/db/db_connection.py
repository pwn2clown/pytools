import os
import sqlite3
from pathlib import Path

BASEDIR = ".yatangaki"

def db_basepath():
    home_dir = os.environ.get("HOME")
    return Path(home_dir) / BASEDIR / "db"

def init_db_conn(db_name: str, project_name: str) -> sqlite3.Connection:
    db_basedir = db_basepath() / "db" / project_name

    if not db_basedir.exists():
        db_basedir.mkdir(parents=True)

    db_path = db_basedir / f"{db_name}.db"

    return sqlite3.connect(str(db_path))
