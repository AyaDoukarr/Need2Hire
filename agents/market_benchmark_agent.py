from services.llm_service import call_llm_json
from i18n import get_output_language_name


PROMPT_BENCHMARK_TEMPLATE = """
Tu es un expert en recrutement et análisis du marché du travail, spécialisé dans l'évaluation de fiches de poste.

Ton rôle :
Analyser une fiche de poste générée et l'évaluer d'un point de vue marché : exigence, précision, attractivité, alignement marché et risques.

Contexte :
- Famille métier : {job_family}
- Sous-famille métier : {job_subfamily}
- Langue de réponse : {output_language}

Informations à évaluer :
{fiche_poste}

Résultat brut de la qualification (pour contexte supplémentaire) :
{qualification_data}

Tâche :
Évalue la fiche de poste ci-dessus et fournis un benchmark complet.

Règles importantes :
- Réponds uniquement avec un JSON valide.
- N'ajoute aucun texte avant ou après le JSON.
- Sois précis et factuel dans tes évaluations.
- "niveau_exigence" évalue si les exigences sont réalistes par rapport au marché :
  - "too demanding" : exigences irréalistes, trop de compétences/missions demandées
  - "balanced" : bon équilibre entre exigences et reality market
  - "not demanding enough" : exigences trop faibles pour le niveau du poste
- "niveau_precision" évalue si le poste est bien défini :
  - "too vague" : poste flou, missions/responsabilités non claires
  - "correct" : niveau de détail adecuado
  - "very precise" : poste très détaillé, presque trop
- "attractivite_poste" évalue l'attractivité globale :
  - "low" : poste peu attractif (peu d'avantages, mission banale)
  - "medium" : poste attractif de façon standard
  - "high" : poste très attractif (impact, évolution, avantages, contexte)
- "alignement_marche" évalue l'alignement avec les standards du marché :
  - "low" : poste atypique, difficilement comparable
  - "medium" : poste dans la moyenne du marché
  - "good" : poste bien aligné avec les tendances actuelles
- "risques_marche" : liste des risques identifiés (max 3)
- "recommandations" : recommandations d'amélioration (max 3)
- "conclusion" : résumé professionnel en 1-2 phrases

Tu dois produire exactement cette structure JSON :
{{
  "niveau_exigence": "too demanding | balanced | not demanding enough",
  "niveau_precision": "too vague | correct | very precise",
  "attractivite_poste": "low | medium | high",
  "alignement_marche": "low | medium | good",
  "risques_marche": ["string"],
  "recommandations": ["string"],
  "conclusion": "string"
}}
"""


def build_benchmark_prompt(job_family: str, job_subfamily: str, fiche_poste: dict, lang: str) -> str:
    import json
    
    fiche_str = json.dumps(fiche_poste, ensure_ascii=False, indent=2)
    
    # Extraction des infos clés pour le contexte supplémentaire
    qualification_data = {
        "intitule": fiche_poste.get("intitule_poste", ""),
        "experience": fiche_poste.get("niveau_experience", ""),
        "contrat": fiche_poste.get("type_contrat", ""),
        "localisation": fiche_poste.get("localisation", ""),
    }
    qual_str = json.dumps(qualification_data, ensure_ascii=False, indent=2)
    
    return PROMPT_BENCHMARK_TEMPLATE.format(
        job_family=job_family,
        job_subfamily=job_subfamily,
        output_language=get_output_language_name(lang),
        fiche_poste=fiche_str,
        qualification_data=qual_str,
    )


def run_market_benchmark(job_family: str, job_subfamily: str, fiche_poste: dict, lang: str = "fr"):
    """
    Runs the market benchmark analysis on a generated job description.
    
    Args:
        job_family: The detected job family
        job_subfamily: The detected job subfamily
        fiche_poste: The generated AXA job description dict
        lang: Language code (fr, en, es)
    
    Returns:
        dict: Market benchmark results with required fields
    """
    prompt = build_benchmark_prompt(job_family, job_subfamily, fiche_poste, lang)
    return call_llm_json(prompt, "", temperature=0.2)