"""Integrační testy webové vrstvy pro kompletní svislý řez."""
import unittest
import tempfile
import os
from app import create_app


class TestWeboveRozhrani(unittest.TestCase):
    """Testy ověřující chování webového rozhraní a flash hlášení."""

    def setUp(self):
        self.temp_db_fd, self.temp_db_path = tempfile.mkstemp(suffix=".db")
        self.app = create_app(db_path=self.temp_db_path)
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

    def tearDown(self):
        os.close(self.temp_db_fd)
        if os.path.exists(self.temp_db_path):
            os.remove(self.temp_db_path)

    def test_zobrazeni_hlavni_stranky_a_mistnosti(self):
        """Ověří načtení stránky a přítomnost výchozích zasedaček a formuláře."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Brixa Meeting Rooms", html)
        self.assertIn("Tichá budka (1. patro)", html)
        self.assertIn("Hlavní zasedačka", html)
        self.assertIn("Uložit rezervaci", html)

    def test_uspesna_rezervace_pres_formular(self):
        """Ověří vytvoření rezervace přes formulář a přesměrování."""
        res = self.client.post(
            "/rezervace",
            data={
                "zasedacka_id": "1",
                "kdo": "Klára Benešová",
                "datum": "2026-10-25",
                "cas_od": "09:00",
                "cas_do": "10:30",
                "ucel": "Porada vedení",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("byla úspěšně uložena", html)
        self.assertIn("Klára Benešová", html)
        self.assertIn("Porada vedení", html)
        self.assertIn("09:00 – 10:30", html)
        self.assertIn("Vytvořeno:", html)

    def test_odmitnuti_prekryvajici_se_rezervace_ve_webu(self):
        """Ověří, že překrývající se rezervace je odmítnuta a zobrazí se jasná hláška."""
        # 1. První rezervace
        self.client.post(
            "/rezervace",
            data={
                "zasedacka_id": "1",
                "kdo": "Klára Benešová",
                "datum": "2026-10-25",
                "cas_od": "14:00",
                "cas_do": "15:00",
                "ucel": "Strategický workshop",
            },
            follow_redirects=True,
        )

        # 2. Druhá kolidující rezervace v téže místnosti
        res = self.client.post(
            "/rezervace",
            data={
                "zasedacka_id": "1",
                "kdo": "Jan Novák",
                "datum": "2026-10-25",
                "cas_od": "14:30",
                "cas_do": "16:00",
                "ucel": "Synchronizace vývoje",
            },
            follow_redirects=True,
        )
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Chyba rezervace:", html)
        self.assertIn("Rezervaci nelze vytvořit z důvodu kolize", html)
        self.assertIn("Klára Benešová", html)
        self.assertIn("Strategický workshop", html)

    def test_staticky_soubor_css_je_dostupny(self):
        """Ověří, že CSS styly jsou správně servírovány pod /static/css/style.css."""
        res = self.client.get("/static/css/style.css")
        self.assertEqual(res.status_code, 200)
        self.assertIn("BRIXA", res.data.decode("utf-8"))
        self.assertIn(".rooms-grid", res.data.decode("utf-8"))


if __name__ == "__main__":
    unittest.main()
