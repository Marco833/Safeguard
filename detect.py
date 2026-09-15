import magic
import os
import hashlib
import sqlite3
from datetime import datetime

EXTENSIONS_ATTENDUES = {
    "application/pdf": [".pdf"],
    "image/png": [".png"],
    "image/jpeg": [".jpg", ".jpeg"],
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": [".docx"],
    "text/plain": [".txt"],
}

def calculer_empreinte(chemin_fichier):
    sha256 = hashlib.sha256()
    with open(chemin_fichier, "rb") as f:
        sha256.update(f.read())
    return sha256.hexdigest()

def init_journal():
    conn = sqlite3.connect("journal.db")
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nom_fichier TEXT,
            empreinte TEXT,
            type_reel TEXT,
            extension_declaree TEXT,
            coherent INTEGER,
            date_analyse TEXT
        )
    """)
    conn.commit()
    return conn

def verifier_coherence(chemin_fichier, conn):
    extension = os.path.splitext(chemin_fichier)[1].lower()
    vrai_type = magic.from_file(chemin_fichier, mime=True)
    empreinte = calculer_empreinte(chemin_fichier)

    extensions_valides = EXTENSIONS_ATTENDUES.get(vrai_type, [])
    coherent = extension in extensions_valides

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO analyses (nom_fichier, empreinte, type_reel, extension_declaree, coherent, date_analyse)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (chemin_fichier, empreinte, vrai_type, extension, int(coherent), datetime.now().isoformat()))
    conn.commit()

    if not coherent:
        return f"⚠️  ALERTE : {chemin_fichier} déclaré en '{extension}' mais contient en réalité '{vrai_type}'"
    return f"✓ OK : {chemin_fichier} cohérent"

# Tests
conn = init_journal()
fichiers_a_tester = ["recette.pdf", "recette_de_tarte.pdf"]

for fichier in fichiers_a_tester:
    print(verifier_coherence(fichier, conn))

conn.close()
