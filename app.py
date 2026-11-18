import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

CLE_API_GEMINI = os.getenv("GEMINI_API_KEY", "TA_CLE_PAR_DEFAUT")
client = genai.Client(api_key=CLE_API_GEMINI)

LISTE_MODELES = [
    "gemini-3.5-flash-lite",
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite"
]

def generer_avec_secours(contents):
    for modele in LISTE_MODELES:
        try:
            reponse = client.models.generate_content(
                model=modele,
                contents=contents
            )
            return reponse.text
        except Exception:
            continue
    return "Erreur : Tous les modèles sont temporairement surchargés."

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Vocal Mobile</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
        h1 { color: #58a6ff; text-align: center; font-size: 1.5rem; }
        .tabs { display: flex; justify-content: center; margin-bottom: 20px; gap: 10px; }
        .tab-btn { background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .tab-btn.active { background: #1f6feb; border-color: #1f6feb; color: white; }
        .section { display: none; background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        .section.active { display: block; }
        button.action-btn { background: #238636; color: white; border: none; padding: 15px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 1.1rem; margin-top: 10px; }
        button.action-btn:hover { background: #2ea043; }
        button.mic-en { background: #8957e5; }
        button.mic-fr { background: #1f6feb; }
        .result-box { margin-top: 15px; padding: 15px; background: #0d1117; border-left: 4px solid #58a6ff; border-radius: 4px; white-space: pre-wrap; font-size: 1.1rem; }
        textarea, input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; background: #0d1117; border: 1px solid #30363d; color: white; border-radius: 8px; box-sizing: border-box; }
    </style>
</head>
<body>
    <h1>J.A.R.V.I.S. Interprète Vocal</h1>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('interprete')">🗣️ Interprète Direct</button>
        <button class="tab-btn" onclick="switchTab('apprentissage')">🧠 Apprentissage</button>
    </div>

    <!-- Section Interprète Vocal -->
    <div id="interprete" class="section active">
        <h3>Mode Bilingue Temps Réel</h3>
        
        <p>1. Écouter l'interlocuteur (Anglais ➔ Français textuel)</p>
        <button class="action-btn mic-en" onclick="ecouterAnglais()">🎙️ Écouter en Anglais</button>

        <p style="margin-top:20px;">2. Parler pour répondre (Français ➔ Anglais lu à voix haute)</p>
        <button class="action-btn mic-fr" onclick="parlerFrancais()">🎤 Parler en Français</button>

        <div class="result-box" id="resultatInterprete">Appuie sur un bouton pour commencer...</div>
    </div>

    <!-- Section Apprentissage Personnel -->
    <div id="apprentissage" class="section">
        <h3>Espace Apprentissage & Projets</h3>
        <textarea id="questionApprentissage" rows="3" placeholder="Ex: Comment structurer ma plateforme webtoon 'resto' ?"></textarea>
        <button class="action-btn" onclick="poserQuestion()">Consulter J.A.R.V.I.S.</button>
        <div class="result-box" id="resultatApprentissage">Prêt pour tes apprentissages...</div>
    </div>

    <script>
        function switchTab(tabId) {
            document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.getElementById(tabId).classList.add('active');
            event.currentTarget.classList.add('active');
        }

        // Synthèse vocale pour lire en anglais
        function lireEnAnglais(texte) {
            const utterance = new SpeechSynthesisUtterance(texte);
            utterance.lang = 'en-US';
            window.speechSynthesis.speak(utterance);
        }

        // 1. Écoute l'Anglais et traduit en Français
        function ecouterAnglais() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'en-US';
            recognition.interimResults = false;
            
            document.getElementById('resultatInterprete').innerText = "Écoute de l'anglais en cours...";
            
            recognition.onresult = async function(event) {
                const texteAnglais = event.results[0][0].transcript;
                document.getElementById('resultatInterprete').innerText = "Texte capté (EN) : " + texteAnglais + "\\nTraduction en cours...";
                
                const res = await fetch('/api/traduire', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({texte: texteAnglais, sens: 'en-fr'})
                });
                const data = await res.json();
                document.getElementById('resultatInterprete').innerText = "🇫🇷 Traduction :\\n" + data.reponse;
            };
            recognition.start();
        }

        // 2. Écoute le Français, traduit en Anglais et le lit à voix haute
        function parlerFrancais() {
            const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
            recognition.lang = 'fr-FR';
            recognition.interimResults = false;
            
            document.getElementById('resultatInterprete').innerText = "Écoute du français en cours...";
            
            recognition.onresult = async function(event) {
                const texteFrancais = event.results[0][0].transcript;
                document.getElementById('resultatInterprete').innerText = "Tu as dit (FR) : " + texteFrancais + "\\nTraduction vers l'anglais...";
                
                const res = await fetch('/api/traduire', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({texte: texteFrancais, sens: 'fr-en'})
                });
                const data = await res.json();
                document.getElementById('resultatInterprete').innerText = "🇬🇧 Traduction (Anglais) :\\n" + data.reponse;
                
                // Lecture automatique à haute voix pour l'interlocuteur
                lireEnAnglais(data.reponse);
            };
            recognition.start();
        }

        async function poserQuestion() {
            const question = document.getElementById('questionApprentissage').value;
            document.getElementById('resultatApprentissage').innerText = "Réflexion en cours...";
            const res = await fetch('/api/apprentissage', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({question: question})
            });
            const data = await res.json();
            document.getElementById('resultatApprentissage').innerText = data.reponse;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/traduire', methods=['POST'])
def api_traduire():
    data = request.json
    texte = data.get('texte', '')
    sens = data.get('sens', 'en-fr')
    
    if sens == 'en-fr':
        prompt = f"Traduis cette phrase anglaise en un français naturel et direct (donne uniquement la traduction sans fioritures) : '{texte}'"
    else:
        prompt = f"Traduis cette phrase française en un anglais naturel et direct (donne uniquement la traduction sans fioritures) : '{texte}'"
        
    reponse = generer_avec_secours(prompt)
    return jsonify({'reponse': reponse.strip()})

@app.route('/api/apprentissage', methods=['POST'])
def api_apprentissage():
    data = request.json
    question = data.get('question', '')
    prompt = f"Tu es le mentor technique de Tuchia Bienvenu Chancelin (projets webtoon, technique). Réponds de manière précise : '{question}'"
    reponse = generer_avec_secours(prompt)
    return jsonify({'reponse': reponse})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)