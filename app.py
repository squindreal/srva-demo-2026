"""Hlavní vstupní bod aplikace Brixa Rezervační systém."""
import os
from flask import Flask
from uloziste.databaze import Databaze
from web.routes import web_bp


def create_app(db_path: str = "rezervace.db") -> Flask:
    """Tovární funkce pro vytvoření a konfiguraci Flask aplikace."""
    app = Flask(__name__)
    
    # Tajný klíč pro flash zprávy
    app.secret_key = os.environ.get("SECRET_KEY", "brixa-zasedacky-tajny-klic-2026")

    # Inicializace databáze
    databaze = Databaze(db_path)
    app.config["DATABASE"] = databaze

    # Registrace webového rozhraní
    app.register_blueprint(web_bp)

    return app


if __name__ == "__main__":
    app = create_app()
    print("---------------------------------------------------------------")
    print("  Brixa Rezervační systém zasedaček běží na http://127.0.0.1:5000")
    print("  Ukončení: Stiskněte Ctrl+C")
    print("---------------------------------------------------------------")
    app.run(host="127.0.0.1", port=5000, debug=True)
