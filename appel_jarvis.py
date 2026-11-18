import os
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from google import genai
import keyboard

# --- CONFIGURATION ---
CLE_API_GEMINI = os.getenv("GEMINI_API_KEY", "ta_cle_ici_si_tu_veux_tester_en_local")

# Liste des modèles avec bascule automatique en cas de surcharge
LISTE_MODELES = [
    "gemini-3.5-flash-lite", # Modèle principal, ultra-rapide et économique
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite"
]

client = genai.Client(api_key=CLE_API_GEMINI)

def generer_avec_secours(contents):
    """Essaie les modèles de la liste un par un en cas de surcharge"""
    derniere_erreur = None
    for modele in LISTE_MODELES:
        try:
            reponse = client.models.generate_content(
                model=modele,
                contents=contents
            )
            return reponse
        except Exception as e:
            derniere_erreur = e
            continue
    raise derniere_erreur

def traduire_et_afficher(fichier_audio):
    """Envoie l'audio à Gemini et affiche uniquement la traduction texte à l'écran"""
    try:
        print("🧠 Analyse et traduction intelligente...")
        audio_ref = client.files.upload(file=fichier_audio)
        
        prompt = """
        Écoute cet enregistrement audio en anglais. Traduis-le immédiatement en un français clair, professionnel et direct. 
        Donne UNIQUEMENT la traduction française, sans aucune phrase d'introduction ni de mise en forme complexe.
        """
        
        reponse = generer_avec_secours([audio_ref, prompt])
        texte_traduit = reponse.text.strip()
        
        print(f"\n🇫🇷 [FRANÇAIS] : {texte_traduit}\n" + "-"*50)
        
    except Exception as e:
        print(f"⚠️ Erreur (modèles surchargés) : {str(e)}")

# --- BOUCLE PRINCIPALE ---
if __name__ == "__main__":
    print("=== PONT D'INTERPRÉTARIAT VISUEL J.A.R.V.I.S. ===")
    print("• Appuie sur [ESPACE] pour COMMENCER à écouter ton frère.")
    print("• Appuie sur [ESPACE] une deuxième fois pour ARRÊTER et afficher la traduction.")
    print("• Appuie sur [CTRL + C] pour quitter.\n")

    fs = 44100

    while True:
        try:
            print("--------------------------------------------------")
            print("🟢 Prêt. Appuie sur [ESPACE] pour écouter ton frère...")
            
            # Première pression : Démarre l'écoute
            keyboard.wait('space')
            time.sleep(0.2)
            
            print("🎧 [Écoute en cours...] Laisse ton frère parler... (Appuie de nouveau sur ESPACE pour stopper)")
            
            frames = []
            stream = sd.InputStream(samplerate=fs, channels=1, dtype='int16', callback=lambda ind, fc, ti, st: frames.append(ind.copy()))
            stream.start()
            
            # Deuxième pression : Stoppe l'écoute
            keyboard.wait('space')
            
            stream.stop()
            stream.close()
            time.sleep(0.2)
            
            if frames:
                fichier_audio = "appel_tmp.wav"
                write(fichier_audio, fs, np.concatenate(frames, axis=0))
                traduire_et_afficher(fichier_audio)

        except KeyboardInterrupt:
            print("\nArrêt de l'interpréteur.")
            break