import os
import sqlite3
from pathlib import Path

BASEDIR = ".yatangaki"

def db_basepath():
    home_dir = os.environ.get("HOME")
    return Path(home_dir) / BASEDIR / "db"
