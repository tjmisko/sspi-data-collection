import urllib3
import requests
import ssl
from os import environ
from database_connector import SSPIDatabaseConnector

class CustomHttpAdapter (requests.adapters.HTTPAdapter):
# "Transport adapter" that allows us to use custom ssl_context.

    def __init__(self, ssl_context=None, **kwargs):
        self.ssl_context = ssl_context
        super().__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = urllib3.poolmanager.PoolManager(
            num_pools=connections, maxsize=maxsize,
            block=block, ssl_context=self.ssl_context)

def get_legacy_session():
    ctx = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
    session = requests.session()
    session.mount('https://', CustomHttpAdapter(ctx))
    return session

# remote_session = get_legacy_session()
# remote_session.post("http://127.0.0.1:5000/remote/session/login", data=dict(username=environ.get("USERNAME"), password=environ.get("PASSWORD")))

database = SSPIDatabaseConnector()