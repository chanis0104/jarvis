import os
import telebot
from google import genai

# Récupération sécurisée des clés depuis le Cloud (ou valeurs locales de secours)
TOKEN = os.getenv("TELEGRAM_TOKEN", "9106698513:AAEK1K4jUA2SydDROnAXcjfuC5k61yxpncE")
CLE_API_GEMINI = os.getenv("GEMINI_API_KEY", "ta_cle_ici_si_tu_veux_tester_en_local")
bot = telebot.TeleBot(TOKEN)
client = genai.Client(api_key=CLE_API_GEMINI)

# Liste des modèles avec bascule automatique en cas de surcharge
LISTE_MODELES = [
    "gemini-3.5-flash-lite", # Modèle principal, ultra-rapide et économique
    "gemini-3.8-flash",
    "gemini-3.6-flash",
    "gemini-3.1-flash-lite"
]

def generer_avec_secours(contents):
    """Essaie les modèles un par un en cas de surcharge temporaire"""
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

@bot.message_handler(commands=['start'])
def envoyer_bienvenue(message):
    bot.reply_to(message, "salut Chanis, je suis en ligne 24h/24 sur le cloud ! Dis-moi tout.")

@bot.message_handler(func=lambda m: True)
def repondre_gemini(message):
    try:
        reponse = generer_avec_secours(message.text)
        bot.reply_to(message, reponse.text)
    except Exception as e:
        bot.reply_to(message, f"Erreur technique (tous les modèles sont surchargés) : {str(e)}")

if __name__ == "__main__":
    print("Bot Telegram prêt à tourner...")
    bot.infinity_polling()