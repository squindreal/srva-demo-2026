"""Testy validačního pravidla o překryvu rezervací."""
import unittest
import tempfile
import os
from uloziste.databaze import Databaze
from logika.sluzby_rezervaci import (
    vytvor_rezervaci,
    detekuj_prekryv,
    PrekryvRezervaceError,
    NeplatnyIntervalError,
    ChybejiciUdajeError,
)


class TestPrekryvRezervaci(unittest.TestCase):
    """Testy ověřující správnou detekci kolizí rezervací v téže místnosti."""

    def setUp(self):
        # Dočasná databáze pro každý test
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.db = Databaze(self.temp_db_path)
        zasedacky = self.db.ziskej_vsechny_zasedacky()
        self.mistnost_1 = zasedacky[0]["id"]
        self.mistnost_2 = zasedacky[1]["id"]

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_vytvoreni_platne_rezervace_a_automaticky_cas(self):
        """Ověří vytvoření platné rezervace a automatické doplnění času vytvoření."""
        rez = vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Klára Benešová",
            od="2026-10-25T10:00",
            do="2026-10-25T11:00",
            ucel="Pravidelný status",
        )
        self.assertIsNotNone(rez["id"])
        self.assertTrue(len(rez["cas_vytvoreni"]) > 0)
        self.assertEqual(rez["kdo"], "Klára Benešová")

    def test_odmitnuti_identickeho_casu_a_jasna_hlaska(self):
        """Rezervace ve zcela shodném čase musí být odmítnuta s jasnou hláškou."""
        vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Petr Svoboda",
            od="2026-10-25T10:00",
            do="2026-10-25T11:00",
            ucel="Schůzka s klientem",
        )

        with self.assertRaises(PrekryvRezervaceError) as ctx:
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="Jana Nováková",
                od="2026-10-25T10:00",
                do="2026-10-25T11:00",
                ucel="Pohovor",
            )

        hlaska = str(ctx.exception)
        self.assertIn("Petr Svoboda", hlaska)
        self.assertIn("Schůzka s klientem", hlaska)
        self.assertIn("2026-10-25 10:00", hlaska)
        self.assertIn("2026-10-25 11:00", hlaska)

    def test_prekryv_zleva(self):
        """Nová rezervace začíná před a končí uvnitř existující rezervace."""
        vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Petr",
            od="2026-10-25T10:00",
            do="2026-10-25T11:00",
            ucel="Existující",
        )

        with self.assertRaises(PrekryvRezervaceError):
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="Jana",
                od="2026-10-25T09:30",
                do="2026-10-25T10:30",
                ucel="Kolize zleva",
            )

    def test_prekryv_zprava(self):
        """Nová rezervace začíná uvnitř existující rezervace a končí po ní."""
        vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Petr",
            od="2026-10-25T10:00",
            do="2026-10-25T11:00",
            ucel="Existující",
        )

        with self.assertRaises(PrekryvRezervaceError):
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="Jana",
                od="2026-10-25T10:30",
                do="2026-10-25T11:30",
                ucel="Kolize zprava",
            )

    def test_vnitrni_prekryv(self):
        """Nová rezervace je celá uvnitř existující rezervace."""
        vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Petr",
            od="2026-10-25T10:00",
            do="2026-10-25T12:00",
            ucel="Existující dlouhá",
        )

        with self.assertRaises(PrekryvRezervaceError):
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="Jana",
                od="2026-10-25T10:30",
                do="2026-10-25T11:30",
                ucel="Kolize vnořená",
            )

    def test_vnejsi_prekryv_obepnuti(self):
        """Nová rezervace zcela obepíná existující rezervaci."""
        vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Petr",
            od="2026-10-25T10:30",
            do="2026-10-25T11:00",
            ucel="Existující krátká",
        )

        with self.assertRaises(PrekryvRezervaceError):
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="Jana",
                od="2026-10-25T10:00",
                do="2026-10-25T11:30",
                ucel="Kolize obepínající",
            )

    def test_navazujici_rezervace_jsou_povoleny(self):
        """
        Rezervace, které se dotýkají (jedna končí přesně v čase, kdy druhá začíná),
        se nepřekrývají a obě musí projít.
        """
        rez1 = vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Petr",
            od="2026-10-25T10:00",
            do="2026-10-25T11:00",
            ucel="Dopolední schůzka",
        )
        # Těsně před
        rez_pred = vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Jana",
            od="2026-10-25T09:00",
            do="2026-10-25T10:00",
            ucel="Předchozí schůzka",
        )
        # Těsně po
        rez_po = vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Karel",
            od="2026-10-25T11:00",
            do="2026-10-25T12:00",
            ucel="Následující schůzka",
        )
        self.assertIsNotNone(rez1["id"])
        self.assertIsNotNone(rez_pred["id"])
        self.assertIsNotNone(rez_po["id"])

    def test_stejny_cas_v_ruzne_mistnosti_je_povolen(self):
        """Rezervace ve stejném čase, ale v jiné místnosti, je platná."""
        vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_1,
            kdo="Petr",
            od="2026-10-25T10:00",
            do="2026-10-25T11:00",
            ucel="Tým A",
        )
        rez_druha = vytvor_rezervaci(
            db=self.db,
            zasedacka_id=self.mistnost_2,
            kdo="Jana",
            od="2026-10-25T10:00",
            do="2026-10-25T11:00",
            ucel="Tým B",
        )
        self.assertIsNotNone(rez_druha["id"])

    def test_neplatny_interval_od_vetsi_nebo_rovno_do(self):
        """Čas od nesmí být větší ani roven času do."""
        with self.assertRaises(NeplatnyIntervalError):
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="Petr",
                od="2026-10-25T11:00",
                do="2026-10-25T10:00",
                ucel="Obrácený čas",
            )

        with self.assertRaises(NeplatnyIntervalError):
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="Petr",
                od="2026-10-25T10:00",
                do="2026-10-25T10:00",
                ucel="Nulová délka",
            )

    def test_chybejici_udaje(self):
        """Nevyplněná povinná pole vyvolají ChybejiciUdajeError."""
        with self.assertRaises(ChybejiciUdajeError):
            vytvor_rezervaci(
                db=self.db,
                zasedacka_id=self.mistnost_1,
                kdo="",
                od="2026-10-25T10:00",
                do="2026-10-25T11:00",
                ucel="Neznámý",
            )


if __name__ == "__main__":
    unittest.main()
