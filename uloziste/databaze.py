"""Správa SQLite databáze pro evidenci zasedaček a rezervací."""
import sqlite3
from typing import List, Dict, Any, Optional

DEFAULT_DB_PATH = "rezervace.db"

# Syntetická data pro výchozí zasedací místnosti dle návrhu (6 místností)
SYNTHETIC_ROOMS = [
    {"nazev": "Tichá budka (1. patro)", "patro": 1, "kapacita": 2},
    {"nazev": "Malá zasedačka A", "patro": 1, "kapacita": 4},
    {"nazev": "Malá zasedačka B", "patro": 2, "kapacita": 6},
    {"nazev": "Kreativní dílna", "patro": 2, "kapacita": 10},
    {"nazev": "Projektová místnost", "patro": 3, "kapacita": 12},
    {"nazev": "Hlavní zasedačka", "patro": 3, "kapacita": 20},
]


class Databaze:
    """Třída pro přímou práci s SQLite databází."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON;")
        return conn

    def _init_db(self) -> None:
        """Inicializuje tabulky v databázi a vloží syntetická data, pokud je prázdná."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS zasedacka (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nazev TEXT NOT NULL,
                    patro INTEGER NOT NULL,
                    kapacita INTEGER NOT NULL
                );
                """
            )
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS rezervace (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    zasedacka_id INTEGER NOT NULL,
                    kdo TEXT NOT NULL,
                    od TEXT NOT NULL,
                    do TEXT NOT NULL,
                    ucel TEXT NOT NULL,
                    cas_vytvoreni TEXT NOT NULL,
                    FOREIGN KEY (zasedacka_id) REFERENCES zasedacka(id) ON DELETE CASCADE
                );
                """
            )

            # Vložení výchozích syntetických zasedaček, pokud tabulka ještě žádné neobsahuje
            cursor.execute("SELECT COUNT(*) FROM zasedacka;")
            pocet = cursor.fetchone()[0]
            if pocet == 0:
                for mistnost in SYNTHETIC_ROOMS:
                    cursor.execute(
                        """
                        INSERT INTO zasedacka (nazev, patro, kapacita)
                        VALUES (?, ?, ?);
                        """,
                        (mistnost["nazev"], mistnost["patro"], mistnost["kapacita"]),
                    )
            conn.commit()

    def ziskej_vsechny_zasedacky(self) -> List[Dict[str, Any]]:
        """Vrátí seznam všech zasedacích místností seřazených podle patra a názvu."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nazev, patro, kapacita FROM zasedacka ORDER BY patro ASC, nazev ASC;"
            )
            return [dict(row) for row in cursor.fetchall()]

    def ziskej_zasedacku_dle_id(self, zasedacka_id: int) -> Optional[Dict[str, Any]]:
        """Vrátí detail konkrétní zasedací místnosti nebo None."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, nazev, patro, kapacita FROM zasedacka WHERE id = ?;",
                (zasedacka_id,),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def vloz_zasedacku(self, nazev: str, patro: int, kapacita: int) -> int:
        """Vloží novou zasedací místnost a vrátí její ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO zasedacka (nazev, patro, kapacita)
                VALUES (?, ?, ?);
                """,
                (nazev, patro, kapacita),
            )
            conn.commit()
            return cursor.lastrowid

    def ziskej_rezervace_pro_zasedacku(self, zasedacka_id: int) -> List[Dict[str, Any]]:
        """Vrátí všechny rezervace pro konkrétní zasedací místnost."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT id, zasedacka_id, kdo, od, do, ucel, cas_vytvoreni
                FROM rezervace
                WHERE zasedacka_id = ?
                ORDER BY od ASC;
                """,
                (zasedacka_id,),
            )
            return [dict(row) for row in cursor.fetchall()]

    def ziskej_rezervace_pro_den(self, datum_str: str) -> List[Dict[str, Any]]:
        """
        Vrátí všechny rezervace, které zasahují do daného dne (datum_str ve formátu YYYY-MM-DD),
        včetně názvu zasedačky, seřazené podle času začátku.
        """
        den_zacatek = f"{datum_str}T00:00"
        den_konec = f"{datum_str}T23:59:59"

        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT 
                    r.id,
                    r.zasedacka_id,
                    z.nazev AS mistnost_nazev,
                    z.patro AS mistnost_patro,
                    z.kapacita AS mistnost_kapacita,
                    r.kdo,
                    r.od,
                    r.do,
                    r.ucel,
                    r.cas_vytvoreni
                FROM rezervace r
                JOIN zasedacka z ON r.zasedacka_id = z.id
                WHERE r.od <= ? AND r.do >= ?
                ORDER BY r.od ASC, z.nazev ASC;
                """,
                (den_konec, den_zacatek),
            )
            return [dict(row) for row in cursor.fetchall()]

    def vloz_rezervaci(
        self,
        zasedacka_id: int,
        kdo: str,
        od: str,
        do: str,
        ucel: str,
        cas_vytvoreni: str,
    ) -> int:
        """Vloží novou rezervaci a vrátí její ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                INSERT INTO rezervace (zasedacka_id, kdo, od, do, ucel, cas_vytvoreni)
                VALUES (?, ?, ?, ?, ?, ?);
                """,
                (zasedacka_id, kdo, od, do, ucel, cas_vytvoreni),
            )
            conn.commit()
            return cursor.lastrowid
