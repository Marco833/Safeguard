# Analyse de risque

## Méthode

Pour chaque menace : description, impact si elle se réalise, mesure mise en place, risque résiduel accepté.

## Menaces couvertes

### 1. Exfiltration de données via camouflage de fichier
**Menace** : un utilisateur (malveillant ou par erreur) renomme un fichier sensible avec une extension anodine (ex: `plan.docx` → `photo_vacances.pdf`) pour le faire sortir par mail sans éveiller de soupçon.
**Impact** : fuite de données confidentielles, potentiellement une violation RGPD si données personnelles.
**Mesure** : analyse du contenu réel via `python-magic` (lecture des magic bytes), comparaison avec l'extension déclarée.
**Risque résiduel** : un attaquant qui chiffre ou compresse le fichier avant envoi contourne cette détection (le contenu réel devient illisible).

### 2. Camouflage par double extension
**Menace** : un fichier nommé `facture.pdf.exe` peut tromper un utilisateur qui ne voit que la première partie du nom (extensions cachées par défaut sur certains systèmes).
**Impact** : exécution de code malveillant si le destinataire ouvre le fichier en pensant que c'est un PDF.
**Mesure** : détection systématique des doubles extensions, blocage automatique de l'envoi.
**Risque résiduel** : un nom de fichier à triple extension ou avec des caractères Unicode trompeurs (ex: caractères RTL) n'est pas couvert dans la version actuelle.

### 3. Fuite de données sensibles dans un fichier au nom neutre
**Menace** : un fichier parfaitement valide et bien nommé (ex: `notes_reunion.pdf`) contient malgré tout des informations confidentielles.
**Impact** : fuite de données que les contrôles nom/type ne peuvent pas détecter.
**Mesure** : extraction du texte (PDF, DOCX, TXT) et recherche de mots-clés sensibles.
**Risque résiduel** : liste de mots-clés statique, ne détecte pas une reformulation du contenu sensible, ni les fichiers images/scans sans OCR.

### 4. Exécutables déguisés
**Menace** : un exécutable ou script malveillant envoyé en pièce jointe.
**Impact** : compromission du poste du destinataire (malware).
**Mesure** : blocage systématique des types MIME dangereux (`application/x-dosexec`, scripts shell...), quelle que soit l'extension déclarée.
**Risque résiduel** : les formats non répertoriés dans `TYPES_DANGEREUX` (ex: macros dans un document Office) ne sont pas couverts par cette règle.

### 5. Faux positif bloquant un envoi légitime
**Menace** : une règle de détection se déclenche à tort sur un mail légitime (ex: un document contenant le mot "confidentiel" dans un contexte normal, sans fuite réelle).
**Impact** : blocage d'un envoi professionnel légitime, gêne opérationnelle pour l'utilisateur.
**Mesure** : notification systématique à l'expéditeur avec la raison précise du blocage, permettant de comprendre et signaler l'erreur.
**Risque résiduel** : aucun mécanisme de déblocage à ce stade (jalon 1) ; un mail bloqué à tort reste bloqué sans recours. Prévu au rendu final avec la validation graduée (justification + 2FA).

## Risques non couverts (hors périmètre jalon 1)

- Fichiers chiffrés ou dans une archive protégée par mot de passe (impossible d'analyser le contenu sans le mot de passe)
- Contenu caché dans les métadonnées EXIF d'une image
- Stéganographie (données cachées dans une image ou un fichier audio)
- Fuite via des canaux autres que le mail (USB, cloud personnel...) — prévu au rendu final avec le "connecteur multi-canal"
