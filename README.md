# Safeguard

DLP qui analyse le contenu réel des pièces jointes email, pas seulement les métadonnées.

## Le problème

Un DLP classique se contente de vérifier le nom et l'extension d'un fichier. Safeguard va plus loin : il lit le contenu réel de chaque pièce jointe pour détecter les tentatives de camouflage (un fichier confidentiel renommé en `.pdf` innocent, par exemple).

## État du projet

- [x] Jalon 1 (janvier) : analyse de contenu — **en cours**
- [ ] Rendu final (juin) : validation graduée

## Architecture (vue d'ensemble)

Un mail arrive → Postfix l'intercepte → un filtre Python analyse chaque pièce jointe (type réel, cohérence nom/contenu, mots-clés sensibles, doubles extensions) → alerte ou passage normal → journalisation dans SQLite.

## Décisions techniques

Voir `docs/adr/` pour l'historique des choix et leurs justifications.
