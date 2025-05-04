from mitmproxy import options
from mitmproxy.tools import dump

#  Local sdk path for now
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../yatangaki-sdk-py')))
from db.http_db import *

class RequestLogger:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def response(self, flow):
        try:
            req = flow.request
            res = flow.response

            request_headers = []
            for (k, v) in req.headers.items():
                request_headers.append(HttpRequestHeader(
                        key=k,
                        value=v
                    ))
            
            response_headers = []
            for (k, v) in res.headers.items():
                response_headers.append(HttpResponseHeader(
                        key=k,
                        value=v
                    ))   
            request_query = []
            for (k, v) in req.query.items():
                request_query.append(HttpRequestQuery(
                        key=k,
                        value=v
                    ))

            request = HttpRequest(
                    timestamp = req.timestamp_end,
                    path = req.path,
                    method = req.method,
                    authority = req.authority,
                    scheme = req.scheme,
                    headers = request_headers,
                    query = request_query,
                    body = req.content
                )

            response = HttpResponse(
                    timestamp = res.timestamp_end,
                    status = res.status_code,
                    headers = response_headers,
                    body = res.content
                )

            self.db_session.add_all([request, response])
            self.db_session.commit()
        except Exception as e:
            print(e)

async def start_proxy(port, db_session):
    opts = options.Options(listen_host="127.0.0.1", listen_port=port)

    master = dump.DumpMaster(
        opts,
        with_termlog=False,
        with_dumper=False,
    )
    master.addons.add(RequestLogger(db_session))
    
    await master.run()
    return master
