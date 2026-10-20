"""Webové routy aplikace. Nevolá SQL přímo, využívá aplikační logiku."""
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from logika.sluzby_rezervaci import (
    ziskej_seznam_zasedacek,
    ziskej_prehled_dne,
    vytvor_rezervaci,
    RezervaceChyba,
)

web_bp = Blueprint("web", __name__, template_folder="templates", static_folder="static")


def _get_db():
    return current_app.config["DATABASE"]


@web_bp.route("/", methods=["GET"])
def index():
    """Hlavní dashboard se seznamem místností, formulářem a přehledem dne."""
    db = _get_db()
    dnes = datetime.now().strftime("%Y-%m-%d")
    vybrane_datum = request.args.get("datum", dnes).strip()
    if not vybrane_datum:
        vybrane_datum = dnes

    zasedacky = ziskej_seznam_zasedacek(db)
    rezervace_dne = ziskej_prehled_dne(db, vybrane_datum)

    return render_template(
        "index.html",
        zasedacky=zasedacky,
        rezervace=rezervace_dne,
        vybrane_datum=vybrane_datum,
        dnes=dnes,
    )


@web_bp.route("/rezervace", methods=["POST"])
def nova_rezervace():
    """Zpracování formuláře pro vytvoření nové rezervace."""
    db = _get_db()

    zasedacka_id = request.form.get("zasedacka_id")
    kdo = request.form.get("kdo", "").strip()
    datum = request.form.get("datum", "").strip()
    cas_od = request.form.get("cas_od", "").strip()
    cas_do = request.form.get("cas_do", "").strip()
    ucel = request.form.get("ucel", "").strip()

    # Složení plného času
    od_plny = f"{datum}T{cas_od}" if datum and cas_od else ""
    do_plny = f"{datum}T{cas_do}" if datum and cas_do else ""

    try:
        nova = vytvor_rezervaci(
            db=db,
            zasedacka_id=zasedacka_id,
            kdo=kdo,
            od=od_plny,
            do=do_plny,
            ucel=ucel,
        )
        flash(
            f"Rezervace pro místnost '{nova['mistnost_nazev']}' byla úspěšně uložena.",
            "success",
        )
    except RezervaceChyba as err:
        flash(str(err), "danger")
    except Exception as err:
        flash(f"Nastala neočekávaná chyba: {err}", "danger")

    # Přesměrujeme zpět na den rezervace, pokud byl zadán
    cil_datum = datum if datum else datetime.now().strftime("%Y-%m-%d")
    return redirect(url_for("web.index", datum=cil_datum))
