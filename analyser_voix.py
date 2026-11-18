import librosa
import numpy as np

# On pointe directement vers ton fichier .ogg enregistré depuis ton téléphone
fichier = "ma_vraie_voix.ogg"
print(f"[Analyse en cours de '{fichier}']...")

try:
    # Chargement de l'audio (librosa va utiliser soundfile en arrière-plan pour lire le .ogg)
    y, sr = librosa.load(fichier)

    # Extraction de la fréquence fondamentale (F0) avec librosa (pyin)
    f0, voiced_flag, voiced_probs = librosa.pyin(y, fmin=librosa.note_to_hz('C2'), fmax=librosa.note_to_hz('C7'))

    # On enlève les silences ou les moments où tu ne parles pas
    f0_nettes = f0[~np.isnan(f0)]

    if len(f0_nettes) > 0:
        frequence_moyenne = np.mean(f0_nettes)
        frequence_mediane = np.median(f0_nettes)
        
        print("\n==============================")
        print("📊 RÉSULTATS DE TON VRAI PROFIL VOCAL (TÉLÉPHONE) :")
        print("===============================")
        print(f"🔹 Fréquence moyenne (F0) : {frequence_moyenne:.2f} Hz")
        print(f"🔹 Fréquence médiane       : {frequence_mediane:.2f} Hz")
        print("===============================")
    else:
        print("[!] Aucune voix claire détectée. Assure-toi que tu parles bien dans le fichier.")

except Exception as e:
    print(f"[!] Erreur lors de l'analyse : {e}")