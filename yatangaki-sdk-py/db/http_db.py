from .db_connection import init_db_conn

class HttpLogsFilterBuilder:
    def __init__(self):
        self.url = None

class HttpDb:
    conn = None
    project_name = None

    @classmethod
    def load_project(cls, project_name: str):
        cls.conn = init_db_conn(db_name = "logs", project_name = project_name)

    @classmethod
    def has_project_loaded(cls):
        return True if cls.conn else False

    @classmethod
    def get_row_summary(cls, limit=100):
        print(cls.has_project_loaded())
        return 0
