import asyncio
from mitmproxy import options
from mitmproxy.tools import dump

#  Local sdk path for now
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../yatangaki-sdk-py')))
from db.http_db import *

#  It sucks by python does not have proper mpsc channels...
project_name = None
master = None

class RequestLogger:
    def response(self, flow):
        global project_name

        if not project_name:
            print("MITM hook, no database selected")
            return
        
        db_session = httpdb(project_name)

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

            response = HttpResponse(
                    timestamp = res.timestamp_end,
                    status = res.status_code,
                    headers = response_headers,
                    body = res.content
                )

            request = HttpRequest(
                    timestamp = req.timestamp_end,
                    path = req.path,
                    method = req.method,
                    authority = req.authority,
                    scheme = req.scheme,
                    headers = request_headers,
                    query = request_query,
                    body = req.content,
                    response = response
                )

            self.db_session.add_all([request])
            self.db_session.commit()
        except Exception as e:
            print(e)

#  FIXME: proxy restarts twice
async def start_proxy():
    global master
    if master:
        print("proxy already listening")
        return

    print("starting proxy service")
    opts = options.Options(
            listen_host="127.0.0.1",
            listen_port=9000,
            mode=["upstream:http://localhost:3128/"]
        )

    master = dump.DumpMaster(
            opts,
            with_dumper=False,
        )
    master.addons.add(RequestLogger())
    
    await master.run()
    print("exiting")

def proxy_entrypoint():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_proxy())
    loop.close()
