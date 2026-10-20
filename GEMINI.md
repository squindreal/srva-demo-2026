# Pravidla vývoje projektu

1. **Technologie:** Python 3, Flask, SQLite přes `sqlite3`. Další knihovny pouze po schválení.
2. **Architektura:** Tři vrstvy ve složkách `web/`, `logika/`, `uloziste/`; `web/` nevolá SQL přímo.
3. **Spouštění:** Aplikace se spouští jedním příkazem uvedeným v `README.md`.
4. **Data a bezpečnost:** Pouze syntetická data. Databázové soubory a `.env` patří do `.gitignore`.
5. **Pracovní postup:** Před každou změnou souborů napiš plán a počkej na schválení.
6. **Dokumentace:** Po každé změně souborů aktualizuj `README.md`.
7. **Git:** Commit vždy s `-m`, žádné interaktivní příkazy, push výhradně na pokyn.
