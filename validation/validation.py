from typing import Any, Dict, List


STRICT_INVALID_MESSAGE = "⚠️ Veuillez préciser un besoin métier réel."


def normalize_text(value: str) -> str:
    return (value or "").strip().lower()


def non_empty_list(value) -> List[Any]:
    if not isinstance(value, list):
        return []
    return [item for item in value if item not in [None, "", [], {}]]


def is_missing_value(value: str) -> bool:
    normalized = normalize_text(value)
    return normalized in {
        "",
        "non précisé",
        "non precise",
        "non renseigné",
        "non renseigne",
        "n/a",
        "na",
        "aucun",
        "aucune",
        "non disponible",
        "à préciser",
        "a preciser",
        "—",
        "-",
    }


def is_actionable_mission(text: str) -> bool:
    value = normalize_text(text)

    if is_missing_value(value) or len(value) < 12:
        return False

    action_verbs = [
        "piloter", "gérer", "gerer", "animer", "définir", "definir",
        "concevoir", "développer", "developper", "mettre en œuvre",
        "mettre en oeuvre", "coordonner", "suivre", "organiser",
        "construire", "déployer", "deployer", "assurer", "produire",
        "analyser", "accompagner", "implémenter", "implementer",
        "manager", "contribuer", "superviser",
    ]

    return any(verb in value for verb in action_verbs)


def is_actionable_profile_item(text: str) -> bool:
    value = normalize_text(text)

    if is_missing_value(value) or len(value) < 8:
        return False

    useful_markers = [
        "expérience", "experience", "maîtrise", "maitrise", "connaissance",
        "compétence", "competence", "capacité", "capacite", "maîtriser",
        "maitriser", "python", "sql", "cloud", "power bi", "gestion de projet",
        "anglais", "communication", "analyse", "gouvernance", "data",
        "finance", "banque", "conformité", "conformite",
    ]

    return any(marker in value for marker in useful_markers)


def detect_source_maturity(source_text: str) -> str:
    text = normalize_text(source_text)

    if len(text) > 1200:
        return "fiche_detaillee"

    detailed_markers = [
        "type de contrat",
        "niveau d'expérience",
        "niveau d’experience",
        "localisation",
        "votre rôle",
        "votre role",
        "votre profil",
        "missions",
        "compétences",
        "competences",
    ]

    medium_markers = [
        "cdi", "cdd", "senior", "junior", "sql", "cloud", "manager",
        "projet", "équipe", "equipe", "expérience", "experience",
    ]

    detailed_count = sum(1 for marker in detailed_markers if marker in text)
    medium_count = sum(1 for marker in medium_markers if marker in text)

    if detailed_count >= 3:
        return "fiche_detaillee"
    if medium_count >= 3:
        return "brief_structuré"
    return "besoin_brut"


def validate_recruitment_input(text: str) -> Dict[str, Any]:
    normalized = normalize_text(text)

    if len(normalized) < 20:
        return {
            "valid": False,
            "reason": STRICT_INVALID_MESSAGE,
        }

    invalid_patterns = [
        "quel temps",
        "météo",
        "meteo",
        "poème",
        "poeme",
        "je veux être heureux",
        "je veux etre heureux",
        "raconte moi une histoire",
        "blague",
        "recette",
    ]

    if any(pattern in normalized for pattern in invalid_patterns):
        return {
            "valid": False,
            "reason": STRICT_INVALID_MESSAGE,
        }

    recruitment_markers = [
        "poste", "recrut", "candidat", "profil", "mission", "compétence",
        "competence", "expérience", "experience", "cdi", "cdd", "manager",
        "équipe", "equipe", "sql", "python", "cloud", "data", "banque",
        "finance", "conformité", "conformite", "projet",
    ]

    has_marker = any(marker in normalized for marker in recruitment_markers)

    if not has_marker and len(normalized.split()) < 6:
        return {
            "valid": False,
            "reason": STRICT_INVALID_MESSAGE,
        }

    return {
        "valid": True,
        "reason": "Besoin exploitable",
    }


def build_display_result(result: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(result, dict):
        return {}

    fiche = result.get("fiche_de_poste_axa", {}) or {}

    display_result = dict(result)
    display_result["fiche_de_poste_axa"] = {
        "reference_offre": fiche.get("reference_offre", "Non précisé"),
        "intitule_poste": fiche.get("intitule_poste", "Non précisé"),
        "type_contrat": fiche.get("type_contrat", "Non précisé"),
        "niveau_experience": fiche.get("niveau_experience", "Non précisé"),
        "societe_du_groupe": fiche.get("societe_du_groupe", "Non précisé"),
        "famille_metier": fiche.get("famille_metier", "Non précisé"),
        "sous_famille_metier": fiche.get("sous_famille_metier", "Non précisé"),
        "localisation": fiche.get("localisation", "Non précisé"),
        "introduction_poste": fiche.get("introduction_poste", "Non précisé"),
        "accroche_missions": fiche.get("accroche_missions", "Non précisé"),
        "votre_role_et_vos_missions": non_empty_list(fiche.get("votre_role_et_vos_missions", [])),
        "votre_profil": non_empty_list(fiche.get("votre_profil", [])),
        "pourquoi_nous_rejoindre": non_empty_list(fiche.get("pourquoi_nous_rejoindre", [])),
        "votre_environnement_de_travail": non_empty_list(fiche.get("votre_environnement_de_travail", [])),
    }

    display_result["resume_besoin"] = result.get("resume_besoin", "Non précisé")
    display_result["termes_flous"] = non_empty_list(result.get("termes_flous", []))
    display_result["informations_manquantes"] = non_empty_list(result.get("informations_manquantes", []))
    display_result["questions_de_clarification"] = non_empty_list(result.get("questions_de_clarification", []))
    display_result["risques_detectes"] = non_empty_list(result.get("risques_detectes", []))
    display_result["criteres_d_evaluation"] = non_empty_list(result.get("criteres_d_evaluation", []))
    display_result["questions_entretien"] = non_empty_list(result.get("questions_entretien", []))
    display_result["diagnostic_llm"] = result.get("diagnostic_llm", {})

    return display_result