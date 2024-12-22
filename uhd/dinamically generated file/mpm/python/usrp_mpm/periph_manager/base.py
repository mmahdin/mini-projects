# base.py
class PeriphManagerBase:
    def __init__(self, args):
        self.args = args

    def initialize(self):
        raise NotImplementedError(
            "This method should be implemented by subclasses.")
