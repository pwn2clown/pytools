from enum import Enum
from .db_connection import init_db_conn

class FilterKind(Enum):
    EndsWith = 0
    Matches = 1
    Contains = 2
    StartsWith = 3
    Equals = 4

    def parse(raw: str):
        match raw:
            case "ends_with":
                return FilterKind.EndsWith
            case "matches":
                return FilterKind.Matches
            case "contains":
                return FilterKind.Contains
            case "starts_with":
                return FilterKind.StartsWith
            case "equals":
                return FilterKind.Equals
            case _:
                raise Exception(f"Bad filter kind value: \"{raw}\"")


class Filter:
    def __init__(self, filter_kind: FilterKind, value: str):
        self.filter_kind = filter_kind
        self.value = value

    def try_from(raw: str):
        splitted = raw.split(':')
        if len(splitted) != 2:
            raise Exception(f"invalid filter format on \"{raw}\"")

        (kind, value) = tuple(splitted)
        filter_kind = FilterKind.parse(kind)

        return Filter(filter_kind, value)


class HttpLogsFilterBuilder:
    def __init__(self):
        self.path = None

    def with_path_filter(self, path_filter: str):
        self.path = Filter.try_from(path_filter)
        return self

class HttpResponse:
    def __init__(self,
            packet_id: int,
            status: int,
            headers: dict,
            body: bytes
        ):
        
        self.packet_id = packet_id
        self.status = status
        self.headers = headers
        self.body = body

    def to_dict(self) -> dict:
        return {
                "packet_id": packet_id,
                "status": self.status,
                "headers": self.headers,
                "body": self.body.decode("utf-8")
            }

class HttpResquest:
    def __init__(self,
            packet_id: int,
            method: str,
            authority: str,
            path: str,
            query: str,
            headers: dict,
            body: bytes
        ):
        
        self.packet_id = packet_id
        self.method = method
        self.authority = authority
        self.path = path
        self.query = query
        self.headers = headers
        self.body = body

    def to_dict(self) -> dict:
        return {
                "packet_id": self.packet_id,
                "method": self.method,
                "authority": self.authority,
                "path": self.path,
                "query": self.query,
                "headers": self.headers,
                "body": self.body.decode("utf-8")
            }

class HttpLogRow:
    def __init__(self,
            packet_id: int,
            request: HttpResquest,
            response: HttpResponse
        ):

        self.packet_id = packet_id
        self.request = request
        self.response = response

    def to_dict(self) -> dict:
        return {
                "packet_id": self.packet_id,
                "request": self.request.to_dict(),
                "response": self.response.to_dict() if self.response else {}
            }

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
    def get_row_by_id(cls, packet_id: int) -> HttpLogRow:
        request = cls.get_request_by_id(packet_id)
        response = cls.get_response_by_id(packet_id)

        return HttpLogRow(packet_id, request, response)
    
    @classmethod
    def get_response_by_id(cls, packet_id: int) -> HttpResponse:
        try:
            cursor = cls.conn.cursor()
            cursor.execute("SELECT status, body FROM request_headers WHERE packet_id=?", [packet_id])
            (status, body) = cursor.fetchone()

            headers = {}
            cursor.execute("SELECT key, value FROM request_headers WHERE packet_id=?", [packet_id])
            for (k, v) in cursor.fetchall():
                headers[str(k)] = str(v)

            return HttpResponse(status, headers, body)
        except Exception as e:
            return None

    @classmethod
    def get_request_by_id(cls, packet_id: int) -> HttpResquest:
        cursor = cls.conn.cursor()
        cursor.execute("SELECT method, authority, path, query, body FROM requests WHERE packet_id=?;", [packet_id])
        (method, authority, path, query, body) = cursor.fetchone()
        
        headers = {}
        cursor.execute("SELECT key, value FROM request_headers WHERE packet_id=?", [packet_id])
        for (k, v) in cursor.fetchall():
            headers[str(k)] = str(v)

        return HttpResquest(packet_id, method, authority, path, query, headers, body)

    @classmethod
    def select(cls, filter_builder: HttpLogsFilterBuilder = None, limit=25):
        cursor = cls.conn.cursor()
        packets = []
        
        cursor.execute("SELECT COUNT(*) FROM requests;")
        row_count = cursor.fetchone()[0]

        for i in range(row_count):
            packets.append(cls.get_row_by_id(i))

        return packets
