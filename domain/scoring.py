from typing import Any, Dict, List

from i18n import tr
from validation.validation import (
    non_empty_list,
    is_missing_value,
    is_actionable_mission,
    is_actionable_profile_item,
    detect_source_maturity,
    detect_experience_in_text,
)

CRITICAL_MISSING_PATTERNS = [
    "intitulé",
    "type de contrat",
    "niveau d'expérience",
    "localisation",
    "societe du groupe",
]

def score_color(score):
    if score < 40:
        return "🔴"
    if score < 70:
        return "🟠"
    return "🟢"

def score_badge_class(score):
    if score < 40:
        return "badge-red"
    if score < 70:
        return "badge-orange"
    return "badge-green"

def classify_missing_info(informations_manquantes: List[str]):
    critical = []
    secondary = []
    for info in informations_manquantes:
        lowered = info.lower()
        if any(p in lowered for p in CRITICAL_MISSING_PATTERNS):
            critical.append(info)
        else:
            secondary.append(info)
    return critical, secondary

def compute_qualification_score(result, source_text: str = "", lang: str = "fr"):
    fiche = result.get("fiche_de_poste_axa", {})
    termes_flous = non_empty_list(result.get("termes_flous", []))
    informations_manquantes = non_empty_list(result.get("informations_manquantes", []))
    criteres = non_empty_list(result.get("criteres_d_evaluation", []))
    questions_entretien = non_empty_list(result.get("questions_entretien", []))
    missions = non_empty_list(fiche.get("votre_role_et_vos_missions", []))
    profil = non_empty_list(fiche.get("votre_profil", []))
    source_maturity = detect_source_maturity(source_text)

    critical_missing, secondary_missing = classify_missing_info(informations_manquantes)

    # Detecter le niveau d'experience dans le texte source AVANT de verifier la fiche
    source_experience = detect_experience_in_text(source_text) if source_text else {"detected": False}
    fiche_experience = fiche.get("niveau_experience", "")

    # Filtrer les informations manquantes si detectees dans le texte source
    if source_experience.get("detected"):
        # Supprimer "Niveau d'experience" des infos manquantes
        filtered_critical = []
        for info in critical_missing:
            if "niveau" not in info.lower() and "experience" not in info.lower():
                filtered_critical.append(info)
        critical_missing = filtered_critical
    
    # Si le niveau est dans le texte source mais pas dans la fiche, on le считаPresent
    niveau_final = fiche_experience if not is_missing_value(fiche_experience) else (source_experience.get("level", ""))

    core_fields = {
        tr("checklist_job_title", lang): fiche.get("intitule_poste", ""),
        "Type de contrat": fiche.get("type_contrat", ""),
        "Niveau d'expérience": niveau_final,
        "Société du groupe": fiche.get("societe_du_groupe", ""),
        "Famille métier": fiche.get("famille_metier", ""),
        "Localisation": fiche.get("localisation", "")
    }
    present_core = [label for label, value in core_fields.items() if not is_missing_value(str(value))]
    missing_core = [label for label, value in core_fields.items() if is_missing_value(str(value))]

    completeness_score = 20
    completeness_formula = []
    completeness_comments = []

    if missing_core:
        penalty = min(10, len(missing_core) * 2)
        completeness_score -= penalty
        completeness_formula.append(f"-{penalty} points : champs structurants manquants ({', '.join(missing_core)})")
    else:
        completeness_formula.append("+0 point : tous les champs structurants sont présents")

    if len(present_core) >= 5 and len(missions) >= 3 and len(profil) >= 3:
        completeness_score += 2
        completeness_formula.append("+2 points : structure suffisamment fournie")

    completeness_comments.append("Mesure si la base du besoin est assez complète pour lancer un recrutement.")
    completeness_score = max(0, min(20, completeness_score))

    precision_score = 20
    precision_formula = []
    precision_comments = []

    if len(termes_flous) == 0:
        precision_formula.append("+0 point : besoin clair, aucun terme flou")
    elif len(termes_flous) <= 2:
        precision_score -= 2
        termes_exemples = ", ".join([str(t.get("terme", ""))[:15] for t in termes_flous[:2]])
        precision_formula.append(f"-2 points : termes flous : {termes_exemples}...")
    elif len(termes_flous) <= 4:
        precision_score -= 5
        termes_exemples = ", ".join([str(t.get("terme", ""))[:12] for t in termes_flous[:3]])
        precision_formula.append(f"-5 points : termes generiques : {termes_exemples}...")
    else:
        precision_score -= 8
        termes_exemples = ", ".join([str(t.get("terme", ""))[:10] for t in termes_flous[:3]])
        precision_formula.append(f"-8 points : trop flou : {termes_exemples}...")

    if len(critical_missing) == 0:
        precision_formula.append("+0 point : toutes les infos critiques presentes")
    elif len(critical_missing) == 1:
        precision_score -= 3
        precision_formula.append(f"-3 points : info manquante : {critical_missing[0][:25]}...")
    elif len(critical_missing) == 2:
        precision_score -= 5
        precision_formula.append(f"-5 points : 2 infos critiques manquantes")
    else:
        precision_score -= 7
        precision_formula.append(f"-7 points : {len(critical_missing)} infos manquantes")

    if len(secondary_missing) > 0:
        penalty = min(3, len(secondary_missing))
        precision_score -= penalty
        precision_formula.append(f"-{penalty} points : informations secondaires encore à préciser")

    if source_maturity == "fiche_detaillee":
        precision_score += 2
        precision_formula.append("+2 points : source déjà très structurée")

    precision_comments.append("Mesure la clarté réelle du besoin et le risque d’ambiguïté.")
    precision_score = max(0, min(20, precision_score))

    screening_score = 0
    screening_formula = []
    screening_comments = []

    actionable_profile_count = sum(1 for p in profil if is_actionable_profile_item(p))

    if len(profil) >= 4 and actionable_profile_count >= 3:
        screening_score += 6
        screening_formula.append("+6 points : profil détaillé et exploitable")
    elif len(profil) >= 2 and actionable_profile_count >= 2:
        screening_score += 4
        screening_formula.append("+4 points : profil partiellement exploitable")
    elif actionable_profile_count >= 1:
        screening_score += 2
        screening_formula.append("+2 points : quelques éléments screening utiles")

    if len(criteres) >= 3:
        screening_score += 6
        screening_formula.append("+6 points : critères de screening présents")
    elif len(criteres) >= 1:
        screening_score += 3
        screening_formula.append("+3 points : critères partiels")

    if len(questions_entretien) >= 3:
        screening_score += 4
        screening_formula.append("+4 points : questions d’entretien utiles")
    elif len(questions_entretien) >= 1:
        screening_score += 2
        screening_formula.append("+2 points : questions d’entretien partielles")

    if len(critical_missing) >= 2:
        screening_score -= 2
        screening_formula.append("-2 points : trop d’angles morts pour sécuriser le screening")

    screening_comments.append("Mesure si le besoin aide concrètement à filtrer les CV.")
    screening_score = max(0, min(20, screening_score))

    mission_score = 0
    mission_formula = []
    mission_comments = []

    actionable_missions_count = sum(1 for m in missions if is_actionable_mission(m))
    has_accroche = not is_missing_value(fiche.get("accroche_missions", ""))
    has_intro = not is_missing_value(fiche.get("introduction_poste", ""))

    if actionable_missions_count >= 4:
        mission_score += 10
        mission_formula.append("+10 points : missions nombreuses et actionnables")
    elif actionable_missions_count >= 2:
        mission_score += 7
        mission_formula.append("+7 points : missions globalement claires")
    elif actionable_missions_count >= 1:
        mission_score += 4
        mission_formula.append("+4 points : quelques missions utiles")

    if len(missions) >= 5:
        mission_score += 4
        mission_formula.append("+4 points : volume de missions satisfaisant")
    elif len(missions) >= 3:
        mission_score += 3
        mission_formula.append("+3 points : volume correct")

    if has_accroche:
        mission_score += 2
        mission_formula.append("+2 points : accroche présente")
    if has_intro:
        mission_score += 2
        mission_formula.append("+2 points : introduction présente")

    mission_comments.append("Mesure si les missions sont concrètes et compréhensibles.")
    mission_score = max(0, min(20, mission_score))

    structure_score = 0
    structure_formula = []
    structure_comments = []

    intro_present = not is_missing_value(fiche.get("introduction_poste", ""))
    accroche_present = not is_missing_value(fiche.get("accroche_missions", ""))
    missions_present = len(missions) >= 3
    profil_present = len(profil) >= 3
    why_present = len(non_empty_list(fiche.get("pourquoi_nous_rejoindre", []))) >= 2
    env_present = len(non_empty_list(fiche.get("votre_environnement_de_travail", []))) >= 2

    if intro_present:
        structure_score += 3
        structure_formula.append("+3 points : introduction présente")
    if accroche_present:
        structure_score += 3
        structure_formula.append("+3 points : accroche missions présente")
    if missions_present:
        structure_score += 4
        structure_formula.append("+4 points : bloc missions suffisant")
    if profil_present:
        structure_score += 4
        structure_formula.append("+4 points : bloc profil suffisant")
    if why_present:
        structure_score += 3
        structure_formula.append("+3 points : rubrique Pourquoi nous rejoindre présente")
    if env_present:
        structure_score += 3
        structure_formula.append("+3 points : rubrique Environnement de travail présente")

    structure_comments.append("Mesure l’alignement avec la structure attendue d’une fiche AXA.")
    structure_score = max(0, min(20, structure_score))

    total_raw = completeness_score + precision_score + screening_score + mission_score + structure_score
    score_global = round(total_raw)

    if score_global < 45:
        niveau_maturite = tr("maturity_1", lang)
        decision = tr("clarify_before_publish", lang)
    elif score_global < 70:
        niveau_maturite = tr("maturity_2", lang)
        decision = tr("publish_with_adjustments", lang)
    elif score_global < 85:
        niveau_maturite = tr("maturity_3", lang)
        decision = tr("ready_to_publish", lang)
    else:
        niveau_maturite = tr("maturity_4", lang)
        decision = tr("ready_to_publish", lang)

    recommandations = []
    if completeness_score < 14:
        recommandations.append("Compléter les champs structurants du poste.")
    if precision_score < 14:
        recommandations.append("Réduire les formulations ambiguës et préciser les vraies informations manquantes.")
    if screening_score < 14:
        recommandations.append("Rendre le besoin plus exploitable pour le screening.")
    if mission_score < 14:
        recommandations.append("Rendre les missions plus concrètes et actionnables.")
    if structure_score < 14:
        recommandations.append("Compléter la structure de fiche AXA.")
    if not recommandations:
        recommandations.append("Le besoin est suffisamment structuré pour une utilisation RH opérationnelle.")

    return {
        "score_global": score_global,
        "details": [
            {
                "dimension": "Complétude structurante",
                "score": completeness_score,
                "sur": 20,
                "commentaire": " ".join(completeness_comments),
                "formule": completeness_formula,
                "purpose": "Vérifie si les informations de base du poste sont présentes."
            },
            {
                "dimension": "Précision du besoin",
                "score": precision_score,
                "sur": 20,
                "commentaire": " ".join(precision_comments),
                "formule": precision_formula,
                "purpose": "Vérifie si le besoin est clair et non contradictoire."
            },
            {
                "dimension": "Exploitabilité screening",
                "score": screening_score,
                "sur": 20,
                "commentaire": " ".join(screening_comments),
                "formule": screening_formula,
                "purpose": "Mesure si un recruteur peut filtrer les CV avec ce besoin."
            },
            {
                "dimension": "Clarté des missions",
                "score": mission_score,
                "sur": 20,
                "commentaire": " ".join(mission_comments),
                "formule": mission_formula,
                "purpose": "Mesure si les missions sont suffisamment explicites."
            },
            {
                "dimension": "Conformité structure AXA",
                "score": structure_score,
                "sur": 20,
                "commentaire": " ".join(structure_comments),
                "formule": structure_formula,
                "purpose": "Mesure l’alignement avec la structure attendue chez AXA."
            },
        ],
        "niveau_maturite": niveau_maturite,
        "decision": decision,
        "recommandations": recommandations,
        "source_maturity": source_maturity,
    }

