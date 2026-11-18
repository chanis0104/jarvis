import asyncio
import os
import time
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
import speech_recognition as sr
from google import genai
import edge_tts
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

VOIX_CONFIG = {
    "voix": "en-GB-RyanNeural",  
    "pitch": "+0Hz",            
    "rate": "+0%"               
}

def creer_chat_avec_secours(client):
    """Initialise une session de chat en testant les modèles disponibles"""
    for modele in LISTE_MODELES:
        try:
            chat = client.chats.create(model=modele)
            print(f"[✔] Modèle actif initialisé : {modele}")
            return chat
        except Exception:
            continue
    raise Exception("Tous les modèles Gemini sont injoignables actuellement.")

def enregistrer_global_hotkey(fichier="entree.wav"):
    """Enregistre via le raccourci global : Ctrl + Espace"""
    fs = 44100
    frames = []

    def callback(indata, frames_count, time_info, status):
        frames.append(indata.copy())

    print("\n🎧 [J.A.R.V.I.S. en veille...] Appuie sur [CTRL + ESPACE] pour parler.")
    keyboard.wait('ctrl+space')
    
    print("🔴 [ENREGISTREMENT EN COURS...]")
    stream = sd.InputStream(samplerate=fs, channels=1, dtype='int16', callback=callback)
    stream.start()

    time.sleep(0.5)
    keyboard.wait('ctrl+space')
    
    stream.stop()
    stream.close()

    print("⏹️ [Traitement en cours...]")
    if frames:
        audio_data = np.concatenate(frames, axis=0)
        write(fichier, fs, audio_data)
        return fichier
    return None

def transcrire_audio(fichier_audio):
    """Convertit l'audio en texte français"""
    r = sr.Recognizer()
    with sr.AudioFile(fichier_audio) as source:
        audio = r.record(source)
    try:
        texte = r.recognize_google(audio, language="fr-FR")
        print(f"Toi (FR) : {texte}")
        return texte
    except sr.UnknownValueError:
        print("J.A.R.V.I.S. : Je n'ai rien entendu de distinct.")
        return None
    except sr.RequestError:
        print("J.A.R.V.I.S. : Problème de connexion Internet.")
        return None

def cerveau_jarvis_intelligent(chat_session, texte_fr):
    """Distingue un ordre direct (avec 'Javis') d'une traduction/discussion"""
    
    texte_min = texte_fr.lower().strip()
    
    if texte_min.startswith("javis") or texte_min.startswith("jarvis"):
        print("[⚙️ Ordre système détecté avec le nom]")
        ordre = texte_min.replace("javis", "").replace("jarvis", "").strip()
        
        prompt_cmd = f"""
        Tu es le noyau système Windows de Tuchia. L'ordre de l'utilisateur est : "{ordre}".
        Donne UNIQUEMENT la commande Windows (CMD/PowerShell) exacte pour exécuter cet ordre sur le PC, sans aucun texte autour, sans guillemets, sans markdown.
        """
        commande = chat_session.send_message(prompt_cmd).text.strip()
        
        print(f"[⚙️ Exécution de la commande] : {commande}")
        try:
            os.system(commande)
            return "Command executed successfully, sir."
        except Exception:
            return "I couldn't execute that command, sir."
            
    else:
        prompt_trad = f"""
        Tu es J.A.R.V.I.S., l'assistant personnel de Tuchia Bienvenu Chancelin (23 ans, Camerounais, profil technique).
        Traduis fidèlement la phrase française suivante en un anglais naturel et professionnel, ou réponds-lui s'il s'agit d'une question. 
        Ne donne AUCUNE explication superflue, uniquement le résultat en anglais :
        "{texte_fr}"
        """
        reponse = chat_session.send_message(prompt_trad)
        return reponse.text.strip()

async def generer_audio_personnalise(texte_en):
    """Génère et lit la réponse audio"""
    fichier_sortie = f"reponse_{int(time.time())}.mp3"
    print(f"J.A.R.V.I.S. (EN) : {texte_en}")
    
    communicate = edge_tts.Communicate(
        text=texte_en, 
        voice=VOIX_CONFIG["voix"], 
        pitch=VOIX_CONFIG["pitch"], 
        rate=VOIX_CONFIG["rate"]
    )
    await communicate.save(fichier_sortie)
    
    os.system(f"start {fichier_sortie}")
    print("[✔] J.A.R.V.I.S. a parlé.")
    await asyncio.sleep(2)

# --- BOUCLE PRINCIPALE ---
if __name__ == "__main__":
    print("=== J.A.R.V.I.S. MODE INTELLIGENT ACTIF ===")
    print("• Dis 'Javis [ton ordre]' pour agir sur le PC.")
    print("• Parle normalement sans son nom pour traduire/discuter.")
    
    client = genai.Client(api_key=CLE_API_GEMINI)
    chat = creer_chat_avec_secours(client)
    chat.send_message("Tu es J.A.R.V.I.S., assistant personnel pour Tuchia Bienvenu Chanis, 23 ans, Camerounais, profil technique.")

    while True:
        try:
            fichier = enregistrer_global_hotkey()
            if fichier:
                texte_fr = transcrire_audio(fichier)
                if texte_fr:
                    phrase_en = cerveau_jarvis_intelligent(chat, texte_fr)
                    asyncio.run(generer_audio_personnalise(phrase_en))
        except KeyboardInterrupt:
            print("\nArrêt de J.A.R.V.I.S. À bientôt !")
            break