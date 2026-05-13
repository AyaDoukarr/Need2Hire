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
        completeness_formula.append(tr("formula_missing_structuring", lang))
    else:
        completeness_formula.append(tr("formula_structuring_present", lang))

    if len(present_core) >= 5 and len(missions) >= 3 and len(profil) >= 3:
        completeness_score += 2
        completeness_formula.append(tr("formula_structure_detailed", lang))

    completeness_comments.append("Mesure si la base du besoin est assez complète pour lancer un recrutement.")
    completeness_score = max(0, min(20, completeness_score))

    precision_score = 20
    precision_formula = []
    precision_comments = []

    if len(termes_flous) == 0:
        precision_formula.append(tr("formula_clear_need", lang))

    elif len(termes_flous) <= 2:
        precision_score -= 2
        termes_exemples = ", ".join([str(t.get("terme", "")) for t in termes_flous[:2]])
        precision_formula.append(
            tr("formula_terms_to_clarify", lang).format(terms=termes_exemples)
        )

    elif len(termes_flous) <= 4:
        precision_score -= 5
        termes_exemples = ", ".join([str(t.get("terme", "")) for t in termes_flous[:3]])
        precision_formula.append(
            tr("formula_terms_to_clarify", lang).format(terms=termes_exemples)
        )

    else:
        precision_score -= 8
        termes_exemples = ", ".join([str(t.get("terme", "")) for t in termes_flous[:4]])
        precision_formula.append(
            tr("formula_many_terms", lang).format(terms=termes_exemples)
        )
        if len(critical_missing) == 0:
            precision_formula.append(tr("formula_all_critical_present", lang))
        elif len(critical_missing) == 1:
            precision_score -= 3
            precision_formula.append(tr("formula_one_critical_missing", lang))
        elif len(critical_missing) == 2:
            precision_score -= 5
            precision_formula.append(tr("formula_two_critical_missing", lang))
        else:
            precision_score -= 7
            precision_formula.append(
                tr("formula_critical_missing", lang).format(
                    items=", ".join(critical_missing[:3])
                )
            )

    if len(secondary_missing) > 0:
        penalty = min(3, len(secondary_missing))
        precision_score -= penalty
        precision_formula.append(
            tr("formula_secondary_missing", lang).format(
                items=", ".join(secondary_missing[:3])
            )
        )


    if source_maturity == "fiche_detaillee":
        precision_score += 2
        precision_formula.append(tr("formula_source_structured", lang))


    precision_comments.append(tr("comment_precision", lang))
    precision_score = max(0, min(20, precision_score))
    screening_score = 0
    screening_formula = []
    screening_comments = []

    actionable_profile_count = sum(1 for p in profil if is_actionable_profile_item(p))

    if len(profil) >= 4 and actionable_profile_count >= 3:
        screening_score += 6
        screening_formula.append(tr("formula_profile_detailed", lang))
    elif len(profil) >= 2 and actionable_profile_count >= 2:
        screening_score += 4
        screening_formula.append(tr("formula_profile_partial", lang))
    elif actionable_profile_count >= 1:
        screening_score += 2
        screening_formula.append(tr("formula_screening_elements", lang))

    if len(criteres) >= 3:
        screening_score += 6
        screening_formula.append(tr("formula_screening_criteria", lang))
    elif len(criteres) >= 1:
        screening_score += 3
        screening_formula.append(tr("formula_partial_criteria", lang))

    if len(questions_entretien) >= 3:
        screening_score += 4
        screening_formula.append(tr("formula_interview_questions", lang))
    elif len(questions_entretien) >= 1:
        screening_score += 2
        screening_formula.append(tr("formula_partial_questions", lang))

    if len(critical_missing) >= 2:
        screening_score -= 2
        screening_formula.append(tr("formula_screening_uncertainty", lang))
    screening_comments.append(tr("comment_screening", lang))
    screening_score = max(0, min(20, screening_score))

    mission_score = 0
    mission_formula = []
    mission_comments = []

    actionable_missions_count = sum(1 for m in missions if is_actionable_mission(m))
    has_accroche = not is_missing_value(fiche.get("accroche_missions", ""))
    has_intro = not is_missing_value(fiche.get("introduction_poste", ""))

    if actionable_missions_count >= 4:
        mission_score += 10
        mission_formula.append(tr("formula_many_actionable_missions", lang))
    elif actionable_missions_count >= 2:
        mission_score += 7
        mission_formula.append(tr("formula_clear_missions", lang))
    elif actionable_missions_count >= 1:
        mission_score += 4
        mission_formula.append(tr("formula_some_useful_missions", lang))

    if len(missions) >= 5:
        mission_score += 4
        mission_formula.append(tr("formula_mission_volume_good", lang))
    elif len(missions) >= 3:
        mission_score += 3
        mission_formula.append(tr("formula_mission_volume_ok", lang))

    if has_accroche:
        mission_score += 2
        mission_formula.append(tr("formula_mission_hook_present", lang))
    if has_intro:
        mission_score += 2
        mission_formula.append(tr("formula_intro_present", lang))

    mission_comments.append(tr("comment_missions", lang))
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
        structure_formula.append(tr("formula_intro_present", lang))
    if accroche_present:
        structure_score += 3
        structure_formula.append(tr("formula_mission_hook_present", lang))
    if missions_present:
        structure_score += 4
        structure_formula.append(tr("formula_mission_block_detailed", lang))
    if profil_present:
        structure_score += 4
        structure_formula.append(tr("formula_profile_block_detailed", lang))
    if why_present:
        structure_score += 3
        structure_formula.append(tr("formula_why_join_present", lang))
    if env_present:
        structure_score += 3
        structure_formula.append(tr("formula_work_env_present", lang))

    structure_comments.append(tr("comment_structure", lang))
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
        recommandations.append(tr("reco_complete_fields", lang))
    if precision_score < 14:
        recommandations.append(tr("reco_reduce_ambiguity", lang))
    if screening_score < 14:
        recommandations.append(tr("reco_screening", lang))
    if mission_score < 14:
        recommandations.append(tr("reco_missions", lang))
    if structure_score < 14:
        recommandations.append(tr("reco_structure", lang))
    if not recommandations:
        recommandations.append(tr("reco_good_quality", lang))

    return {
        "score_global": score_global,
        "details": [
            {
                "dimension": tr("dimension_completeness", lang),
                "score": completeness_score,
                "sur": 20,
                "commentaire": tr("comment_completeness", lang),
                "formule": completeness_formula,
                "purpose": tr("purpose_completeness", lang)
            },
            {
                "dimension": tr("dimension_precision", lang),
                "score": precision_score,
                "sur": 20,
                "commentaire": tr("comment_precision", lang),
                "formule": precision_formula,
                "purpose": tr("purpose_precision", lang)
            },
            {
                "dimension": tr("dimension_screening", lang),
                "score": screening_score,
                "sur": 20,
                "commentaire": tr("comment_screening", lang),
                "formule": screening_formula,
                "purpose": tr("purpose_screening", lang)
            },
            {
                "dimension": tr("dimension_missions", lang),
                "score": mission_score,
                "sur": 20,
                "commentaire": tr("comment_missions", lang),
                "formule": mission_formula,
                "purpose": tr("purpose_missions", lang)
            },
            {
                "dimension": tr("dimension_structure", lang),
                "score": structure_score,
                "sur": 20,
                "commentaire": tr("comment_structure", lang),
                "formule": structure_formula,
                "purpose": tr("purpose_structure", lang)
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
            "critere": tr("checklist_job_title", lang),
            "statut": tr("checklist_oui", lang) if not is_missing_value(fiche.get("intitule_poste", "")) else tr("checklist_non", lang),
            "commentaire": tr("checklist_title_comment", lang),
        },
        {
            "critere": tr("checklist_structuring_info", lang),
            "statut": tr("checklist_oui", lang) if computed_score["details"][0]["score"] >= 16 else tr("checklist_partiel", lang) if computed_score["details"][0]["score"] >= 10 else tr("checklist_non", lang),
            "commentaire": tr("checklist_structuring_comment", lang),
        },
        {
            "critere": tr("checklist_missions", lang),
            "statut": tr("checklist_oui", lang) if len(non_empty_list(fiche.get("votre_role_et_vos_missions", []))) >= 3 else tr("checklist_partiel", lang),
            "commentaire": tr("checklist_missions_comment", lang),
        },
        {
            "critere": tr("checklist_profile", lang),
            "statut": tr("checklist_oui", lang) if len(non_empty_list(fiche.get("votre_profil", []))) >= 3 else tr("checklist_partiel", lang),
            "commentaire": tr("checklist_profile_comment", lang),
        },
        {
            "critere": tr("checklist_criteria", lang),
            "statut": tr("checklist_oui", lang) if len(non_empty_list(result.get("criteres_d_evaluation", []))) >= 2 else tr("checklist_partiel", lang),
            "commentaire": tr("checklist_criteria_comment", lang),
        },
        {
            "critere": tr("checklist_ambiguity", lang),
            "statut": tr("checklist_faible", lang) if computed_score["details"][1]["score"] >= 16 else tr("checklist_moyen", lang) if computed_score["details"][1]["score"] >= 10 else tr("checklist_eleve", lang),
            "commentaire": tr("checklist_ambiguity_comment", lang),
        },
]

def build_screening_recommendations(result, lang: str = "fr"):
    fiche = result.get("fiche_de_poste_axa", {})
    recs = []

    if fiche.get("votre_role_et_vos_missions", []):
        recs.append(tr("screen_reco_missions", lang))
    if fiche.get("votre_profil", []):
        recs.append(tr("screen_reco_profile", lang))
    if result.get("criteres_d_evaluation", []):
        recs.append(tr("screen_reco_criteria", lang))
    if result.get("questions_entretien", []):
        recs.append(tr("screen_reco_questions", lang))
    if result.get("informations_manquantes", []):
        recs.append(tr("screen_reco_missing", lang))
    if not recs:
        recs.append(tr("screen_reco_good", lang))

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