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
DB_FILE = "db_prodotti.json"
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
    """Calcola la data di scadenza effettiva in base al tipo e ai valori salvati."""
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

def compone_scheda_prodotto(barcode, lingua="it"):
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

    # Catena di siti / API da interrogare in sequenza (Fallback Chain)
    fonti_api = [
        f"https://world.openfoodfacts.org/api/v0/product/{barcode}.json",
        f"https://it.openfoodfacts.org/api/v0/product/{barcode}.json",
        f"https://fr.openfoodfacts.org/api/v0/product/{barcode}.json",
        f"https://de.openfoodfacts.org/api/v0/product/{barcode}.json",
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
                        p.get("product_name_it") or 
                        p.get("product_name_en") or 
                        p.get("title") or ""
                    )
                    
                    cat_raw = p.get("categories") or p.get("categories_tags", [""])[0]
                    if isinstance(cat_raw, str) and cat_raw:
                        scheda["categoria"] = cat_raw.split(",")[0].replace("en:", "").replace("it:", "").strip().capitalize()
                    
                    scheda["foto"] = p.get("image_front_url") or p.get("image_url") or p.get("image_front_small_url") or ""
                    scheda["quantita_netta"] = p.get("quantity") or p.get("product_quantity") or ""
                    scheda["ingredienti"] = p.get(f"ingredients_text_{lingua}") or p.get("ingredients_text") or p.get("ingredients_text_it") or ""
                    scheda["allergeni"] = p.get("allergens_from_ingredients") or p.get("allergens", "")
                    scheda["calorie"] = p.get("nutriments", {}).get("energy-kcal_100g", "") or p.get("nutriments", {}).get("energy-kcal", "")
                    
                    break
        except Exception as e:
            print(f"⚠️ Tentativo fallito con {url_off}: {e}")

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

        # Nuova API per gli alert dei 10 giorni (Menu principale)
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
                    
                    # Regole cromatiche per gli alert e liste
                    if is_tassativo:
                        badge_style = 'tassativo'      # Rosso / Scritta Bianca
                    else:
                        badge_style = 'consigliata'    # Giallo / Scritta Nera

                    prodotti_in_scadenza.append({
                        'id': item.get('barcode') or item.get('nome'),
                        'nome': item.get('nome'),
                        'scadenza': scad_date.strftime('%d/%m/%Y'),
                        'giorni_rimasti': giorni_rimasti,
                        'ubicazione': item.get('ubicazione', 'Non specificata'),
                        'tassativo': is_tassativo,
                        'badge_style': badge_style
                    })

            # Ordina per urgenza crescente (da scaduto/oggi a 10 giorni)
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

        # Nuova API per la Lista della Spesa Preventiva con codici colore
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

                # Regola: Esaurimento scorta (Quantità rimasta a 1 pezzo) -> Sfondo Blu, Scritta Bianca
                if quantita == 1:
                    lista_spesa.append({
                        'nome': item.get('nome'),
                        'motivo': 'In esaurimento (rimasto solo 1 pezzo)',
                        'categoria_colore': 'esaurimento', # Blu / Bianca
                        'stato_testo': '🔵 Suggerimento Scorta'
                    })
                    continue

                # Regola: Scadenze imminenti (entro 10 giorni)
                if scad_date and scad_date <= soglia_10_giorni:
                    if is_tassativo:
                        colore = 'tassativo'    # Rosso / Bianca
                        testo = '🔴 Scadenza Tassativa Imminente'
                    else:
                        colore = 'consigliata'  # Giallo / Nera
                        testo = '🟡 Scadenza Consigliata Imminente'

                    lista_spesa.append({
                        'nome': item.get('nome'),
                        'motivo': f"Scade il {scad_date.strftime('%d/%m/%Y')}",
                        'categoria_colore': colore,
                        'stato_testo': testo
                    })
                # Regola: Senza scadenza ed esauriti (Quantità 0) -> Sfondo Scuro, Scritta Bianca
                elif tipo_scadenza == 'nessuna' and quantita == 0:
                    lista_spesa.append({
                        'nome': item.get('nome'),
                        'motivo': 'Prodotto esaurito',
                        'categoria_colore': 'senza_scadenza', # Sfondo scuro / Bianca
                        'stato_testo': '⬛ Nessuna Scadenza'
                    })

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({'shopping_list': lista_spesa}, ensure_ascii=False).encode("utf-8"))
            return

        if parsed_url.path == "/save_scan":
            barcode = query_components.get("barcode", [""])[0]
            if barcode == "":
                ULTIMA_SCANSIONE.clear()
                ULTIMA_SCANSIONE.update({
                    "barcode": "", "nome": "", "categoria": "", "foto": "", 
                    "quantita_netta": "", "ingredienti": "", "allergeni": "", "calorie": "", "found": False
                })
            elif barcode:
                print(f"📱 Ricevuto codice a barre dal cellulare: {barcode}")
                info_prodotto = compone_scheda_prodotto(barcode, "it")
                
                ULTIMA_SCANSIONE.clear()
                ULTIMA_SCANSIONE.update({
                    "barcode": barcode,
                    "nome": info_prodotto.get("nome", ""),
                    "categoria": info_prodotto.get("categoria", ""),
                    "foto": info_prodotto.get("foto", ""),
                    "quantita_netta": info_prodotto.get("quantita_netta", ""),
                    "ingredienti": info_prodotto.get("ingredienti", ""),
                    "allergeni": info_prodotto.get("allergeni", ""),
                    "calorie": info_prodotto.get("calorie", ""),
                    "found": info_prodotto.get("found", False)
                })

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            return

        if parsed_url.path == "/last_scan":
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(ULTIMA_SCANSIONE).encode("utf-8"))
            return

        if parsed_url.path == "/search":
            barcode = query_components.get("q", [""])[0]
            lingua = query_components.get("lang", ["it"])[0]
            scheda_risultato = compone_scheda_prodotto(barcode, lingua)

            if barcode:
                ULTIMA_SCANSIONE.clear()
                ULTIMA_SCANSIONE.update({
                    "barcode": barcode,
                    "nome": scheda_risultato.get("nome", ""),
                    "categoria": scheda_risultato.get("categoria", ""),
                    "foto": scheda_risultato.get("foto", ""),
                    "quantita_netta": scheda_risultato.get("quantita_netta", ""),
                    "ingredienti": scheda_risultato.get("ingredienti", ""),
                    "allergeni": scheda_risultato.get("allergeni", ""),
                    "calorie": scheda_risultato.get("calorie", ""),
                    "found": scheda_risultato.get("found", False)
                })
                print(f"📱 Rilevato codice via /search dal telefono (Lingua: {lingua}): {barcode}")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps(scheda_risultato).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        parsed_url = urllib.parse.urlparse(self.path)

        if parsed_url.path == "/save_pantry":
            content_length = int(self.headers.get('Content-Length', 0))
            post_data = self.rfile.read(content_length)
            try:
                item = json.loads(post_data.decode('utf-8'))
                dispensa_path = os.path.join(os.path.dirname(__file__), DISPENSA_FILE)
                dispensa = []
                if os.path.exists(dispensa_path):
                    with open(dispensa_path, "r", encoding="utf-8") as f:
                        try:
                            dispensa = json.load(f)
                        except:
                            dispensa = []
                
                dispensa.append(item)
                
                with open(dispensa_path, "w", encoding="utf-8") as f:
                    json.dump(dispensa, f, ensure_ascii=False, indent=4)
                
                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "ok"}).encode("utf-8"))
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()

