# ADR 004 : Blocage réel de l'envoi (au lieu du simple marquage)

## Statut
Accepté

## Contexte
La version précédente se contentait de préfixer le sujet du mail avec `[ALERTE SAFEGUARD]` puis laissait l'envoi se poursuivre normalement. Ce comportement ne prévient aucune fuite : le destinataire externe recevait quand même le fichier sensible. Un vrai DCS doit empêcher l'envoi.

## Décision
- Un mail dont une pièce jointe déclenche une des 4 règles de détection n'est plus transmis au(x) destinataire(s)
- Le mail original est sauvegardé intégralement dans `quarantaine/` (format `.eml`, horodaté), consultable pour audit
- L'expéditeur reçoit une notification automatique précisant la raison exacte du blocage (fichier concerné + règle déclenchée)

## Conséquences
- Positif : conforme au principe du DCS — aucune fuite ne sort réellement
- Positif : traçabilité complète (journal SQLite + fichier `.eml` archivé)
- Point de vigilance : pas encore de mécanisme de déblocage — un faux positif bloque définitivement le mail sans recours pour l'instant. Le rendu final (juin) prévoit une validation graduée avec justification et 2FA pour couvrir ce cas
- Limite actuelle : la quarantaine n'a pas de purge automatique, un volume important de blocages remplirait le disque à terme
