# Need2Hire — Assistant IA de qualification des besoins de recrutement

## Contexte

Dans de nombreux processus de recrutement, la qualité du besoin initial est déterminante.
Un besoin mal structuré ou incomplet entraîne des incompréhensions, des retards et des décisions moins fiables.

Need2Hire est un prototype d’assistant basé sur l’intelligence artificielle visant à améliorer cette phase clé en apportant une aide à la structuration, à l’analyse et à la prise de décision.

---

## Objectif

L’application a pour objectif de :

* Structurer un besoin de recrutement à partir d’un texte libre
* Identifier les informations manquantes ou imprécises
* Générer une fiche de poste exploitable
* Apporter une aide à la décision via des indicateurs métier

Ce prototype s’inscrit dans une démarche de validation de valeur avant industrialisation.

---

## Fonctionnalités

### Analyse du besoin

* Extraction des éléments clés (intitulé, missions, profil, localisation, contrat)
* Détection des incohérences et zones floues
* Identification des informations manquantes pertinentes

### Scoring métier

* Score global de qualité du besoin
* Score de confiance de l’analyse
* Détail des indicateurs (complétude, précision, screening, structure)

### Aide à la décision

* Recommandation sur l’état du besoin (prêt / à compléter / à revoir)
* Checklist qualité
* Questions de clarification ciblées (si nécessaire)

### Génération de livrables

* Fiche de poste structurée
* Email de brief recruteur prêt à l’envoi
* Support de préparation d’entretien

---

## Architecture

L’application repose sur une architecture modulaire :

* `app.py` : interface utilisateur (Streamlit)
* `orchestration/` : pipeline de traitement
* `agents/` : logique d’extraction et d’analyse
* `domain/` : scoring métier
* `validation/` : validation des entrées
* `ui/` : composants d’affichage
* `data/` : référentiels métiers AXA

---

## Technologies utilisées

* Python
* Streamlit
* Modèles LLM (via Groq / OpenAI compatible API)
* Traitement de texte et structuration JSON

---

## Déploiement

L’application est déployée via Streamlit Cloud.

### Prérequis

* Python 3.10+
* Fichier `requirements.txt`

### Variables d’environnement

Les clés API doivent être définies dans les variables d’environnement ou dans les secrets Streamlit :

```
GROQ_API_KEY = "..."
GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_AUDIO_MODEL = "whisper-large-v3-turbo"
```

---

## Limites du prototype

* Les résultats dépendent de la qualité du modèle LLM utilisé
* Les calculs de score reposent sur des heuristiques métier
* L’application n’est pas connectée aux systèmes RH internes

---

## Positionnement

Ce prototype ne remplace pas la décision RH.
Il vise à :

* Structurer la réflexion
* Réduire les zones d’incertitude
* Améliorer la qualité des échanges entre manager et recruteur

---

## Perspectives

* Connexion aux outils RH (ATS, référentiels internes)
* Personnalisation par métier et entité
* Amélioration du scoring via données historiques
* Intégration dans un workflow de recrutement complet

---

## Auteur

Projet réalisé dans le cadre d’un travail de recherche et développement autour de l’usage de l’intelligence artificielle appliquée au recrutement.
