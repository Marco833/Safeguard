# Installation et déploiement

Procédure testée sur Debian 13 (trixie).

## 1. Prérequis système

sudo apt install postfix mailutils libmagic1

Lors de l'installation de Postfix, choisir "Site internet" dans la fenêtre de configuration.

## 2. Environnement Python

Debian bloque pip install au niveau système (PEP 668). Un environnement virtuel est obligatoire :

cd ~/safeguard
python3 -m venv venv
source venv/bin/activate
pip install python-magic pypdf python-docx

Toujours vérifier que (venv) apparaît dans le prompt avant tout pip install, sous peine d'échec silencieux.

## 3. Configuration Postfix

Ajouter dans /etc/postfix/master.cf :

safeguard unix - n n - - pipe
  flags=Rq user=andre argv=/home/andre/safeguard/venv/bin/python3 /home/andre/safeguard/filtre.py ${sender} ${recipient}

127.0.0.1:10025 inet n - n - - smtpd
  -o content_filter=
  -o receive_override_options=no_unknown_recipient_checks,no_header_body_checks
  -o smtpd_helo_restrictions=
  -o smtpd_client_restrictions=
  -o smtpd_sender_restrictions=
  -o smtpd_recipient_restrictions=permit_mynetworks,reject
  -o mynetworks=127.0.0.0/8
  -o smtpd_authorized_xforward_hosts=127.0.0.0/8

Activer le filtre :

sudo postconf -e "content_filter=safeguard:dummy"
sudo systemctl reload postfix

Pourquoi le port 10025 ? Sans ce second point d'entrée sans filtre, le mail réinjecté reboucle indéfiniment dans le filtre (too many hops). Voir docs/architecture.md.

## 4. Initialisation de la base de données

La table SQLite se crée automatiquement au premier lancement du filtre. Si une modification de schéma est nécessaire sur une base existante (ajout de colonne), utiliser une migration manuelle :

python3 -c "
import sqlite3
conn = sqlite3.connect('journal.db')
conn.execute('ALTER TABLE analyses ADD COLUMN nom_colonne TYPE')
conn.commit()
"

## 5. Vérification du déploiement

sudo systemctl status postfix
sudo postconf content_filter

Test bout en bout avec le script envoyer_test.py fourni, puis vérification du sujet et du journal :

python3 envoyer_test.py
sudo grep "Subject:" /var/mail/andre | tail -1

## Problèmes rencontrés et solutions (retour d'expérience)

| Symptôme | Cause | Solution |
|---|---|---|
| externally-managed-environment sur pip install | Debian protège le Python système | Toujours utiliser un venv |
| too many hops | Le filtre réinjecte dans le même content_filter | Utiliser le port 10025 dédié |
| ModuleNotFoundError en prod mais pas en test manuel | pip install lancé hors du venv | Vérifier (venv) avant chaque install |
| sqlite3.OperationalError: table has no column | Colonne ajoutée au code mais pas à la base existante | Migration ALTER TABLE manuelle |