def compute_qualification_confidence(result, computed_score, lang: str = "fr"):
    termes_flous = len(non_empty_list(result.get("termes_flous", [])))
    informations_manquantes = len(non_empty_list(result.get("informations_manquantes", [])))
    fiche = result.get("fiche_de_poste_axa", {})
    missions = len(non_empty_list(fiche.get("votre_role_et_vos_missions", [])))
    profil = len(non_empty_list(fiche.get("votre_profil", [])))
    criteres = len(non_empty_list(result.get("criteres_d_evaluation", [])))

    base = 82
    base -= min(20, termes_flous * 4)
    base -= min(24, informations_manquantes * 3)

    if missions >= 3:
        base += 4
    if profil >= 3:
        base += 4
    if criteres >= 2:
        base += 3
    if computed_score["score_global"] >= 80:
        base += 2
    elif computed_score["score_global"] < 50:
        base -= 5

    score = max(25, min(95, base))

    if score < 45:
        level = tr("level_faible", lang)
        comment = tr("comment_low_confidence", lang)
    elif score < 70:
        level = tr("level_moyen", lang)
        comment = tr("comment_medium_confidence", lang)
    else:
        level = tr("level_eleve", lang)
        comment = tr("comment_high_confidence", lang)

    return {"score": score, "level": level, "comment": comment}

