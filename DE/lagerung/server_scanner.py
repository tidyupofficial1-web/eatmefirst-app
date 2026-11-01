import http.server
import socketserver
import json
import urllib.request
import urllib.parse
import os
import socket
import threading
import ssl
from datetime import datetime, timedelta

PORT = 8888
UDP_DISCOVERY_PORT = 8889
DB_FILE = "produkte_db.json"
DISPENSA_FILE = "dispensa.json"

# Imposta la directory di lavoro sulla radice del progetto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
os.chdir(BASE_DIR)

# Memoria temporanea per l'ultima scansione con tutti i campi tecnici estesi
ULTIMA_SCANSIONE = {
    "barcode": "",
    "nome": "",
    "categoria": "",
    "foto": "",
    "quantita_netta": "",
    "ingredienti": "",
    "allergeni": "",
    "calorie": "",
    "found": False
}

def carica_db_locale():
    db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
    if os.path.exists(db_path):
        try:
            with open(db_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def salva_su_db_locale(barcode, scheda):
    db = carica_db_locale()
    db[barcode] = scheda
    db_path = os.path.join(os.path.dirname(__file__), DB_FILE)
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=4)

def load_pantry():
    dispensa_path = os.path.join(os.path.dirname(__file__), DISPENSA_FILE)
    if os.path.exists(dispensa_path):
        try:
            with open(dispensa_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []
    return []

def calculate_expiration_date(item):
    """Berechnet das tatsächliche Verfallsdatum basierend auf dem Typ und den gespeicherten Werten."""
    tipo = item.get('tipo_scadenza')
    valore = item.get('valore_scadenza')
    data_carico_str = item.get('data_carico')

    if tipo == 'nessuna' or not valore:
        return None

    if tipo == 'esatta':
        try:
            return datetime.strptime(valore, '%Y-%m-%d').date()
        except ValueError:
            return None

    try:
        data_rif = datetime.strptime(data_carico_str.split('T')[0], '%Y-%m-%d').date()
    except Exception:
        data_rif = datetime.today().date()

    if tipo == 'giorni':
        return data_rif + timedelta(days=int(valore))
    elif tipo == 'mesi':
        return data_rif + timedelta(days=int(valore) * 30)

    return None

def compone_scheda_prodotto(barcode, lingua="de"):
    db = carica_db_locale()
    if barcode in db:
        scheda = db[barcode]
        scheda["found"] = True
        return scheda

    scheda = {
        "found": False,
        "barcode": barcode,
        "nome": "",
        "categoria": "",
        "foto": "",
        "quantita_netta": "",
        "ingredienti": "",
        "allergeni": "",
        "calorie": "",
        "extra": {}
    }

    # Fallback-Kette von Websites / APIs, die nacheinander abgefragt werden
    fonti_api = [
        f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
        f"https://de.openfoodfacts.org/api/v0/product/{barcode}.json",
        f"https://it.openfoodfacts.org/api/v0/product/{barcode}.json",
        f"https://fr.openfoodfacts.org/api/v0/product/{barcode}.json",
        f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    ]

    for url_off in fonti_api:
        try:
            req = urllib.request.Request(url_off, headers={'User-Agent': 'EatMeFirst - LocalApp'})
            with urllib.request.urlopen(req, timeout=3) as response:
                data = json.loads(response.read().decode())
                p = data.get("product", {}) if "product" in data else data
                
                if data.get("status") == 1 or p:
                    scheda["found"] = True
                    
                    scheda["nome"] = (
                        p.get(f"product_name_{lingua}") or 
                        p.get("product_name") or 
                        p.get("product_name_de") or 
                        p.get("product_name_en") or 
                        p.get("title") or ""
                    )
                    
                    cat_raw = p.get("categories") or p.get("categories_tags", [""])[0]
                    if isinstance(cat_raw, str) and cat_raw:
                        scheda["categoria"] = cat_raw.split(",")[0].replace("en:", "").replace("de:", "").strip().capitalize()
                    
                    scheda["foto"] = p.get("image_front_url") or p.get("image_url") or p.get("image_front_small_url") or ""
                    scheda["quantita_netta"] = p.get("quantity") or p.get("product_quantity") or ""
                    scheda["ingredienti"] = p.get(f"ingredients_text_{lingua}") or p.get("ingredients_text") or p.get("ingredients_text_de") or ""
                    scheda["allergeni"] = p.get("allergens_from_ingredients") or p.get("allergens", "")
                    scheda["calorie"] = p.get("nutriments", {}).get("energy-kcal_100g", "") or p.get("nutriments", {}).get("energy-kcal", "")
                    
                    break
        except Exception as e:
            print(f"⚠️ Fehlgeschlagener Versuch mit {url_off}: {e}")

    if scheda["found"]:
        salva_su_db_locale(barcode, scheda)

    return scheda

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        if args and any("/last_scan" in str(arg) for arg in args):
            return
        super().log_message(format, *args)

    def do_GET(self):
        parsed_url = urllib.parse.urlparse(self.path)
        query_components = urllib.parse.parse_qs(parsed_url.query)

        # Neue API für die 10-Tage-Benachrichtigungen (Hauptmenü)
        if parsed_url.path == "/api/menu_alerts":
            pantry = load_pantry()
            today = datetime.today().date()
            soglia_10_giorni = today + timedelta(days=10)
            prodotti_in_scadenza = []

            for item in pantry:
                scad_date = calculate_expiration_date(item)
                if scad_date and scad_date <= soglia_10_giorni:
                    giorni_rimasti = (scad_date - today).days
                    is_tassativo = item.get('tassativo', False)
                    
                    # Farbliche Regeln für Benachrichtigungen und Listen
                    if is_tassativo:
                        badge_style = 'tassativo'      # Rot / Weißer Text
                    else:
                        badge_style = 'consigliata'    # Gelb / Schwarzer Text

                    prodotti_in_scadenza.append({
                        'id': item.get('barcode') or item.get('nome'),
                        'nome': item.get('nome'),
                        'scadenza': scad_date.strftime('%d.%m.%Y'),
                        'giorni_rimasti': giorni_rimasti,
                        'ubicazione': item.get('ubicazione', 'Nicht angegeben'),
                        'tassativo': is_tassativo,
                        'badge_style': badge_style
                    })

            # Nach aufsteigender Dringlichkeit sortieren
            prodotti_in_scadenza.sort(key=lambda x: x['giorni_rimasti'])

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                'has_alerts': len(prodotti_in_scadenza) > 0,
                'count': len(prodotti_in_scadenza),
                'items': prodotti_in_scadenza
            }, ensure_ascii=False).encode("utf-8"))
            return

        # Neue API für die vorbeugende Einkaufsliste mit Farbcodierung
        if parsed_url.path == "/api/shopping_list_preventive":
            pantry = load_pantry()
            today = datetime.today().date()
            soglia_10_giorni = today + timedelta(days=10)
            lista_spesa = []

            for item in pantry:
                quantita = item.get('quantita', 0)
                scad_date = calculate_expiration_date(item)
                is_tassativo = item.get('tassativo', False)
                tipo_scadenza = item.get('tipo_scadenza')

                # Regel: Vorratserschöpfung (Restmenge 1 Stück) -> Blauer Hintergrund, Weißer Text
                if quantita == 1:
                    lista_spesa.append({
                        'nome': item.get('nome'),
                        'motivo': 'Fast aufgebraucht (nur noch 1 Stück übrig)',
                        'categoria_colore': 'esaurimento', # Blau / Weiß
                        'stato_testo': '🔵 Vorratsempfehlung'
                    })
                    continue

                # Regel: Anstehende Verfallsdaten (innerhalb von 10 Tagen)
                if scad_date and scad_date <= soglia_10_giorni:
                    if is_tassativo:
                        colore = 'tassativo'    # Rot / Weiß
                        testo = '🔴 Zwingendes Verfallsdatum bevorstehend'
                    else: