================================================================================
           PRÉSENTATION TECHNIQUE : IA DE QUALIFICATION DU BESOIN DE RECRUTEMENT
                              SQORUS | IA RH
================================================================================

SLIDE 1 : RÉSUMÉ EXÉCUTIF
--------------------------------------------------------------------------------

Problème métier
-Transformer les demandes de recrutement vague des managers en fiches de poste structurées et exploitables
-Eliminar les aller-retour entre RH et managers (délai typique : 2 à 3 semaines)
-Standardiser les fiches de poste selon le format et la taxonomie AXA
-Permettre un screening objectif des candidats avec des critères d'évaluation clairs

Objectif de l'application
-Transformer un besoin exprimé en naturel langage en une fiche de poste AXA prête à l'emploi
-Identifier les informations manquantes et les termes flous
-Générer des critères de screening et des questions d'entretien
-Qualifier le besoin avec un score de maturité


SLIDE 2 : CONTEXTE ET ENJEUX
--------------------------------------------------------------------------------

Problèmes liés aux besoins de recrutement mal définis
-Les managers expriment leur besoin de manière imprecise ("Nous cherchons un bon profil data")
-Manque de precision sur les competencies, l'experience requise, les missions
-Terminologie floue et subjective ("junior", "senior", "autonome")
-Absence de critères objectifs pour évaluer les candidats

Impact côté RH
-Difficulté à comprendre le vrai besoin du manager
-Performance tiempo excessive pour qualifié le besoin (2-3 semaines)
-Risque de mauvais screening et de candidats non adapter
-Incohérence avec la taxonomie métier du groupe

Impact côté managers
-Diffculté à exprimer clairement leur besoin
-Echanges multiples pour préciser les informations
-Delai avant d'avoir une fiche de poste utilisable
-Incertitude sur la qualité du profil retenu


SLIDE 3 : PRÉSENTATION DE LA SOLUTION
--------------------------------------------------------------------------------

Ce que fait l'application
-Entrée : besoin en texte libre, audio ou fichier existant
-Traitement : analyse multi-étapes avec agentes IA spécialisés
-Sortie : fiche de poste structurée, score de qualification, critères de screening

Valeur apportée
-Réduction du temps de qualification de 40-60%
-Standardisation automatique selon le format AXA
-Critères objectifs pour le screening des CV
-Amélioration de la qualité des candidatures
-Décision éclairée pour les équipes RH


SLIDE 4 : PARCOURS FONCTIONNEL
--------------------------------------------------------------------------------

1. Saisie du besoin
   -Texte libre (langage naturel)
   -Audio (enregistrement vocal)
   -Fichier (fiche existante)

2. Validation
   -Vérification de la longueur minimale
   -Consolidation des informations

3. Analyse
   -Détection de la famille métier (45 familles)
   -Détection de la sous-famille
   -Identification des termes flous
   -Détection des informations manquantes

4. Génération de la fiche de poste
   -Structure AXA (10+ champs)
   -Critères d'évaluation
   -Questions d'entretien
   -Risques détectés

5. Scoring
   -Score global sur 100
   -Niveau de confiance (25-95%)
   -Recommandations

6. Restitution
   -Fiche de poste AXA
   -Brief recruiter
   -Rapport de qualification


SLIDE 5 : ARCHITECTURE TECHNIQUE
--------------------------------------------------------------------------------

1. Couche UI (app.py)
   -Interface Streamlit
   -Gestion des entrées utilisateur
   -Affichage des résultats
   -Gestion de l'état de session

2. Couche Orchestration (orchestration/pipeline.py)
   -Coordination du pipeline
   -Enchaînement des étapes
   -Gestion des erreurs
   -Passage des paramètres


3. Couche Agents (agents/)
   -extractor_agent.py : extraction et génération de fiche
   -family_router_agent.py : détection famille métier
   -subfamily_router_agent.py : détection sous-famille
   -quality_agent.py : validation de la qualité
   -market_benchmark_agent.py : analyse concurrentielle
   -summary_agent.py : résumé exécutif

4. Couche Métier (domain/)
   -scoring.py : calcul du score de qualification
   -matching.py : scoring familles/sous-familles
   -rules.py : règles métier et seuils
   -schemas.py : validation des données

5. Couche Validation (validation/)
   -validation.py : validation des entrées
   -Fonctions utilitaires

6. Couche Services (services/)
   -llm_service.py : intégration LLM (Groq)
   -audio_service.py : transcription audio

7. Couche Données (data/)
   -data_layer.py : taxonomie et données de référence
   -Fichiers CSV : taxonomie AXA, référentiels


SLIDE 6 : FLUX DE DONNÉES
--------------------------------------------------------------------------------