def prioritize_risks(risques):
    mapping = {"eleve": "Bloquant", "élevé": "Bloquant", "moyen": "Important", "faible": "Amélioration"}
    grouped = {"Bloquant": [], "Important": [], "Amélioration": []}
    for r in risques:
        grouped[mapping.get((r.get("impact", "") or "").lower(), "Important")].append(r)
    return grouped

def build_quality_checklist(result, computed_score, lang: str = "fr"):
    fiche = result.get("fiche_de_poste_axa", {})
    return [
        {
            "critere": "Intitulé du poste",
            "statut": "Oui" if not is_missing_value(fiche.get("intitule_poste", "")) else "Non",
            "commentaire": "L'intitulé doit permettre de comprendre immédiatement la nature du poste."
        },
        {
            "critere": "Informations structurantes",
            "statut": "Oui" if computed_score["details"][0]["score"] >= 16 else "Partiel" if computed_score["details"][0]["score"] >= 10 else "Non",
            "commentaire": "Contrat, expérience, société, localisation et famille métier doivent être visibles."
        },
        {
            "critere": "Missions explicites",
            "statut": "Oui" if len(non_empty_list(fiche.get("votre_role_et_vos_missions", []))) >= 3 else "Partiel",
            "commentaire": "Les responsabilités principales doivent être concrètes et compréhensibles."
        },
        {
            "critere": "Profil structuré",
            "statut": "Oui" if len(non_empty_list(fiche.get("votre_profil", []))) >= 3 else "Partiel",
            "commentaire": "Le profil doit distinguer expérience, compétences et posture attendue."
        },
        {
            "critere": "Critères de screening",
            "statut": "Oui" if len(non_empty_list(result.get("criteres_d_evaluation", []))) >= 2 else "Partiel",
            "commentaire": "Le brief doit aider à filtrer les candidatures."
        },
        {
            "critere": "Risque d'ambiguïté",
            "statut": "Faible" if computed_score["details"][1]["score"] >= 16 else "Moyen" if computed_score["details"][1]["score"] >= 10 else "Élevé",
            "commentaire": "Risque de mauvaise interprétation du besoin."
        },
    ]

