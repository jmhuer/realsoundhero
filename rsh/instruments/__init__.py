"""Facts about instruments. Use ``get_instrument("ukulele")`` from registry.py."""
from rsh.instruments.base import Instrument
from rsh.instruments.registry import available_instruments, get_instrument, register

__all__ = ["Instrument", "available_instruments", "get_instrument", "register"]