Entrée utilisateur ("Nous cherchons un chef de projet data senior...")
         │
         ▼
Validation (validation/validation.py)
-Vérification longueur minimale
-Nettoyage du texte
         │
         ▼
Pré-matching Python (domain/matching.py)
-Scoring sur 45 familles métier
-Seuil de confiance
         │
         ▼
Family Router Agent (agents/family_router_agent)
-Confirmation LLM si incertain
-Score de confiance
         │
         ▼
Sous-famille
-Scoring Python sur sous-familles
-Router LLM si nécessaire
         │
         ▼
Extractor Agent (agents/extractor_agent)
-Génération fiche de poste JSON
-Termes flous, informations manquantes
-Critères, questions d'entretien
         │
         ▼
Scoring (domain/scoring.py)
-5 dimensions (0-100 chacune)
-Score global et confiance
-Recommandations
         │
         ▼
Sortie
-Fiche AXA structurée
-Rapport de qualification


SLIDE 7 : UTILISATION DE L'IA
--------------------------------------------------------------------------------

Plusieurs agents spécialisés
-Chaque agent a une expertise précise
-Famille router : connaissance taxonomie
-Extractor : structuration de fiche
-Quality : validation de sortie
-Market benchmark : analyse concurrentielle

Génération structurée (JSON)
-Sortie JSON stricte avec validation
-Chaînes LLM avec validation de structure
-Pas de texte libre non structuré

Rôle du LLM dans chaque étape
1. Détection famille : confirmer classification Python
2. Extraction : générer fiche structurée
3. Quality : valider structure et contenu
4. Benchmark : analyser le marché
5. Summary : résumer pour le recruteur


SLIDE 8 : LOGIQUE DE SCORING
--------------------------------------------------------------------------------

5 Dimensions évaluées (chacune sur 20 points)

1. Complétude structurante (20 pts)
   -Champs présents : intitulé, contrat, expérience, société, famille, localisation
   -Pénalité pour informations manquantes critiques

2. Précision du besoin (20 pts)
   -Nombre de termes flous détectés
   -Informations critiques manquantes
   -Contradictions

3. Exploitabilité screening (20 pts)
   -Critères d'évaluation présents
   -Éléments actionnables dans le profil
   -Questions d'entretien

4. Clarté des missions (20 pts)
   -Nombre de missions actionnables
   -Spécificité vs langage générique

5. Conformité AXA (20 pts)
   -Alignement structure AXA
   -Sections requises présentes

Score global : moyenne des 5 dimensions (0-100)

Niveau de confiance : 25-95%
-Basé sur complétude et cohérence
-Faible : entrée incomplète/ambiguë
-Moyen : utile mais需validation RH
-Élevé : cohérent et opérationnel


SLIDE 9 : POINTS FORTS DE LA SOLUTION
--------------------------------------------------------------------------------

Architecture modulaire
-Séparation claire des responsabilités
-Chaque agent est indépendant
-Facile à maintenir et faire évoluer
-Tests unitaires par composant

Aide à la décision RH
-Score objectif de qualification
-Niveau de confiance explicite
-Recommandations actionnables
-Risques identifiés

Automatisation intelligente
-Routing Python avant IA (rapide, économique)
-LLM seulement si nécessaire
-Qualité garantie par validation
-Erreur récupérable sans re-exécution


SLIDE 10 : LIMITES ACTUELLES
--------------------------------------------------------------------------------

Dépendance au LLM
-Dépendance à un modèle externe (Groq/Llama)
-Risque d'évolution du comportement
-Potentiel d'hallucination (atténué par validation)

Limites API
-Rate limits (requêtes/minute)
-Stratégie de fallback nécessaire
-File d'attente pour fort volume

Absence d'intégration outils RH
-Entrée manuelle des données
-Pas de synchro ATS
-Pas de gestion des candidats
-Pas de génération d'offre


SLIDE 11 : PERSPECTIVES
--------------------------------------------------------------------------------

Court terme (Q2-Q3 2026)
-Intégration ATS interne (Workday)
-Expansion taxonomie entreprise
-Support multi-langues

Moyen terme (Q4 2026)
-Benchmark salarial temps réel
-Analyse concurrentielle automatique
-Algorithme de matching candidat
-Tableau de bord analytique

Long terme (2027+)
-Modèle prédictif de succès
-Construction automatique du pipeline
-Planification entretien automatisée
-Automatisation complète du recrutement

Optimisation
-Cache pour requêtes répétées
-Traitement par lots
-Modèle fine-tuné personnalisé

================================================================================
                          FIN DE LA PRÉSENTATION
================================================================================