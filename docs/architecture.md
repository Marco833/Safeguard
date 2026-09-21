# Architecture technique

## Flux global

1. Un utilisateur interne envoie un mail avec pièce jointe depuis son client mail
2. **Postfix (port submission, 587)** reçoit le mail — c'est le point d'entrée dédié aux envois des utilisateurs internes, pas à la réception de mails externes
3. Le `content_filter` configuré sur ce port redirige le mail vers **`filtre.py`**, exécuté via un transport `pipe`
4. `filtre.py` extrait chaque pièce jointe et applique 4 mécanismes de détection, dans cet ordre :
   1. Type de fichier dangereux (exécutables, scripts)
   2. Double extension suspecte
   3. Mot-clé sensible dans le contenu extrait (PDF, DOCX, TXT)
   4. Cohérence entre l'extension déclarée et le type réel (magic bytes)
5. Chaque analyse est journalisée dans **`journal.db`** (SQLite) : empreinte SHA-256, type réel, cohérence, mot déclencheur le cas échéant
6. **Si une alerte est levée** :
   - le mail est sauvegardé intégralement dans `quarantaine/` (format `.eml`)
   - l'expéditeur reçoit une notification précisant la pièce jointe et la raison du blocage
   - le mail n'est **jamais transmis** au destinataire externe
7. **Si aucune alerte** : le mail est réinjecté dans **Postfix (port 127.0.0.1:10025)**, un point d'entrée local sans `content_filter`, pour livraison normale

## Pourquoi filtrer le port submission (587) et non le port 25 ?

Le port 25 reçoit les mails **entrants**, venant de l'extérieur — les filtrer ne prévient aucune fuite de données. Le port submission (587) reçoit les mails **envoyés par les utilisateurs internes** : c'est le bon point d'interception pour du DCS (Data Loss/Leak Prevention), puisque l'objectif est d'empêcher une fuite avant qu'elle ne sorte de l'organisation. Voir `docs/adr/003-filtrage-sortant.md` pour le détail de cette correction.

## Pourquoi un second port Postfix (10025) ?

Sans ce second point d'entrée, un mail validé et réinjecté par le filtre repasserait par le même `content_filter`, créant une boucle infinie (`too many hops`). Le port 10025 est configuré pour accepter uniquement les connexions locales (`127.0.0.0/8`) et ne réapplique pas le filtre.

## Composants et rôle de chacun

| Composant | Rôle | Technologie |
|---|---|---|
| Postfix (submission, 587) | Réception des mails sortants internes | Paquet Debian standard |
| filtre.py | Analyse de contenu et décision blocage/passage | Python 3.13, venv dédié |
| python-magic | Détection du type réel (magic bytes) | Bibliothèque Python |
| pypdf / python-docx | Extraction de texte | Bibliothèques Python |
| journal.db | Traçabilité de toutes les analyses | SQLite |
| quarantaine/ | Archivage des mails bloqués | Fichiers `.eml` horodatés |
| Postfix (127.0.0.1:10025) | Réinjection des mails validés, sans filtre | Paquet Debian standard |
