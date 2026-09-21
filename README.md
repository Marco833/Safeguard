# Safeguard

DCS (Data Loss/Leak Prevention) qui analyse le contenu réel des pièces jointes email **sortantes**, pas seulement les métadonnées.

## Le problème

Un utilisateur peut faire fuiter des données sensibles vers l'extérieur en les envoyant par mail — que ce soit volontairement (camouflage d'un fichier confidentiel) ou par erreur. Safeguard intercepte les mails **avant leur envoi vers l'extérieur** et analyse le contenu réel de chaque pièce jointe pour détecter et bloquer ces fuites.

## Le fonctionnement

Un mail envoyé par un utilisateur interne passe par le port d'envoi (submission) de Postfix, qui le redirige vers Safeguard avant toute transmission externe. Si une pièce jointe est jugée à risque, le mail est bloqué, mis en quarantaine, et l'expéditeur reçoit une notification. Sinon, le mail part normalement.

## État du projet

- [x] Jalon 1 (janvier) : analyse de contenu, blocage des envois suspects — **en cours**
- [ ] Rendu final (juin) : validation graduée (chiffrement, portail 2FA, déblocage justifié)

## Détections mises en place

1. Types de fichiers dangereux (exécutables, scripts)
2. Doubles extensions suspectes (ex : `facture.pdf.exe`)
3. Mots-clés sensibles dans le contenu réel du fichier
4. Incohérence entre l'extension déclarée et le type réel

## Architecture (vue d'ensemble)

Voir `docs/architecture.md` pour le détail.

Un mail sortant est intercepté par Postfix (port submission) → analysé par `filtre.py` (4 mécanismes de détection) → bloqué et mis en quarantaine si suspect, ou transmis normalement sinon → journalisation systématique dans SQLite.

## Installation

Voir `docs/installation.md`.

## Décisions techniques

Voir `docs/adr/` pour l'historique des choix et leurs justifications, y compris la correction du filtrage entrant vers sortant (ADR 003).