def build_screening_recommendations(result, lang: str = "fr"):
    fiche = result.get("fiche_de_poste_axa", {})
    recs = []

    if fiche.get("votre_role_et_vos_missions", []):
        recs.append("Vérifier dans les CV la présence d'expériences liées aux missions prioritaires.")
    if fiche.get("votre_profil", []):
        recs.append("Rechercher les compétences, la séniorité et la posture attendue.")
    if result.get("criteres_d_evaluation", []):
        recs.append("Utiliser les critères d'évaluation comme grille commune de screening.")
    if result.get("questions_entretien", []):
        recs.append("Préparer l'entretien à partir des questions proposées.")
    if result.get("informations_manquantes", []):
        recs.append("Ne pas figer trop tôt le screening si des informations critiques restent à clarifier.")
    if not recs:
        recs.append("Le besoin est suffisamment structuré pour préparer un screening cohérent.")

    return recs


def build_contextualized_justification(result, source_text: str = "", lang: str = "fr"):
    """Génère des justifications contextualisées basées sur le contenu réel du besoin."""
    termes_flous = result.get("termes_flous", [])
    informations_manquantes = result.get("informations_manquantes", [])
    fiche = result.get("fiche_de_poste_axa", {})
    
    justifications = []
    
    # Termes flous - justification métier
    if termes_flous and len(termes_flous) > 0:
        premiers_termes = termes_flous[:2]
        termes_text = []
        for t in premiers_termes:
            terme = t.get("terme", "")
            pourquoi = t.get("pourquoi_c_est_flou", "")
            if terme:
                termes_text.append(f"'{terme}' : {pourquoi[:80]}...")
        if termes_text:
            justifications.append({
                "titre": "Termes à préciser",
                "details": termes_text,
                "impact_recrutement": "Sans clarification, le screening des CV sera subjectif et poreux."
            })
    
    # Informations manquantes - justification métier
    if informations_manquantes and len(informations_manquantes) > 0:
        premiere_info = informations_manquantes[0]
        justifications.append({
            "titre": f"Info manquante : {premiere_info[:40]}...",
            "details": [f"Cette information est indispensable pour {premiere_info.lower()}"],
            "impact_recrutement": "Impossible de qualifier les candidats sans cette information."
            if any(x in premiere_info.lower() for x in ["expéri", "compéten", "contrat", "local"]) 
            else "Risque de malentendu avec le manager."
        })
    
    # Contrat manquant
    if is_missing_value(fiche.get("type_contrat", "")):
        justifications.append({
            "titre": "Type de contrat",
            "details": ["CDI, CDD, ou Interim non précisés"],
            "impact_recrutement": " Les candidats postulent sans knowing les conditions. Dépenses inutiles."
        })
    
    # Expérience
    if is_missing_value(fiche.get("niveau_experience", "")):
        justifications.append({
            "titre": "Niveau d'expérience",
            "details": ["Senior, Confirmé, Junior non précisés"],
            "impact_recrutement": " On ne peut pas filter les CV efficacement."
        })
    
    return justifications if justifications else None