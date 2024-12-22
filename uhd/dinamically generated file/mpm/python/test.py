# Test the dynamic behavior
from usrp_mpm.rpc_server import RpcServer

default_args = {"some_key": "some_value"}
server = RpcServer(default_args)
mgr = server._mgr_generator()
mgr.initialize()