# --- SERVIZIO UDP BROADCAST (Autodiscovery) ---
def start_udp_discovery_listener():
    def listen():
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(('', UDP_DISCOVERY_PORT))
            print(f"📡 Servizio UDP Autodiscovery in ascolto sulla porta {UDP_DISCOVERY_PORT}...")
            
            while True:
                data, addr = sock.recvfrom(1024)
                message = data.decode('utf-8').strip()
                if message == "DISCOVER_EATMEFIRST_SERVER":
                    sock.sendto(b"EATMEFIRST_SERVER_HERE", addr)
        except Exception as e:
            print(f"⚠️ Errore nel listener UDP: {e}")

    thread = threading.Thread(target=listen, daemon=True)
    thread.start()

if __name__ == "__main__":
    start_udp_discovery_listener()

    server_address = ("0.0.0.0", PORT)
    
    try:
        httpd = http.server.HTTPServer(server_address, CustomHandler)
        
        # Configurazione SSL per HTTPS (indispensabile per Brave su IP locali)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(certfile="cert.pem", keyfile="key.pem")
        httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"🔒 Server EatMeFirst HTTPS attivo sulla porta {PORT} (Sicuro per Brave)")
        
        httpd.serve_forever()
        
    except Exception as e:
        print(f"\n❌ ERRORE CRITICO ALL'AVVIO DEL SERVER: {e}")
    except KeyboardInterrupt:
        print("\nServer arrestato dall'utente.")
    
    input("\nPremi INVIO per chiudere la finestra...")