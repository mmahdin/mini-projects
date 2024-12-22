# rpc_server.py
from usrp_mpm.periph_manager import periph_manager


class RpcServer:
    def __init__(self, default_args):
        # Create the periph_manager based on the configured device
        self._mgr_generator = lambda: periph_manager(default_args)
