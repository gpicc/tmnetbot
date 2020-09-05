from pyrogram import idle

from . import mongo, periodic_task
from .mongo import admins
from .telegram import telegram


def main():
    mongo.init()
    telegram.start()
    periodic_task.start()
    print("Bot on")

    if admins.count_documents({}) == 0:
        print("[!] Usa /makemeadmin per diventare admin senza intervenire manualmente")
        print("[!] dal database. Funziona solamente quando non è rilevato alcun admin.")

    idle()
    print("Il bot verrà fermato.\n")
    telegram.stop()
