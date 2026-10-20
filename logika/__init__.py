"""Aplikační logika pro správu zasedaček a rezervací."""
from .sluzby_rezervaci import (
    RezervaceChyba,
    PrekryvRezervaceError,
    NeplatnyIntervalError,
    ChybejiciUdajeError,
    detekuj_prekryv,
    vytvor_rezervaci,
    ziskej_seznam_zasedacek,
    ziskej_prehled_dne,
)

__all__ = [
    "RezervaceChyba",
    "PrekryvRezervaceError",
    "NeplatnyIntervalError",
    "ChybejiciUdajeError",
    "detekuj_prekryv",
    "vytvor_rezervaci",
    "ziskej_seznam_zasedacek",
    "ziskej_prehled_dne",
]
