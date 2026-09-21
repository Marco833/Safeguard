# ADR 003 : Filtrage des mails sortants (DCS), pas entrants

## Statut
Accepté

## Contexte
La première version du projet filtrait les mails **entrants** (port 25), ce qui correspond à une protection de boîte de réception, pas à du DCS (Data Leak/Loss Prevention). Le sujet demande de détecter les fuites de données **avant expédition** — c'est-à-dire filtrer les mails **sortants**, envoyés par un utilisateur interne vers l'extérieur. Erreur identifiée suite à retour du professeur.

## Décision
- Retrait du `content_filter` global sur le port 25 (entrant)
- Activation du filtre uniquement sur le port `submission` (587), dédié à l'envoi de mails par les clients authentifiés
- Le moteur de détection (4 mécanismes) reste inchangé — seul le point d'interception change

## Conséquences
- Positif : le filtre protège maintenant le bon flux (sortant), conforme à l'objectif DCS
- Positif : aucune réécriture du moteur de détection nécessaire, seulement la configuration Postfix
- Point de vigilance : en production, le port submission nécessiterait une authentification SMTP (SASL) pour identifier l'expéditeur réel ; non implémenté à ce stade car hors périmètre du jalon 1, prévu si nécessaire au rendu final
- À faire ensuite : basculer l'action du filtre de "marquer le sujet" vers un vrai blocage/chiffrement, cohérent avec le rendu final attendu en juin
