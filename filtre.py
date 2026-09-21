#!/home/andre/safeguard/venv/bin/python3
from email.message import EmailMessage
from pypdf import PdfReader
import smtplib
import docx
import io
import sys
import os
import email
import tempfile
import magic
import hashlib
import sqlite3
from datetime import datetime

DOSSIER_PROJET = os.path.dirname(os.path.abspath(__file__))

EXTENSIONS_ATTENDUES = {
    "application/pdf": [".pdf"],
    "image/png": [".png"],
    "image/jpeg": [".jpg", ".jpeg"],
    "image/gif": [".gif"],
    "text/plain": [".txt"],
    "text/csv": [".csv"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": [".xlsx"],
    "application/vnd.openxmlformats-officedocument.presentationml.presentation": [".pptx"],
    "application/msword": [".doc"],
    "application/vnd.ms-excel": [".xls"],
    "application/zip": [".zip"],
    "application/x-rar": [".rar"],
    "application/x-7z-compressed": [".7z"],
}

TYPES_DANGEREUX = {
    "application/x-dosexec": "exécutable Windows (.exe)",
    "application/x-executable": "exécutable Linux",
    "application/x-sh": "script shell",
    "application/x-msdownload": "exécutable Windows",
}
MOTS_CLES_SENSIBLES = [
    "confidentiel", "confidential", "secret", "ne pas divulguer",
    "usage interne", "strictement confidentiel", "top secret",
]

def extraire_texte(contenu, vrai_type):
    try:
        if vrai_type == "application/pdf":
            reader = PdfReader(io.BytesIO(contenu))
            return " ".join(page.extract_text() or "" for page in reader.pages)
        elif vrai_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            d = docx.Document(io.BytesIO(contenu))
            return " ".join(p.text for p in d.paragraphs)
        elif vrai_type == "text/plain":
            return contenu.decode("utf-8", errors="ignore")
    except Exception:
        return ""
    return ""

def contient_mot_sensible(texte):
    texte_minuscule = texte.lower()
    for mot in MOTS_CLES_SENSIBLES:
        if mot in texte_minuscule:
            return mot
    return None

def calculer_empreinte(chemin):
    sha256 = hashlib.sha256()
    with open(chemin, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()

def journaliser(nom, empreinte, vrai_type, extension, coherent, mot_sensible=None):
    conn = sqlite3.connect(os.path.join(DOSSIER_PROJET, "journal.db"))
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_fichier TEXT, empreinte TEXT, type_reel TEXT,
            extension_declaree TEXT, coherent INTEGER, date_analyse TEXT,
            mot_sensible TEXT
        )
    """)
    cur.execute("""
        INSERT INTO analyses (nom_fichier, empreinte, type_reel, extension_declaree, coherent, date_analyse, mot_sensible)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (nom, empreinte, vrai_type, extension, int(coherent), datetime.now().isoformat(), mot_sensible))
    conn.commit()
    conn.close()

def analyser_piece_jointe(nom_fichier, contenu):
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(contenu)
        chemin_tmp = tmp.name

    extension = os.path.splitext(nom_fichier)[1].lower()
    vrai_type = magic.from_buffer(contenu, mime=True)
    empreinte = calculer_empreinte(chemin_tmp)
    os.unlink(chemin_tmp)

    if vrai_type in TYPES_DANGEREUX:
        journaliser(nom_fichier, empreinte, vrai_type, extension, False)
        return False, f"type de fichier dangereux ({TYPES_DANGEREUX[vrai_type]})"

    nom_sans_derniere_ext = os.path.splitext(nom_fichier)[0]
    if os.path.splitext(nom_sans_derniere_ext)[1]:
        journaliser(nom_fichier, empreinte, vrai_type, extension, False)
        return False, "double extension suspecte"

    texte = extraire_texte(contenu, vrai_type)
    mot_trouve = contient_mot_sensible(texte)
    if mot_trouve:
        journaliser(nom_fichier, empreinte, vrai_type, extension, False, mot_trouve)
        return False, f"contenu sensible détecté (mot-clé : {mot_trouve})"

    extensions_valides = EXTENSIONS_ATTENDUES.get(vrai_type, [])
    coherent = extension in extensions_valides

    journaliser(nom_fichier, empreinte, vrai_type, extension, coherent)
    if not coherent:
        return False, f"incohérence : extension {extension} mais type réel {vrai_type}"
    return True, None

def notifier_expediteur(sender, sujet_original, raisons):
    notif = EmailMessage()
    notif["Subject"] = f"[SAFEGUARD] Envoi bloqué : {sujet_original}"
    notif["From"] = "safeguard@localhost"
    notif["To"] = sender
    corps = "Votre mail a été bloqué par Safeguard pour la raison suivante :\n\n"
    corps += "\n".join(f"- {r}" for r in raisons)
    corps += "\n\nContactez l'administrateur si vous pensez qu'il s'agit d'une erreur."
    notif.set_content(corps)

    with smtplib.SMTP("127.0.0.1", 10025) as smtp:
        smtp.sendmail("safeguard@localhost", [sender], notif.as_bytes())

def mettre_en_quarantaine(msg):
    horodatage = datetime.now().strftime("%Y%m%d_%H%M%S")
    chemin = os.path.join(DOSSIER_PROJET, "quarantaine", f"{horodatage}.eml")
    with open(chemin, "wb") as f:
        f.write(msg.as_bytes())
    return chemin

def main():
    sender = sys.argv[1]
    recipients = sys.argv[2:]

    raw = sys.stdin.buffer.read()
    msg = email.message_from_bytes(raw)

    raisons = []
    for part in msg.walk():
        nom = part.get_filename()
        if nom:
            contenu = part.get_payload(decode=True)
            if contenu:
                ok, raison = analyser_piece_jointe(nom, contenu)
                if not ok:
                    raisons.append(f"{nom} : {raison}")

    if raisons:
        mettre_en_quarantaine(msg)
        notifier_expediteur(sender, msg.get("Subject", ""), raisons)
        sys.exit(0)

    with smtplib.SMTP("127.0.0.1", 10025) as smtp:
        smtp.sendmail(sender, recipients, msg.as_bytes())

if __name__ == "__main__":
    main()
