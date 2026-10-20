"""Služby pro validaci a správu rezervací včetně detekce kolizí."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from uloziste.databaze import Databaze


class RezervaceChyba(Exception):
    """Obecná výjimka rezervačního systému."""
    pass


class PrekryvRezervaceError(RezervaceChyba):
    """Výjimka vyvolaná při pokusu o rezervaci překrývající se s jinou ve stejné místnosti."""
    pass


class NeplatnyIntervalError(RezervaceChyba):
    """Výjimka vyvolaná při neplatném časovém intervalu (např. od >= do)."""
    pass


class ChybejiciUdajeError(RezervaceChyba):
    """Výjimka vyvolaná při chybějících nebo neplatných vstupních datech."""
    pass


def normalizuj_cas(cas_str: str) -> datetime:
    """
    Převede textový čas na datetime objekt.
    Podporuje běžné formáty YYYY-MM-DDTHH:MM i YYYY-MM-DD HH:MM.
    """
    if not cas_str or not isinstance(cas_str, str):
        raise ChybejiciUdajeError("Čas musí být neprázdný řetězec.")
    
    cisteny = cas_str.strip().replace(" ", "T")
    try:
        # Zkusíme s minutovou přesností
        if len(cisteny) == 16:
            return datetime.strptime(cisteny, "%Y-%m-%dT%H:%M")
        # Nebo se sekundami
        elif len(cisteny) == 19:
            return datetime.strptime(cisteny, "%Y-%m-%dT%H:%M:%S")
        else:
            return datetime.fromisoformat(cisteny)
    except ValueError as e:
        raise ChybejiciUdajeError(f"Neplatný formát data a času: '{cas_str}'. Očekává se formát YYYY-MM-DD HH:MM.") from e


def detekuj_prekryv(
    existujici_rezervace: List[Dict[str, Any]],
    novy_od: str,
    novy_do: str,
) -> Optional[Dict[str, Any]]:
    """
    Ověří, zda se požadovaný časový interval [novy_od, novy_do) překrývá
    s některou z existujících rezervací.
    
    Matematické pravidlo překryvu dvou polootevřených intervalů [A_od, A_do) a [B_od, B_do):
    A_od < B_do a zároveň A_do > B_od.
    
    Pokud ke kolizi dojde, vrátí kolidující rezervaci. Jinak vrátí None.
    """
    novy_od_dt = normalizuj_cas(novy_od)
    novy_do_dt = normalizuj_cas(novy_do)

    for rez in existujici_rezervace:
        stara_od_dt = normalizuj_cas(rez["od"])
        stara_do_dt = normalizuj_cas(rez["do"])

        # Kontrola překryvu
        if novy_od_dt < stara_do_dt and novy_do_dt > stara_od_dt:
            return rez

    return None


def ziskej_seznam_zasedacek(db: Databaze) -> List[Dict[str, Any]]:
    """Vrátí seznam všech zasedacích místností."""
    return db.ziskej_vsechny_zasedacky()


def ziskej_prehled_dne(db: Databaze, datum_str: str) -> List[Dict[str, Any]]:
    """Vrátí rezervace pro vybraný den (datum ve formátu YYYY-MM-DD)."""
    if not datum_str:
        datum_str = datetime.now().strftime("%Y-%m-%d")
    return db.ziskej_rezervace_pro_den(datum_str)


def vytvor_rezervaci(
    db: Databaze,
    zasedacka_id: Any,
    kdo: str,
    od: str,
    do: str,
    ucel: str,
) -> Dict[str, Any]:
    """
    Vytvoří novou rezervaci po ověření validity údajů a kontrole překryvu.
    Čas vytvoření se generuje automaticky na úrovni systému.
    """
    # 1. Základní kontrola vstupních údajů
    if not zasedacka_id:
        raise ChybejiciUdajeError("Musíte vybrat zasedací místnost.")
    try:
        zasedacka_id_int = int(zasedacka_id)
    except (ValueError, TypeError):
        raise ChybejiciUdajeError("Identifikátor zasedací místnosti musí být číslo.")

    kdo_clean = (kdo or "").strip()
    if not kdo_clean:
        raise ChybejiciUdajeError("Pole 'Kdo rezervuje' je povinné.")

    ucel_clean = (ucel or "").strip()
    if not ucel_clean:
        raise ChybejiciUdajeError("Pole 'Účel rezervace' je povinné.")

    # 2. Kontrola existence místnosti
    mistnost = db.ziskej_zasedacku_dle_id(zasedacka_id_int)
    if not mistnost:
        raise ChybejiciUdajeError("Vybraná zasedací místnost v systému neexistuje.")

    # 3. Kontrola formátu a pořadí časů
    od_dt = normalizuj_cas(od)
    do_dt = normalizuj_cas(do)

    if od_dt >= do_dt:
        raise NeplatnyIntervalError("Čas začátku rezervace (Od) musí předcházet času jejího konce (Do).")

    od_iso = od_dt.strftime("%Y-%m-%dT%H:%M")
    do_iso = do_dt.strftime("%Y-%m-%dT%H:%M")

    # 4. Kontrola překryvu s existujícími rezervacemi v téže místnosti
    existujici = db.ziskej_rezervace_pro_zasedacku(zasedacka_id_int)
    kolize = detekuj_prekryv(existujici, od_iso, do_iso)

    if kolize:
        kolize_od = kolize["od"].replace("T", " ")
        kolize_do = kolize["do"].replace("T", " ")
        raise PrekryvRezervaceError(
            f"Rezervaci nelze vytvořit z důvodu kolize: místnost '{mistnost['nazev']}' "
            f"je v čase {kolize_od} – {kolize_do} již rezervována "
            f"(organizátor: {kolize['kdo']}, účel: '{kolize['ucel']}')."
        )

    # 5. Automatické zaznamenání systémového času vytvoření
    cas_vytvoreni = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    nova_id = db.vloz_rezervaci(
        zasedacka_id=zasedacka_id_int,
        kdo=kdo_clean,
        od=od_iso,
        do=do_iso,
        ucel=ucel_clean,
        cas_vytvoreni=cas_vytvoreni,
    )

    return {
        "id": nova_id,
        "zasedacka_id": zasedacka_id_int,
        "mistnost_nazev": mistnost["nazev"],
        "kdo": kdo_clean,
        "od": od_iso,
        "do": do_iso,
        "ucel": ucel_clean,
        "cas_vytvoreni": cas_vytvoreni,
    }
