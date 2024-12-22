# n3xx.py
from .base import PeriphManagerBase


class PeriphManagerN3xx(PeriphManagerBase):
    def initialize(self):
        print("Initializing N3xx peripheral manager with args:", self.args)

# Define the entry point


def periph_manager(args):
    return PeriphManagerN3xx(args)
