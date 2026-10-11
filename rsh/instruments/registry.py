"""Look up instruments by key. This is the single place new instruments are added."""
from typing import Dict, List

from rsh.instruments.base import Instrument
from rsh.instruments.ukulele import UKULELE

_INSTRUMENTS: Dict[str, Instrument] = {}


def register(instrument: Instrument) -> None:
    _INSTRUMENTS[instrument.key] = instrument


def get_instrument(key: str) -> Instrument:
    try:
        return _INSTRUMENTS[key]
    except KeyError:
        raise KeyError(f"unknown instrument {key!r}; known: {sorted(_INSTRUMENTS)}") from None


def available_instruments() -> List[Instrument]:
    return list(_INSTRUMENTS.values())


register(UKULELE)
# TODO (Milestone 9): create instruments/guitar.py (E2 A2 D3 G3 B3 E4) and register it here.
