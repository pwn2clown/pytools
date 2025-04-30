from enum import Enum
from .db_connection import init_db_conn

class FilterKind(Enum):
    EndWith = 0
    Matches = 1
    Contains = 2
    StartsWith = 3
    Equals = 4

class Filter:
    def __init__(self, filter_kind: FilterKind, value: str):
        self.filter_kind = filter_kind
        self.value = value

class HttpLogsFilterBuilder:
    def __init__(self):
        self.url = None

    def with_url_filter(self, url_filter: Filter):
        self.url = url_filter
        return self

class HttpLogRow:
    def __init__(self, packet_id: int, method: str, authority: str, path: str, query: str):
        self.packet_id = packet_id
        self.method = method
        self.authority = authority
        self.path = path
        self.query = query

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
    def get_row_summary(cls, log_filter: Filter = None, limit=100):
        BASE_STMT = "SELECT packet_id, method, authority, path, query FROM requests;"

        packets = []

        cursor = cls.conn.cursor()
        cursor.execute(BASE_STMT)
        rows = cursor.fetchall()
        for (packet_id, method, authority, path, query) in rows:
            packet = HttpLogRow(packet_id, method, authority, path, query)
            packets.append(packet)
        return packets
