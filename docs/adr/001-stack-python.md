# ADR 001 : Choix de la stack technique

## Statut
Accepté

## Contexte
Le projet nécessite une stack simple à maîtriser (peu d'expérience en développement au départ), capable d'analyser du contenu de fichiers, et respectant la contrainte de souveraineté (aucune IA publique, tout doit tourner en local).

## Décision
- **Langage** : Python — écosystème riche pour l'analyse de fichiers (python-magic, pypdf, python-docx), syntaxe accessible pour un débutant
- **Serveur mail** : Postfix — standard open-source Linux, bien documenté, permet l'interception via un filtre de contenu
- **Stockage du journal** : SQLite — base de données fichier unique, aucun serveur à administrer, suffisant pour le volume du projet
- **Environnement d'isolation** : venv Python — Debian bloque l'installation de paquets Python au niveau système (PEP 668), un environnement virtuel est nécessaire

## Conséquences
- Positif : stack cohérente, tout en Python sauf Postfix, facile à documenter et à faire tourner sur une machine vierge
- Négatif : SQLite ne conviendrait pas à un volume de production élevé (non bloquant pour ce projet)
- Point de vigilance : toujours vérifier l'activation du venv avant `pip install`, sous peine d'échec silencieux (rencontré en pratique)
