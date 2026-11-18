import sounddevice as sd
from scipy.io.wavfile import write

print("=== ENREGISTREMENT DE TA VOIX ===" )
print("Dans 3 secondes, parle clairement pendant 6 secondes (dis par exemple : 'Bonjour, je m'appelle Tucha Bienvenu Chanis, j'ai 23 ans et je suis camerounais').")

# Petit compte à rebours
import time
time.sleep(3)

fs = 44100
duree = 6  # en secondes
print("\n[🔴 ENREGISTREMENT EN COURS... PARLE !]")
audio = sd.rec(int(duree * fs), samplerate=fs, channels=1, dtype='int16')
sd.wait()

# Sauvegarde directe sous le bon nom au bon endroit
write("ma_voix.wav", fs, audio)
print("\n[✔] C'est dans la boîte ! Le fichier 'ma_voix.wav' a été créé avec succès dans ton dossier.")