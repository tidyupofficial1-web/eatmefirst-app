/**
 * EatMeFirst - Gestore Schedulatore Messaggi Programmati
 */

async function controllaMessaggiProgrammati() {
    // 1. Verifica se l'utente ha accettato le condizioni e recupera la data d'inizio
    let consentDateStr = localStorage.getItem('eatmefirst_consent_date');
    
    // Se non ha accettato o manca la data, il conto non parte
    if (!consentDateStr || localStorage.getItem('eatmefirst_consent') !== 'accepted') {
        return; 
    }

    // 2. Calcola i giorni trascorsi dall'accettazione delle condizioni
    const dataInizio = new Date(consentDateStr);
    const oggi = new Date();
    const diffTempo = Math.abs(oggi - dataInizio);
    const giorniTrascorsi = Math.floor(diffTempo / (1000 * 60 * 60 * 24));

    // 3. Rileva la lingua attiva (IT, EN, DE, FR, ES)
    let userLang = (localStorage.getItem('eatmefirst_lang') || navigator.language || 'IT').substring(0, 2).toUpperCase();
    if (!['IT', 'EN', 'DE', 'FR', 'ES'].includes(userLang)) {
        userLang = 'IT';
    }

    // 4. Traguardi programmati aggiornati (5, 20, 45, 90, 110 giorni)
    const soglieTraguardi = [5, 20, 45, 90, 110];

    // 5. Controlla quale messaggio mostrare (uno alla volta per sessione)
    for (let g of soglieTraguardi) {
        let flagVisto = localStorage.getItem(`eatmefirst_msg_${g}_visto`);
        
        if (giorniTrascorsi >= g && flagVisto !== 'true') {
            await caricaEmostraMessaggio(userLang, g);
            break; // Mostra solo il primo disponibile in coda per evitare l'effetto raffica
        }
    }
}

/**
 * Fetch asincrono del file JSON dalla cartella messaggi/LINGUA/GIORNO.json
 */
async function caricaEmostraMessaggio(lingua, giorno) {
    try {
        // Percorso relativo calcolato dalla radice/menu verso la cartella messaggi
        const percorsoFile = `messaggi/${lingua}/${giorno}.json`;
        let risposta = await fetch(percorsoFile);
        
        if (!risposta.ok) throw new Error("File messaggio non trovato");
        
        let datiMsg = await risposta.json();
        mostraModalDinamica(datiMsg, giorno);

    } catch (errore) {
        console.log("⚠️ Impossibile caricare il messaggio programmato: ", errore);
    }
}

/**
 * Genera la modale grafica a schermo
 */
function mostraModalDinamica(dati, giorno) {
    const modalHTML = `
        <div id="scheduled-msg-modal" style="position: fixed; top:0; left:0; width:100%; height:100%; background: rgba(0,0,0,0.85); display:flex; align-items:center; justify-content:center; z-index:9999; padding:20px;">
            <div style="background: #161b22; border: 2px solid #3182ce; border-radius: 16px; max-width: 520px; width: 100%; padding: 25px; color: #f0f6fc; box-shadow: 0 10px 25px rgba(0,0,0,0.5); font-family: sans-serif;">
                <div style="display: flex; align-items: center; gap: 15px; margin-bottom: 15px; border-bottom: 1px solid #30363d; padding-bottom: 12px;">
                    <img src="${dati.avatar}" alt="Avatar" style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 2px solid #2ecc71;" onerror="this.style.display='none'">
                    <div>
                        <h3 style="margin:0; color: #bfdbfe; font-size: 1.2rem;">${dati.mittente}</h3>
                        <span style="font-size: 0.8rem; color: #8b949e;">Traguardo: Giorno ${giorno}</span>
                    </div>
                </div>
                <p style="font-size: 0.95rem; line-height: 1.6; color: #e0e6ed; margin-bottom: 20px;">
                    ${dati.testo}
                </p>
                <div style="text-align: right;">
                    <button onclick="chiudiEMemorizza(${giorno})" style="background: #238636; color: white; border: none; padding: 10px 20px; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 0.9rem;">
                        Grazie! 👍
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

/**
 * Segna il messaggio come visto nel localStorage e chiude la finestra
 */
function chiudiEMemorizza(giorno) {
    localStorage.setItem(`eatmefirst_msg_${giorno}_visto`, 'true');
    const modal = document.getElementById('scheduled-msg-modal');
    if (modal) modal.remove();
}

// Avvia il controllo all'apertura del menu
document.addEventListener('DOMContentLoaded', controllaMessaggiProgrammati);