import os
from flask import Flask, render_template_string, request, jsonify
from google import genai

app = Flask(__name__)

# Récupération de la clé API depuis l'environnement Render
CLE_API_GEMINI = os.getenv("GEMINI_API_KEY", "TA_CLE_PAR_DEFAUT")
client = genai.Client(api_key=CLE_API_GEMINI)

# Liste des modèles avec bascule automatique en cas de surcharge
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

# Interface HTML/CSS intégrée (Design moderne, sombre style J.A.R.V.I.S.)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>J.A.R.V.I.S. Mobile</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0d1117; color: #c9d1d9; margin: 0; padding: 20px; }
        h1 { color: #58a6ff; text-align: center; font-size: 1.5rem; }
        .tabs { display: flex; justify-content: center; margin-bottom: 20px; gap: 10px; }
        .tab-btn { background: #21262d; border: 1px solid #30363d; color: #c9d1d9; padding: 10px 20px; border-radius: 8px; cursor: pointer; font-weight: bold; }
        .tab-btn.active { background: #1f6feb; border-color: #1f6feb; color: white; }
        .section { display: none; background: #161b22; padding: 20px; border-radius: 12px; border: 1px solid #30363d; box-shadow: 0 4px 12px rgba(0,0,0,0.5); }
        .section.active { display: block; }
        textarea, input[type="text"] { width: 100%; padding: 12px; margin: 10px 0; background: #0d1117; border: 1px solid #30363d; color: white; border-radius: 8px; box-sizing: border-box; }
        button.action-btn { background: #238636; color: white; border: none; padding: 12px 20px; width: 100%; border-radius: 8px; font-weight: bold; cursor: pointer; font-size: 1rem; }
        button.action-btn:hover { background: #2ea043; }
        .result-box { margin-top: 15px; padding: 15px; background: #0d1117; border-left: 4px solid #58a6ff; border-radius: 4px; white-space: pre-wrap; }
    </style>
</head>
<body>
    <h1>J.A.R.V.I.S. Assistant Mobile</h1>
    
    <div class="tabs">
        <button class="tab-btn active" onclick="switchTab('interprete')">🗣️ Interprète</button>
        <button class="tab-btn" onclick="switchTab('apprentissage')">🧠 Apprentissage</button>
    </div>

    <!-- Section Interprète -->
    <div id="interprete" class="section active">
        <h3>Pont de Traduction</h3>
        <p>Tape ou colle la phrase à traduire :</p>
        <textarea id="texteInput" rows="3" placeholder="Écris ici (Français ou Anglais)..."></textarea>
        <button class="action-btn" onclick="traduireTexte()">Traduire & Transmettre</button>
        <div class="result-box" id="resultatInterprete">En attente d'une action...</div>
    </div>

    <!-- Section Apprentissage Personnel -->
    <div id="apprentissage" class="section suppuration">
        <h3>Espace Apprentissage & Projets</h3>
        <p>Pose une question pour ton code, tes projets ou ta veille technique :</p>
        <textarea id="questionApprentissage" rows="3" placeholder="Ex: Comment optimiser ma plateforme webtoon 'resto' ?"></textarea>
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

        async function traduireTexte() {
            const texte = document.getElementById('texteInput').value;
            document.getElementById('resultatInterprete').innerText = "Traduction en cours...";
            const res = await fetch('/api/traduire', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({texte: texte})
            });
            const data = await res.json();
            document.getElementById('resultatInterprete').innerText = data.reponse;
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
    prompt = f"Traduis et adapte cette phrase de façon professionnelle et claire : '{texte}'"
    reponse = generer_avec_secours(prompt)
    return jsonify({'reponse': reponse})

@app.route('/api/apprentissage', methods=['POST'])
def api_apprentissage():
    data = request.json
    question = data.get('question', '')
    prompt = f"Tu es le mentor technique et l'assistant personnel de Tuchia Bienvenu Chancelin (23 ans, profil technique, projets de plateforme webtoon). Réponds de manière précise, structurée et motivante à sa requête : '{question}'"
    reponse = generer_avec_secours(prompt)
    return jsonify({'reponse': reponse})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)