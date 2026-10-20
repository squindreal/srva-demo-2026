# Rezervační systém zasedacích místností (Brixa)

Webový rezervační systém pro firmu Brixa (60 zaměstnanců, 6 zasedaček). Systém řeší problém blokovaných prázdných místností pomocí automatického uvolňování přes IoT čidla (přítomnost osob, koncentrace CO2).

## Jak spustit aplikaci (krok za krokem)

1. Nainstalujte závislosti:
   ```bash
   py -m pip install flask
   ```
   *(nebo `pip install flask`, pokud máte pip v systémové cestě PATH)*
2. Spusťte aplikaci jedním příkazem:
   ```bash
   py app.py
   ```
3. Otevřete prohlížeč na adrese `http://127.0.0.1:5000`.

### Spuštění automatických testů

K otestování validačních pravidel (zejména striktního zákazu překryvu rezervací) a webového rozhraní spusťte:
```bash
py -m unittest discover tests
```

## Struktura projektu

Projekt striktně dodržuje třívrstvou architekturu:
- `web/`: Uživatelské rozhraní rozdělené do tří přehledných sekcí:
  1. **Seznam místností:** Přehledné karty zasedaček s patrem a kapacitou.
  2. **Přehled rezervací dne:** Strukturovaná tabulka s časovým blokem, zasedačkou, organizátorem, účelem a automatickým systémovým časem zápisu.
  3. **Formulář rezervace:** Přehledný formulář s automatickou kontrolou překryvu a jasnými chybovými hlášeními.
  - Nevolá SQL přímo, využívá aplikační logiku. Záhlaví a design systém jsou stylizovány v korporátní identitě ŠKODA (Deep Emerald, Electric Green) s textovým logem ŠKODA. Servírování stylů CSS zajištěno přes `web/static/css/style.css`.
- `logika/`: Aplikační logika, validace vstupů, automatické generování času vzniku rezervace a kontrola překryvu intervalů ($A_{od} < B_{do} \land A_{do} > B_{od}$).
- `uloziste/`: Databázová vrstva pracující s SQLite přes modul `sqlite3`, automatická tvorba schématu a vložení syntetických zasedacích místností.
- `tests/`: Sada automatických testů (detekce kolizí rezervací, překryv zleva/zprava/vnoření/obepnutí, povolené návaznosti, webové rozhraní a dostupnost CSS stylů).
- `app.py`: Jediný spouštěcí vstupní bod aplikace.
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
