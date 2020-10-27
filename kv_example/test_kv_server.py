from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

kv = {}

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

# Create server
with SimpleXMLRPCServer(('localhost', 8000),
                        requestHandler=RequestHandler) as server:

    def put(key, value):
        kv[key] = value
        return 0
    server.register_function(put, 'put')

    def get(key):
        if key in kv:
           return kv[key]
        else:
          return -1
    server.register_function(get, 'get')

    # Run the server's main loop
    server.serve_forever()

