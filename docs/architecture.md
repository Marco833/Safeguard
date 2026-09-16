# Architecture technique

## Flux global

1. Un client mail envoie un message vers `andre@localhost`
2. **Postfix (port 25)** reçoit le mail via SMTP standard
3. Le `content_filter` de Postfix redirige le mail vers **`filtre.py`**, exécuté via un transport `pipe`
4. `filtre.py` extrait chaque pièce jointe et applique 4 mécanismes de détection, dans cet ordre :
   1. Type de fichier dangereux (exécutables, scripts)
   2. Double extension suspecte
   3. Mot-clé sensible dans le contenu extrait (PDF, DOCX, TXT)
   4. Cohérence entre l'extension déclarée et le type réel (magic bytes)
5. Chaque analyse est journalisée dans **`journal.db`** (SQLite) : empreinte SHA-256, type réel, cohérence, mot déclencheur le cas échéant
6. Si une alerte est levée, le sujet du mail est préfixé par `[ALERTE SAFEGUARD]`
7. Le mail est réinjecté dans **Postfix (port 10025)**, un point d'entrée configuré sans `content_filter`, pour éviter une boucle infinie
8. Le mail est livré dans la boîte du destinataire

## Pourquoi un second port Postfix (10025) ?

Sans ce second point d'entrée, le mail réinjecté par le filtre repasserait par le même `content_filter`, créant une boucle infinie (`too many hops`). Le port 10025 est configuré pour accepter uniquement les connexions locales (`127.0.0.0/8`) et ne réapplique pas le filtre.

## Composants et rôle de chacun

| Composant | Rôle | Technologie |
|---|---|---|
| Postfix | Réception et livraison SMTP | Paquet Debian standard |
| filtre.py | Analyse de contenu | Python 3.13, venv dédié |
| python-magic | Détection du type réel (magic bytes) | Bibliothèque Python |
| pypdf / python-docx | Extraction de texte | Bibliothèques Python |
| journal.db | Traçabilité des analyses | SQLite |
