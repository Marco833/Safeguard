# Installation et déploiement

Procédure testée sur Debian 13 (trixie).

## 1. Prérequis système

sudo apt install postfix mailutils libmagic1

Lors de l'installation de Postfix, choisir "Site internet" dans la fenêtre de configuration.

⚠️ Le fichier `filtre.py` contient en première ligne un "shebang" (`#!/home/andre/safeguard/venv/bin/python3`) qui doit être adapté au chemin réel de chaque installation. Après avoir cloné le dépôt et créé le venv, modifier cette première ligne pour qu'elle pointe vers `/home/VOTRE-USERNAME/Safeguard/venv/bin/python3`.

Les autres chemins (base de données, quarantaine) sont calculés automatiquement par le script, aucune autre modification n'est nécessaire.

## 2. Environnement Python

Debian bloque pip install au niveau système (PEP 668). Un environnement virtuel est obligatoire :

cd ~/safeguard
python3 -m venv venv
source venv/bin/activate
pip install python-magic pypdf python-docx

Toujours vérifier que (venv) apparaît dans le prompt avant tout pip install, sous peine d'échec silencieux.

## 3. Configuration Postfix

Ajouter à la fin de `/etc/postfix/master.cf` le service pipe et le point de réinjection sans filtre :

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

Dans le même fichier, décommenter la ligne `submission` (généralement en tout début de fichier) et y ajouter le filtre :

submission inet n       -       y       -       -       smtpd
  -o content_filter=safeguard:dummy
  -o smtpd_recipient_restrictions=permit_mynetworks,reject

⚠️ Le `content_filter` global (`sudo postconf -e "content_filter=..."`) ne doit **pas** être utilisé — il filtrerait aussi les mails entrants (port 25), ce qui ne correspond pas à un usage DCS. Le filtre doit être appliqué uniquement sur le port `submission`, comme indiqué ci-dessus. Vérifier qu'il est bien vide :

sudo postconf content_filter
# doit renvoyer : content_filter =

Recharger Postfix :

sudo systemctl reload postfix

**Pourquoi le port 10025 ?** Sans ce second point d'entrée sans filtre, le mail réinjecté après analyse reboucle indéfiniment dans le filtre (`too many hops`). Voir `docs/architecture.md`.

**Pourquoi le port submission (587) et pas le port 25 ?** Le port 25 reçoit les mails entrants ; le port submission reçoit les mails envoyés par les utilisateurs internes. Voir `docs/adr/003-filtrage-sortant.md`.

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
sudo grep -A 3 "^submission" /etc/postfix/master.cf

Créer le dossier de quarantaine s'il n'existe pas :

mkdir -p quarantaine

Test bout en bout avec le script `envoyer_test.py` fourni (configuré pour envoyer sur le port 587), avec une pièce jointe piégée :

python3 envoyer_test.py
sudo grep "Subject:" /var/mail/andre | tail -1
ls -la quarantaine/

Le mail original ne doit pas atteindre le destinataire : la dernière ligne de `/var/mail/andre` doit afficher une notification `[SAFEGUARD] Envoi bloqué`, et un fichier `.eml` doit apparaître dans `quarantaine/`.

## Compatibilité testée

- **Debian 13** : installation et fonctionnement complet validés
- **Ubuntu** (24.04) : installation et fonctionnement complet validés (seule adaptation nécessaire : le shebang de `filtre.py`)
- **Kali Linux** : installation prévue, non testée à ce jour

Note : sur Ubuntu, consulter les logs Postfix avec `sudo tail -f /var/log/mail.log` plutôt que `journalctl -u postfix`.


## Problèmes rencontrés et solutions (retour d'expérience)

| Symptôme | Cause | Solution |
|---|---|---|
| externally-managed-environment sur pip install | Debian protège le Python système | Toujours utiliser un venv |
| too many hops | Le filtre réinjecte dans le même content_filter | Utiliser le port 10025 dédié |
| ModuleNotFoundError en prod mais pas en test manuel | pip install lancé hors du venv | Vérifier (venv) avant chaque install |
| sqlite3.OperationalError: table has no column | Colonne ajoutée au code mais pas à la base existante | Migration ALTER TABLE manuelle |
| Filtrage appliqué aux mails entrants au lieu de sortants | content_filter appliqué globalement (port 25) au lieu du port submission | Filtrer uniquement le port submission (587), laisser le port 25 sans filtre |
