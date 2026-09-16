# ADR 002 : Choix des 4 mécanismes de détection

## Statut
Accepté

## Contexte
Le jalon 1 exige de détecter les "signaux faibles" : écart nom ↔ contenu, extension ≠ type réel. Une seule règle de cohérence nom/type ne suffit pas à couvrir tous les cas de camouflage réalistes (le cas test officiel "recette de tarte" implique un fichier au nom et au type parfaitement cohérents, mais au contenu sensible).

## Décision
Quatre règles appliquées en cascade, dans cet ordre précis :

1. **Type dangereux** (`TYPES_DANGEREUX`) : bloque tout exécutable ou script quelle que soit l'extension déclarée. Priorité maximale car c'est la menace la plus grave (compromission du poste).
2. **Double extension** : détecte les noms du type `facture.pdf.exe`. Appliquée avant la vérification de cohérence classique, car un fichier à double extension est toujours suspect indépendamment de son contenu.
3. **Mot-clé sensible dans le contenu** : extraction de texte (PDF, DOCX, TXT) et recherche de termes comme "confidentiel". C'est la règle la plus proche du cas d'usage réel du DLP — un fichier bien nommé peut quand même contenir des données sensibles.
4. **Cohérence extension / type réel** (magic bytes) : la vérification de base, qui capture les cas non couverts par les règles précédentes.

L'ordre est important : dès qu'une règle détecte un problème, l'analyse s'arrête et journalise la cause précise (traçabilité).

## Conséquences
- Positif : chaque alerte journalisée indique précisément quelle règle a été déclenchée, utile pour l'explication à l'oral et pour un futur ajustement des règles
- Négatif : la liste de mots-clés sensibles est statique — un texte reformulé pour éviter les mots-clés n'est pas détecté (limite documentée dans `analyse-risque.md`)
- Point de vigilance technique : ajouter une colonne à la table SQLite `analyses` après sa création nécessite une migration manuelle (`ALTER TABLE`), le simple `CREATE TABLE IF NOT EXISTS` ne suffit pas — rencontré en pratique lors de l'ajout de la colonne `mot_sensible`
