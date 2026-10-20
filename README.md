# Rezervační systém zasedacích místností (Brixa)

Webový rezervační systém pro firmu Brixa (60 zaměstnanců, 6 zasedaček). Systém řeší problém blokovaných prázdných místností pomocí automatického uvolňování přes IoT čidla (přítomnost osob, koncentrace CO2).

## Jak spustit aplikaci (krok za krokem)

1. Nainstalujte závislosti:
   ```bash
   pip install flask
   ```
2. Spusťte aplikaci jedním příkazem *(plánováno)*:
   ```bash
   py app.py
   ```
3. Otevřete prohlížeč na adrese `http://127.0.0.1:5000`.

## Struktura projektu

Projekt striktně dodržuje třívrstvou architekturu:
- `web/` *(plánováno)*: Uživatelské rozhraní, šablony a webové routy (nevolá SQL přímo).
- `logika/` *(plánováno)*: Aplikační logika, validace rezervací a chytrá pravidla (uvolňování neobsazených místností).
- `uloziste/` *(plánováno)*: Databázová vrstva pracující s SQLite přes modul `sqlite3`.
- `docs/`: Analytický návrh systému (`NAVRH.md`).
- `GEMINI.md`: Pravidla vývoje a postupu prací.
- `README.md`: Základní dokumentace a příručka ke spuštění.

## Rozhodnutí klienta (20. 10. 2026)

- **Limit pro nepřítomnost:** Rezervace se uvolní po 15 minutách neaktivity čidla.
- **Detekce:** Plně automatická pomocí IoT čidel v místnostech; bez tabletů.
- **Notifikace:** Uvolnění rezervace se organizátorovi oznamuje e-mailem.
- **Role a práva:** 4 role (Zaměstnanec, Asistentka, Ředitel, Office manažerka). Asistentky mohou rušit cizí rezervace s povinným odůvodněním.
- **Výpadek čidla:** Při offline stavu čidla zůstávají rezervace platné.
- **Statistiky:** Měsíční report pro ředitele zachovává jmenný přehled osob blokujících místnosti.
- **Opakované rezervace:** Podpora týdenního opakování s možností manuálního řešení kolizí.
- **Kvalita vzduchu:** Vizuální varování na přehledu při CO2 > 1000 ppm.
- **MS Teams:** Integrace odložena na budoucí fázi projektu (po MVP).

## Otevřené otázky

Všechny původní nejasnosti z brífu byly vyřešeny 20. 10. 2026. Pro budoucí rozšíření zůstává k dopracování:
- Přesné napojení na firemní poskytovatele identity (SSO přes Microsoft 365 / Entra ID).
- Způsob nasazení MS Teams webhooků/botů po dokončení základní webové verze.

## Použité nástroje AI

- **Google Antigravity IDE**: Vývojové prostředí a orchestrace úloh.
- **Gemini 3.8 Flash (High)**: Analýza požadavků, vypracování návrhu architektury, definice ECA pravidel a strukturování dokumentace.
