<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EatMeFirst - Connexion et Choix du Mode de Chargement</title>
    <style>
        :root {
            --bg-color: #12181b;
            --card-bg: #1e272c;
            --primary-color: #2ecc71;
            --text-color: #e0e6ed;
            --text-muted: #a0aec0;
            --border-color: #2d3748;
            --info-bg: #1a2634;
            --info-border: #3182ce;
            --accent-hover: #27ae60;
            --warning-bg: #2d2415;
            --warning-border: #f39c12;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 0;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
        }

        /* En-tête Supérieur */
        .top-navbar {
            width: 100%;
            background-color: #101416;
            padding: 12px 24px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-sizing: border-box;
            border-bottom: 1px solid var(--border-color);
        }

        .brand-logo {
            display: flex;
            align-items: center;
            gap: 10px;
            text-decoration: none;
            color: #ffffff;
            font-size: 1.3rem;
            font-weight: bold;
        }

        .brand-logo img {
            height: 36px;
            width: auto;
        }

        .language-flags {
            display: flex;
            gap: 12px;
            align-items: center;
        }

        .flag-icon {
            width: 30px;
            height: 20px;
            cursor: pointer;
            object-fit: cover;
            border-radius: 3px;
            transition: transform 0.2s;
            border: 1px solid rgba(255,255,255,0.2);
            display: inline-block;
        }

        .flag-icon:hover {
            transform: scale(1.15);
        }

        /* Disposition Principale */
        .main-wrapper {
            padding: 30px 20px;
            width: 100%;
            max-width: 850px;
            box-sizing: border-box;
        }

        .container {
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 35px;
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
            border: 1px solid var(--border-color);
        }

        .header {
            display: flex;
            flex-direction: column;
            align-items: center;
            text-align: center;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 25px;
            margin-bottom: 25px;
        }

        .presentation-img {
            width: 120px;
            height: 120px;
            border-radius: 50%;
            border: 3px solid var(--primary-color);
            object-fit: cover;
            box-shadow: 0 4px 15px rgba(0,0,0,0.4);
            margin-bottom: 15px;
        }

        .header-text h1 {
            margin: 0;
            color: var(--primary-color);
            font-size: 2rem;
        }

        .header-text p {
            margin: 8px 0 0 0;
            color: var(--text-muted);
            font-size: 1.1rem;
        }

        p, li {
            line-height: 1.7;
            color: var(--text-color);
            font-size: 1.02rem;
        }

        .highlight-box {
            background-color: var(--info-bg);
            border-left: 4px solid var(--info-border);
            padding: 20px;
            border-radius: 6px;
            margin: 25px 0;
        }

        .terms-box {
            background-color: #161d21;
            padding: 20px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin: 25px 0;
        }

        /* SÉLECTION DE LA MÉTHODE - ÉTAT DÉSACTIVÉ PAR DÉFAUT */
        .method-selection {
            background-color: #161d21;
            padding: 25px;
            border-radius: 8px;
            border: 1px solid var(--border-color);
            margin: 30px 0;
            opacity: 0.4;
            pointer-events: none;
            transition: all 0.4s ease;
        }

        .method-selection.enabled {
            opacity: 1;
            pointer-events: auto;
        }

        .method-options {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-top: 15px;
        }

        .method-btn {
            background-color: #1e272c;
            border: 2px solid var(--border-color);
            color: var(--text-color);
            padding: 14px 20px;
            border-radius: 8px;
            text-align: left;
            font-size: 1.05rem;
            cursor: pointer;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .method-btn:hover {
            border-color: var(--primary-color);
            background-color: #222e35;
        }

        .method-btn.selected {
            border-color: var(--primary-color);
            background-color: rgba(46, 204, 113, 0.1);
            font-weight: bold;
        }

        /* Boîte QR Code et Guide pour le Smartphone */
        .smartphone-warning-box {
            display: none;
            background-color: var(--warning-bg);
            border: 1px solid var(--warning-border);
            border-left: 4px solid var(--warning-border);
            padding: 25px;
            border-radius: 8px;
            margin: 20px 0;
            animation: fadeIn 0.4s ease-in;
        }

        .qr-card-container {
            background: #ffffff;
            padding: 15px;
            border-radius: 10px;
            width: 170px;
            height: 170px;
            margin: 20px auto;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            text-align: center;
        }

        .qr-card-container img {
            width: 130px;
            height: 130px;
            object-fit: contain;
        }

        #finalSection {
            margin-top: 35px;
            border-top: 2px solid var(--border-color);
            padding-top: 25px;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .btn-container {
            text-align: center;
        }

        .btn-start {
            display: inline-block;
            padding: 14px 35px;
            background-color: var(--primary-color);
            color: #12181b;
            text-decoration: none;
            border-radius: 8px;
            font-weight: bold;
            font-size: 1.2rem;
            transition: all 0.2s;
            box-shadow: 0 4px 12px rgba(46, 204, 113, 0.3);
            border: none;
            cursor: not-allowed;
            opacity: 0.5;
            pointer-events: none;
        }

        .btn-start.active {
            cursor: pointer;
            opacity: 1;
            pointer-events: auto;
        }

        .btn-start:hover.active {
            background-color: var(--accent-hover);
            transform: scale(1.03);
        }
    </style>
</head>
<body>

<!-- En-tête Supérieur -->
<header class="top-navbar">
    <a href="../menu.html" class="brand-logo">
        <img src="../../IMG/logo_1024_white.png" alt="EatMeFirst Logo">
        <span>EatMeFirst</span>
    </a>
    <div class="language-flags">
        <a href="../../IT/chargement/collegamento.html" title="Italiano"><img src="../../IMG/bandiera_Italy.jpg" alt="Italiano" class="flag-icon"></a>
        <a href="../../EN/chargement/collegamento.html" title="English"><img src="../../IMG/bandiera_England.jpg" alt="English" class="flag-icon"></a>
        <a href="../../DE/chargement/collegamento.html" title="Deutsch"><img src="../../IMG/bandiera_Germany.jpg" alt="Deutsch" class="flag-icon"></a>
        <a href="connexion.html" title="Français"><img src="../../IMG/bandiera_France.jpg" alt="Français" class="flag-icon" style="opacity: 1;"></a>
        <a href="../../ES/chargement/carga.html" title="Español"><img src="../../IMG/bandiera_Espana.jpg" alt="Español" class="flag-icon"></a>
    </div>
</header>

<div class="main-wrapper">
    <div class="container">
        
        <div class="header">
            <img src="../../IMG/Leo_technicien_informatique.png" alt="Leo le Programmeur" class="presentation-img">
            <div class="header-text">
                <h1>Nous y voilà, c'est Leo</h1>
                <p>Le programmeur de la maison à votre disposition</p>
            </div>
        </div>

        <p>Bonjour <span class="user-name-span">l'ami</span>, comme Max vous l'a dit, ici vous êtes en sécurité : votre ordinateur s'est transformé en un serveur privé et autonome rien que pour vous, sans rien charger sur des clouds externes[cite: 1].</p>
        
        <div class="highlight-box">
            <strong>🔒 La vérification avec l'antivirus</strong><br><br>
            Avant de continuer, faisons la vérification promise par Max : faites un clic droit sur le dossier où vous avez extrait EatMeFirst et choisissez <em>« Analyser avec Windows Defender »</em> (ou votre antivirus préféré). Il vous donnera immédiatement le feu vert complet ![cite: 1]
        </div>

        <!-- 1. ACCEPTATION DES TERMES ET CONDITIONS -->
        <div class="terms-box">
            <p style="margin-top: 0; font-weight: bold; color: var(--primary-color);">Dernière formalité :</p>
            <p style="margin-bottom: 15px; font-size: 0.98rem; color: var(--text-muted);">Il ne reste plus qu'une dernière formalité, à savoir l'acceptation des conditions de fourniture. Si vous souhaitez les lire, vous pouvez cliquer sur le <a href="../conditions.html" target="_blank" style="color: var(--info-border);">lien des conditions</a>, sinon vous pouvez procéder en cochant la case ci-dessous[cite: 1].</p>
            
            <label style="display: flex; align-items: center; gap: 12px; cursor: pointer; font-size: 1.05rem;">
                <input type="checkbox" id="termsCheck" onchange="toggleTerms()" style="width: 20px; height: 20px; accent-color: var(--primary-color);">
                <span>J'accepte les conditions d'utilisation et les termes d'EatMeFirst[cite: 1].</span>
            </label>
        </div>

        <!-- 2. CHOIX DE LA MÉTHODE DE CHARGEMENT -->
        <div class="method-selection" id="methodSelectionBox">
            <strong>Quelle solution souhaitez-vous adopter pour saisir les codes-barres dans votre garde-manger ?</strong>[cite: 1]
            <div class="method-options">
                <button type="button" class="method-btn" onclick="selectMethod(this, 'smartphone')">
                    📱 <span>Smartphone recyclé en tant que scanner Wi-Fi (Recommandé, Coût 0)[cite: 1]</span>
                </button>
                <button type="button" class="method-btn" onclick="selectMethod(this, 'pistola')">
                    🔌 <span>Douchette laser USB[cite: 1]</span>
                </button>
                <button type="button" class="method-btn" onclick="selectMethod(this, 'manuale')">
                    ⌨️ <span>Saisie manuelle au clavier[cite: 1]</span>
                </button>
            </div>
        </div>

        <!-- CODE QR ET AVIS RASSURANT POUR LE SMARTPHONE -->
        <div class="smartphone-warning-box" id="smartphoneWarning">
            <strong style="color: var(--primary-color); font-size: 1.2rem;">📱 Connexion Smartphone via Code QR</strong>[cite: 1]<br><br>
            <p style="margin: 0 0 12px 0;">
                <span class="user-name-span">L'ami</span>, vous avez choisi d'utiliser votre ancien smartphone. Scannez le code QR ci-dessous avec l'appareil photo du téléphone[cite: 1] :
            </p>

            <!-- Box visuelle avec Code QR dynamique du réseau local -->
            <div class="qr-card-container">
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=150x150&data=https://192.168.1.72:8888/FR/chargement/chargement.html" alt="Code QR Connexion Smartphone">[cite: 1]
                <span style="font-size: 0.65rem; color: #333; margin-top: 4px; font-weight: bold;">https://192.168.1.72:8888</span>[cite: 1]
            </div>

            <!-- EXPLICATION DE L'IP LOCALE -->
            <div style="background-color: rgba(255, 255, 255, 0.05); border-radius: 6px; padding: 12px 15px; margin: 15px 0;">
                <strong style="color: #ffffff; font-size: 0.95rem;">💡 Qu'est-ce que l'adresse 192.168.1.72 ?</strong>[cite: 1]
                <p style="margin: 5px 0 0 0; font-size: 0.92rem; color: var(--text-color);">
                    Les chiffres commençant par <code>192.168...</code> identifient de manière exclusive les réseaux domestiques privés. Ce nombre est la « plaque d'immatriculation interne » de votre PC sur le Wi-Fi de la maison : il confirme que le téléphone communique <strong>uniquement et exclusivement avec votre ordinateur</strong> et non avec des sites externes sur Internet[cite: 1].
                </p>
            </div>

            <p style="margin: 10px 0;">
                Sur l'ordinateur portable comme sur le téléphone, des avertissements ou des messages en rouge dans la barre d'adresse peuvent apparaître : c'est le comportement normal lorsque deux appareils communiquent sur un réseau local en utilisant une adresse sécurisée avec le <strong>« S »</strong> de <code>https://</code>. Par mesure de sécurité, Windows et le navigateur vous avertissent de cette anomalie, mais soyez rassuré : vous êtes toujours à l'intérieur de votre PC et de votre réseau domestique protégé[cite: 1].
            </p>
            
            <p style="margin: 10px 0; color: var(--text-muted); font-size: 0.95rem;">
                <em>Remarque : tous les navigateurs ne se comportent pas de la même manière ; certains sont plus tolérants et le message rouge peut donc ne pas s'afficher du tout[cite: 1].</em>
            </p>

            <strong style="color: #ffffff; display: block; margin-top: 15px;">Que faire si l'écran de blocage apparaît :</strong>[cite: 1]
            <ol style="margin: 8px 0 0 0; padding-left: 20px; font-size: 0.98rem;">
                <li>Cliquez sur <strong>« Avancé »</strong> puis sur <strong>« Continuer vers 192.168.1.72 (non sécurisé) »</strong>[cite: 1].</li>
                <li>Lorsque le téléphone vous demandera l'autorisation d'accéder à l'appareil photo, sélectionnez <strong>« Autoriser »</strong>[cite: 1].</li>
            </ol>
        </div>

        <!-- SECTION FINALE (Bouton de Démarrage) -->
        <div id="finalSection" class="btn-container">
            <button type="button" id="btnProceed" onclick="avviaProgramma()" class="btn-start">Lancer le Programme →</button>[cite: 1]
        </div>

    </div>
</div>

<script>
    let selectedMethodValue = "";

    document.addEventListener('DOMContentLoaded', () => {
        const savedName = localStorage.getItem('eatmefirst_username_fr');
        if (savedName && savedName.trim() !== "") {
            document.querySelectorAll('.user-name-span').forEach(el => {
                el.textContent = savedName.trim();
            });
        }
    });

    function toggleTerms() {
        const checkbox = document.getElementById('termsCheck');
        const methodBox = document.getElementById('methodSelectionBox');

        if (checkbox.checked) {
            methodBox.classList.0 ? methodBox.classList.add('enabled') : methodBox.className += " enabled";
        } else {
            methodBox.classList.remove('enabled');
            document.getElementById('smartphoneWarning').style.display = 'none';
            selectedMethodValue = "";
            const buttons = document.querySelectorAll('.method-btn');
            buttons.forEach(btn => btn.classList.remove('selected'));
        }
        updateStartButton();
    }

    function selectMethod(element, method) {
        selectedMethodValue = method;
        
        const buttons = document.querySelectorAll('.method-btn');
        buttons.forEach(btn => btn.classList.remove('selected'));
        element.classList.add('selected');

        const warningBox = document.getElementById('smartphoneWarning');

        if (method === 'smartphone') {
            warningBox.style.display = 'block';
        } else {
            warningBox.style.display = 'none';
        }

        updateStartButton();
        document.getElementById('finalSection').scrollIntoView({ behavior: 'smooth' });
    }

    function updateStartButton() {
        const checkbox = document.getElementById('termsCheck');
        const btn = document.getElementById('btnProceed');

        if (checkbox.checked && selectedMethodValue !== "") {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    }

    function avviaProgramma() {
        if (!document.getElementById('termsCheck').checked || selectedMethodValue === "") return;

        if (selectedMethodValue === 'smartphone') {
            window.location.href = window.location.origin + "/FR/chargement/chargement.html";
        } else {
            window.location.href = "chargement.html"; 
        }
    }
</script>

</body>
</html>