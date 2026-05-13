import os
import re
from auth import render_login,render_logout,image_to_base64
from pathlib import Path
from auth import render_login, render_logout
import streamlit as st
import json
from styles import AXA_STYLES, FLIP_CARD_STYLE
from i18n import tr, get_output_language_name
from services.llm_service import call_llm_json
from config import STRICT_INVALID_MESSAGE
from data.data_layer import TAXONOMY_ROWS, REFERENCE_ROWS
from orchestration.pipeline import run_pipeline
from validation.validation import validate_recruitment_input, build_display_result
from domain.scoring import prioritize_risks
from ui.reporting import generate_qualification_report_markdown
from ui.ui_components import (
    render_analysis_block,
    render_invalid_input_block,
    render_premium_sidebar,
    render_rh_analysis_page,
)
from services.audio_service import transcribe_audio_file, save_uploaded_audio_to_temp
from styles import DARK_MODE_STYLE

#st.markdown(DARK_MODE_STYLE, unsafe_allow_html=True)




def init_agent1_state():
    defaults = {
        "agent1_conversation": [],
        "agent1_result": None,
        "agent1_display_result": None,
        "agent1_score": None,
        "agent1_confidence": None,
        "agent1_job_family": "Générique",
        "agent1_job_subfamily": "Non précisé",
        "agent1_language": "fr",
        "agent1_invalid_input": False,
        "agent1_result_language": None,
        "agent1_pipeline_output": None,
        # Tracking initial missing info for step 2 filtering
        "agent1_initial_missing": [],
        "agent1_initial_questions": [],
        "agent1_initial_termes_flous": [],
        "agent1_initial_score": None,
        "agent1_current_page": "dashboard",
        "main_section": "dashboard",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_agent1():
    for k in [
        "agent1_conversation",
        "agent1_result",
        "agent1_display_result",
        "agent1_score",
        "agent1_confidence",
        "agent1_pipeline_output",
    ]:
        st.session_state[k] = [] if k == "agent1_conversation" else None

    st.session_state.agent1_job_family = "Générique"
    st.session_state.agent1_job_subfamily = "Non précisé"
    st.session_state.agent1_invalid_input = False
    st.session_state.agent1_result_language = None
    st.session_state.agent1_initial_missing = []
    st.session_state.agent1_initial_questions = []
    st.session_state.agent1_initial_termes_flous = []
    st.session_state.agent1_initial_score = None
    st.session_state.agent1_ignored_items = []
    st.session_state.rh_active_input = None
    st.session_state.agent1_completed_items = []
    st.session_state.agent1_total_rh_items = 0


def build_consolidated_text():
    blocks = []
    followup_count = 1

    for item in st.session_state.agent1_conversation:
        if item["type"] == "initial":
            blocks.append(f"Besoin initial du manager :\n{item['content']}")
        elif item["type"] == "followup":
            blocks.append(f"Précision complémentaire {followup_count} :\n{item['content']}")
            followup_count += 1

    return "\n\n".join(blocks).strip()
def translate_generated_content(content, target_language):
    if content is None:
        return None

    target = {
        "fr": "French",
        "en": "English",
        "es": "Spanish",
    }.get(target_language, "French")

    prompt = f"""
You are a professional HR translator.

Translate ALL textual VALUES in the provided JSON to {target}.

STRICT RULES:
- Keep exactly the same JSON structure.
- Never translate JSON keys.
- Translate every user-facing sentence, bullet, risk, question, recommendation, profile item and job description field.
- Keep proper nouns, company names, technologies and acronyms unchanged: AXA, SQL, Python, Power BI, Tableau, CDI, Data, IA, IT.
- Return only valid JSON.
"""

    payload = json.dumps({"content": content}, ensure_ascii=False)

    translated = call_llm_json(prompt, payload, temperature=0)

    if isinstance(translated, dict) and "content" in translated:
        return translated["content"]

    return content
def reject_invalid_need(error_message=None):
    st.session_state.agent1_result = None
    st.session_state.agent1_display_result = None
    st.session_state.agent1_score = None
    st.session_state.agent1_confidence = None
    st.session_state.agent1_invalid_input = True
    st.session_state.agent1_result_language = None

    if st.session_state.agent1_pipeline_output is None:
        st.session_state.agent1_pipeline_output = {}

    if error_message:
        st.session_state.agent1_pipeline_output["error"] = error_message


def normalize_simple(text: str) -> str:
    return (text or "").strip().lower()

def clean_missing_info(missing_list, consolidated_text, result=None, job_family="", job_subfamily=""):

    text = normalize_simple(consolidated_text)
    fiche = (result or {}).get("fiche_de_poste_axa", {}) if isinstance(result, dict) else {}

    fiche_text = normalize_simple(
        " ".join([
            str(fiche.get("intitule_poste", "")),
            str(fiche.get("type_contrat", "")),
            str(fiche.get("niveau_experience", "")),
            str(fiche.get("localisation", "")),
            " ".join(fiche.get("votre_role_et_vos_missions", []) or []),
            " ".join(fiche.get("votre_profil", []) or []),
            " ".join(fiche.get("votre_environnement_de_travail", []) or []),
        ])
    )

    full_text = f"{text} {fiche_text}"

    internal_fields = [
        "société du groupe", "societe du groupe",
        "intitulé du poste", "intitule du poste",
        "famille métier", "famille metier",
        "sous-famille métier", "sous-famille metier",
        "mots-clés", "mots cles",
        "référence interne", "reference interne",
        "reference offre",
        "job family",
    ]

    useless_patterns = [
        "communication", "soft skills", "rigueur", "autonomie",
        "leadership", "esprit d'équipe", "adaptabilité", "vulgarisation"
    ]

    def has_any(keywords):
        return any(k in full_text for k in keywords)

    has_job_title = has_any([
        "chef de projet", "business analyst", "data analyst", "data engineer",
        "consultant", "développeur", "developpeur", "manager", "product owner",
        "scrum master", "architecte", "ingénieur", "ingenieur"
    ])

    has_experience = bool(
        re.search(r"\b\d+\s*(an|ans|année|années|years?)\b", full_text)
        or "d'expérience" in full_text
        or "d’experience" in full_text
        or "d’expérience" in full_text
        or has_any(["junior", "confirmé", "confirme", "senior", "expert"])
    )

    has_contract = has_any(["cdi", "cdd", "freelance", "stage", "alternance", "intérim", "interim"])
    has_location = has_any(["paris", "nanterre", "lyon", "marseille", "lille", "toulouse","remote", "hybride", "télétravail", "teletravail", "présentiel", "presentiel"
    ])
    has_technical_skills = has_any([
        "sql", "python", "power bi", "tableau", "excel", "spark", "scala",
        "azure", "aws", "gcp", "databricks", "snowflake"
    ])
    has_salary = has_any([
    "€", "k€", "ke", "salaire", "rémunération", "remuneration", "package",
    "fourchette"])
    has_remote = has_any(["télétravail", "teletravail", "remote", "hybride", "présentiel", "presentiel"])
    has_team_context = has_any([
    "équipe", "équipes", "equipe", "equipes",
    "collaborerez", "collaboration",
    "équipes it", "equipes it",
    "métiers", "metiers",
    "décideurs", "decideurs",
    "rattaché", "rattache", "manager", "squad", "tribu"
    ])   

    has_project_context = has_any([
    "transformation data", "cadre de notre transformation", "transformation",
    "pilotage par la donnée", "pilotage par la donnee",
    "automatiser les insights", "prise de décision", "prise de decision",
    "migration", "déploiement", "deploiement", "refonte", "implémentation",
    "implementation", "reporting financier", "data lake", "crm", "erp"
    ])

    generated_missing = []

    if not has_job_title:
        generated_missing.append("Intitulé du poste ou rôle cible précis")

    if not has_experience:
        generated_missing.append("Niveau d’expérience attendu")

    if not has_contract:
        generated_missing.append("Type de contrat")

    if not has_location:
        generated_missing.append("Localisation ou rythme de présence")

    if not has_project_context:
        generated_missing.append("Contexte et périmètre concret du projet")

    if not has_technical_skills:
        generated_missing.append("Compétences ou outils attendus")

    if not has_team_context:
        generated_missing.append("Taille, rattachement ou organisation de l’équipe")

    if not has_salary:
        generated_missing.append("Fourchette de rémunération")

    if not has_remote:
        generated_missing.append("Modalités de télétravail ou présence sur site")

    cleaned = []
    seen = set()

    # 1. Nettoyer les infos remontées par le LLM
    for item in missing_list or []:
        item_text = str(item).strip()
        item_norm = normalize_simple(item_text)

        if not item_norm or item_norm in seen:
            continue

        if re.search(r"\([^)]{3,}\)", item_text):
            continue

        if any(field in item_norm for field in internal_fields):
            continue

        if any(p in item_norm for p in useless_patterns):
            continue

        # Ne pas afficher un manque si l'info est déjà détectée dans la JD
        if has_experience and any(k in item_norm for k in [
            "expérience", "experience", "seniorité", "seniorite", "niveau"
        ]):
            continue

        if has_team_context and any(k in item_norm for k in [
            "équipe", "equipe", "rattachement", "organisation"
        ]):
            continue

        if has_project_context and any(k in item_norm for k in [
            "contexte", "projet", "périmètre", "perimetre"
        ]):
            continue

        if has_technical_skills and any(k in item_norm for k in [
            "compétence", "competence", "outil", "stack", "technologie"
        ]):
            continue

        seen.add(item_norm)
        cleaned.append(item_text)

        # 2. Ajouter les manques déterministes détectés par le code
    for item in generated_missing:
        item_norm = normalize_simple(item)
        if item_norm not in seen:
            seen.add(item_norm)
            cleaned.append(item)

    # 3. Déduplication sémantique
    semantic_groups = {
        "localisation": [
            "localisation",
            "perimetre geographique",
            "périmètre géographique",
            "rythme de presence",
            "rythme de présence",
            "teletravail",
            "télétravail",
            "presence sur site",
            "présence sur site",
            "hybride",
            "remote",
        ],
        "contrat": [
            "contrat",
            "cdi",
            "cdd",
            "freelance",
            "interim",
            "intérim",
        ],
        "experience": [
            "experience",
            "expérience",
            "seniorite",
            "séniorité",
            "annees",
            "années",
            "niveau",
        ],
        "equipe": [
            "taille",
            "rattachement",
            "organisation de l’équipe",
            "organisation de l'equipe",
            "équipe",
            "equipe",
        ],
        "projet": [
            "contexte",
            "périmètre concret",
            "perimetre concret",
            "projet",
        ],
        "competences": [
            "compétences",
            "competences",
            "outils",
            "stack",
            "technologies",
        ],
        "salaire": [
            "salaire",
            "rémunération",
            "remuneration",
            "fourchette",
            "package",
        ],
    }

    canonical_labels = {
        "localisation": "Localisation et modalités de travail",
        "contrat": "Type de contrat attendu",
        "experience": "Niveau d’expérience attendu",
        "equipe": "Taille, rattachement ou organisation de l’équipe",
        "projet": "Contexte et périmètre concret du projet",
        "competences": "Compétences ou outils attendus",
        "salaire": "Fourchette de rémunération",
    }

    final_cleaned = []
    already_grouped = set()

    for item in cleaned:
        item_norm = normalize_simple(item)
        matched_group = None

        for group_name, keywords in semantic_groups.items():
            if any(k in item_norm for k in keywords):
                matched_group = group_name
                break

        if matched_group:
            if matched_group in already_grouped:
                continue

            already_grouped.add(matched_group)
            final_cleaned.append(canonical_labels.get(matched_group, item))
        else:
            final_cleaned.append(item)

    return final_cleaned[:5]

def clean_clarification_questions(questions, consolidated_text, result=None):
    text = normalize_simple(consolidated_text)
    fiche = (result or {}).get("fiche_de_poste_axa", {}) if isinstance(result, dict) else {}

    fiche_text = normalize_simple(
        " ".join([
            str(fiche.get("intitule_poste", "")),
            str(fiche.get("type_contrat", "")),
            str(fiche.get("niveau_experience", "")),
            str(fiche.get("localisation", "")),
            " ".join(fiche.get("votre_role_et_vos_missions", []) or []),
            " ".join(fiche.get("votre_profil", []) or []),
        ])
    )

    full_text = f"{text} {fiche_text}"

    blocked_patterns = [
        "minimum ou un maximum",
        "minimum ou maximum",
        "niveau d'expérience précis",
        "niveau d'experience precis",
        "quel est le niveau d'expérience précis",
        "quel niveau d'expérience",
        "senior signifie",
        "5 ans minimum",
        "3 ans minimum",
        "niveau sql",
        "niveau attendu en sql",
        "niveau attendu en azure",
        "niveau attendu en spark",
        "niveau attendu en databricks",
    ]

    has_experience = any(x in full_text for x in [
        "junior", "confirmé", "confirme", "senior", "expert",
        "1 an", "2 ans", "3 ans", "4 ans", "5 ans", "6 ans",
        "7 ans", "8 ans", "9 ans", "10 ans",
    ])

    has_technical_stack = any(x in full_text for x in [
        "sql", "python", "spark", "pyspark", "azure", "databricks",
        "snowflake", "tableau", "power bi", "java", "react",
    ])

    cleaned = []
    seen = set()

    for q in questions or []:
        q_text = str(q).strip()
        q_norm = normalize_simple(q_text)

        if not q_norm or q_norm in seen:
            continue

        if any(p in q_norm for p in blocked_patterns):
            continue

        if has_experience and any(x in q_norm for x in [
            "expérience", "experience", "senior", "junior", "confirmé", "confirme"
        ]):
            continue

        if has_technical_stack and any(x in q_norm for x in [
            "niveau", "maîtrise", "maitrise", "compétence technique",
            "competence technique", "sql", "azure", "spark", "databricks"
        ]):
            continue
        if "localisation" in q_norm and any(x in full_text for x in [
     "remote", "hybride", "télétravail", "teletravail", "présentiel", "presentiel"
        ]):
            continue

        if "type de contrat" in q_norm and any(x in full_text for x in [
         "cdi", "cdd", "freelance", "stage", "alternance", "intérim", "interim"
        ]):
            continue

        if "société du groupe axa" in q_norm or "societe du groupe axa" in q_norm:
            continue
        seen.add(q_norm)
        cleaned.append(q_text)

    return cleaned[:3]

def run_qualification_analysis(lang):
    consolidated_text = build_consolidated_text()
    # Validation désactivée ici : les JD avec titres/tirets doivent passer.
    pipeline_output = None
    raw_result = None
    display_result = None
    computed_score = None
    confidence = None

    with st.spinner(tr("analysis_running", lang)):
       
        pipeline_output = run_pipeline(
            user_input=consolidated_text,
            lang=lang,
        )

        st.session_state.agent1_pipeline_output = pipeline_output

        if pipeline_output.get("status") != "success":
            reject_invalid_need(pipeline_output.get("error", STRICT_INVALID_MESSAGE))
            return

        raw_result = pipeline_output["result"]
        if lang != "fr":
            try:
                raw_result = translate_generated_content(raw_result, lang)
                pipeline_output["result"] = raw_result
                st.session_state.agent1_pipeline_output = pipeline_output
            except Exception as e:
                st.warning("Traduction partielle indisponible pour le moment. Réessayez dans quelques secondes.")
            pipeline_output["result"] = raw_result
            st.session_state.agent1_pipeline_output = pipeline_output
        print("\n===== RAW RESULT =====")
        print(json.dumps(raw_result, indent=2, ensure_ascii=False))
        print("======================\n")
        raw_result["informations_manquantes"] = clean_missing_info(
            raw_result.get("informations_manquantes", []),
            consolidated_text,
            result=raw_result,
            job_family=pipeline_output.get("family", ""),
            job_subfamily=pipeline_output.get("subfamily", ""),
        )
        ignored_missing = {
            x.replace("missing::", "").strip().lower()
            for x in st.session_state.get("agent1_ignored_items", [])
            if str(x).startswith("missing::")
        }

        raw_result["informations_manquantes"] = [
            info for info in raw_result.get("informations_manquantes", [])
            if str(info).strip().lower() not in ignored_missing
        ]
        # Ajouter automatiquement une question sur l'experience si manquante
        from validation.validation import detect_experience_in_text
        fiche = raw_result.get("fiche_de_poste_axa", {})
        fiche_exp = (fiche.get("niveau_experience") or "").strip().lower()
        source_exp = detect_experience_in_text(consolidated_text)
        
        # Verifier si lvl manquant (vide, placeholder, ou non detecte)
        exp_is_missing = not fiche_exp or fiche_exp in ["", "non precise", "non спе注明", "non renseigne", "nan", "na", "n/a"]
        exp_not_detected = not source_exp.get("detected", False)
        
        # Ajouter info manquante + question si experience non trouvee
        if exp_is_missing and exp_not_detected:
            raw_result.setdefault("questions_de_clarification", [])
            q_list = [q.lower() for q in raw_result.get("questions_de_clarification", [])]
            if "experience" not in " ".join(q_list):
                raw_result["questions_de_clarification"].append("Quel niveau d'experience est attendu (junior, confirme, senior, X annees) ?")
            
            raw_result.setdefault("informations_manquantes", [])
            i_list = [i.lower() for i in raw_result.get("informations_manquantes", [])]
            if "experience" not in " ".join(i_list):
                raw_result["informations_manquantes"].append("Niveau d'experience attendu non precise")

        raw_result["questions_de_clarification"] = clean_clarification_questions(
        raw_result.get("questions_de_clarification", []),
        consolidated_text,
        result=raw_result,
    )
        display_result = build_display_result(raw_result)
        computed_score = pipeline_output["score"]
        confidence = pipeline_output["confidence"]
    if lang != "fr":
        computed_score = translate_generated_content(computed_score, lang)
        confidence = translate_generated_content(confidence, lang)
    if raw_result is None or display_result is None:
        reject_invalid_need("Erreur pendant l’analyse. Veuillez réessayer.")
        return

    st.session_state.agent1_invalid_input = False
    st.session_state.agent1_result = raw_result
    st.session_state.agent1_display_result = display_result
    
    # === FILTRAGE INFOS MANQUANTES ÉTAPE 2 ===
    # Stocker les initiaux à l'étape 1, filtrer aux étapes suivantes
    if not st.session_state.get("agent1_initial_missing"):
        # Étape 1: stocker les initiaux
        st.session_state.agent1_initial_missing = raw_result.get("informations_manquantes", [])[:]
        st.session_state.agent1_initial_questions = raw_result.get("questions_de_clarification", [])[:]
        st.session_state.agent1_initial_termes_flous = raw_result.get("termes_flous", [])[:]
        st.session_state.agent1_initial_score = computed_score
    else:
        # Étape 2+: ne garder que les initiaux - résolus
        initial_missing = st.session_state.get("agent1_initial_missing", [])
        current_missing = raw_result.get("informations_manquantes", [])

        # IMPORTANT :
        # Après l'étape 1, on interdit les nouveaux manques générés par le LLM.
        # On ne garde que les manques déjà présents au départ.
        current_missing_allowed = [
            m for m in current_missing
            if normalize_simple(m) in [normalize_simple(x) for x in initial_missing]
        ]
        initial_questions = st.session_state.get("agent1_initial_questions", [])
        
        # Récupérer les réponses follow-up
        followup_texts = []
        for item in st.session_state.get("agent1_conversation", []):
            if item.get("type") == "followup":
                followup_texts.append(item.get("content", "").lower())
        followup_combined = " ".join(followup_texts)
        
        # Filtrer les infos manquantes: garder seulement les initiaux non résolus
        resolved_keywords = [
            "projet", "transformation", "migration", "implementation", "deploiement",
            "azure", "aws", "gcp", "google", "cloud",
            "sql", "python", "scala", "spark", "tableau", "power bi", "java", "docker",
            "junior", "senior", "confirme", "expert", "an", "annees",
            "paris", "lyon", "nanterre", "remote", "teletravail", "hybrid",
            "cdi", "cdd", "interim", "freelance",
            "equipe", "team", "contexte", "collaborateurs",
            "ia", "analytics", "machine learning", "ml", "bi"
        ]
        
        filtered_missing = []

        for info in current_missing_allowed:
            info_lower = normalize_simple(info)

            resolved = False

            for followup in followup_texts:
                followup_norm = normalize_simple(followup)

                if any(k in info_lower for k in ["contrat", "cdi", "cdd", "freelance", "stage", "alternance"]):
                    resolved = any(k in followup_norm for k in ["cdi", "cdd", "freelance", "stage", "alternance", "intérim", "interim"])

                elif any(k in info_lower for k in ["localisation", "télétravail", "teletravail", "présence", "presence", "modalités"]):
                    resolved = any(k in followup_norm for k in ["paris", "nanterre", "lyon", "remote", "hybride", "télétravail", "teletravail", "présentiel", "presentiel"])

                elif any(k in info_lower for k in ["rémunération", "remuneration", "salaire", "fourchette", "package"]):
                    resolved = any(k in followup_norm for k in ["€", "k€", "ke", "salaire", "rémunération", "remuneration", "package", "fourchette"])

                elif any(k in info_lower for k in ["expérience", "experience", "seniorité", "seniorite"]):
                    resolved = any(k in followup_norm for k in ["junior", "confirmé", "confirme", "senior", "expert", "an", "ans"])

            if not resolved:
                filtered_missing.append(info)

        raw_result["informations_manquantes"] = filtered_missing
        
        # Filtrer les questions aussi
        filtered_questions = []
        for q in initial_questions:
            q_lower = q.lower()
            resolved = any(k in followup_combined for k in resolved_keywords if k in q_lower)
            if not resolved:
                filtered_questions.append(q)
        
        raw_result["questions_de_clarification"] = filtered_questions
        
        # === FILTRAGE TERMES FLOUS ÉTAPE 2 ===
        # Filtrer les termes flous initiaux résolus par les réponses
        initial_termes_flous = st.session_state.get("agent1_initial_termes_flous", [])
        if initial_termes_flous and followup_combined:
            # Mots-clés de résolution par type de terme
            resolution_map = {
                "ia": ["ia metier", "machine learning", "ml", "analytics", "dashboard", "bi", "predictif", "scoring", "transformation data"],
                "analytics": ["analytics", "bi", "dashboard", "reporting", "tableau", "power bi", "ia metier"],
                "gouvernance": ["qualite des donnees", "data lake", "synapse", "quality", "catalog", "master data", "reference data", "azure"],
                "cas d'usage": ["usage metier", "ia metier", "transformation", "data", "analytics", "automation", "projet"],
                "data": ["analytics", "bi", "data warehouse", "lake", "pipeline", "integration", "sql"],
                "piloter": ["projet", "transformation", "roadmap", "equipe", "team", "metier", "cadrage"]
            }
            
            filtered_termes = []
            for terme_obj in initial_termes_flous:
                terme = terme_obj.get("terme", "")
                terme_lower = terme.lower()
                
                # Trouver les keywords liés
                linked_keywords = []
                for key, kws in resolution_map.items():
                    if key in terme_lower:
                        linked_keywords = kws
                        break
                
                # Vérifier si le terme est résolu
                resolved = any(kw in followup_combined for kw in linked_keywords)
                if not resolved:
                    filtered_termes.append(terme_obj)
            
            raw_result["termes_flous"] = filtered_termes
        
        # === PROTECTION SCORING PAR DIMENSION ===
        # Si enrichissement → chaque dimension protégée ne peut pas diminuer
        if followup_combined and st.session_state.get("agent1_initial_score"):
            initial_score = st.session_state.agent1_initial_score
            # Dimensions à protéger: precision, screening, missions
            protected_dims = ["Précision du besoin", "Exploitabilité screening", "Clarté des missions"]
            
            protected_details = []
            for detail in computed_score.get("details", []):
                dim = detail.get("dimension", "")
                if dim in protected_dims:
                    old_dim_score = 0
                    new_dim_score = detail.get("score", 0)
                    # Trouver le score de l'étape 1
                    for init_d in initial_score.get("details", []):
                        if init_d.get("dimension") == dim:
                            old_dim_score = init_d.get("score", 0)
                            break
                    # Garder le max
                    if new_dim_score < old_dim_score:
                        detail["score"] = old_dim_score
                protected_details.append(detail)
            
            # Recalculer score_global depuis les détails protégés
            new_global = computed_score.get("score_global", 0)
            old_global = initial_score.get("score_global", 0)
            if new_global < old_global:
                computed_score["score_global"] = old_global
                computed_score["details"] = protected_details
                # Mettre à jour le niveau maturité
                if computed_score.get("niveau_maturite") != initial_score.get("niveau_maturite"):
                    computed_score["niveau_maturite"] = initial_score.get("niveau_maturite")
        
        # Mettre à jour le résultat filtré
        st.session_state.agent1_result = raw_result
    
    st.session_state.agent1_score = computed_score
    st.session_state.agent1_confidence = confidence
    st.session_state.agent1_job_family = pipeline_output.get("family", "Générique")
    st.session_state.agent1_job_subfamily = pipeline_output.get("subfamily", "Non précisé")
    st.session_state.agent1_language = lang
    st.session_state.agent1_result_language = lang

def rerun_analysis_if_language_changed(lang):
    if (
        st.session_state.agent1_conversation
        and st.session_state.agent1_result is not None
        and not st.session_state.agent1_invalid_input
        and st.session_state.agent1_result_language != lang
    ):
        with st.spinner(tr("retranslating", lang)):
            run_qualification_analysis(lang)
        st.rerun()
def main():
    init_agent1_state()

    st.set_page_config(
        page_title=tr("page_title", st.session_state.agent1_language),
        page_icon="",
        layout="wide",
        initial_sidebar_state="collapsed",
    )
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"] {
                display: none !important;
            }

            [data-testid="stSidebar"] {
                background: #22314d;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(AXA_STYLES, unsafe_allow_html=True)
    
    st.markdown(FLIP_CARD_STYLE, unsafe_allow_html=True)

    is_logged = render_login()
    if not is_logged:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"],
                [data-testid="stSidebar"],
                [data-testid="collapsedControl"] {
                    display: none !important;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.stop()

    if st.session_state.get("show_splash"):
        st.session_state.show_splash = False
        logo_b64 = image_to_base64("assets/logo_need2hire.png")

        if logo_b64:
            st.markdown(
                f"""
                <style>
                .splash-door {{
                    position: fixed;
                    inset: 0;
                    z-index: 999999;
                    background: white;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    animation: hideSplash 2.8s ease forwards;
                    pointer-events: none;
                }}

                .splash-logo {{
                    width: 620px;
                    max-width: 80vw;
                    animation: logoZoom 1.2s ease forwards;
                }}

                .door-left, .door-right {{
                    position: fixed;
                    top: 0;
                    width: 50vw;
                    height: 100vh;
                    background: white;
                    z-index: 1000000;
                    animation-duration: 2.4s;
                    animation-fill-mode: forwards;
                    animation-delay: 1.1s;
                    animation-timing-function: cubic-bezier(.77,0,.18,1);
                }}

                .door-left {{
                    left: 0;
                    animation-name: slideLeft;
                }}

                .door-right {{
                    right: 0;
                    animation-name: slideRight;
                }}

                @keyframes slideLeft {{
                    to {{ transform: translateX(-100%); }}
                }}

                @keyframes slideRight {{
                    to {{ transform: translateX(100%); }}
                }}

                @keyframes logoZoom {{
                    from {{ opacity: 0; transform: scale(.92); }}
                    to {{ opacity: 1; transform: scale(1); }}
                }}

                @keyframes hideSplash {{
                    0%, 85% {{ opacity: 1; }}
                    100% {{ opacity: 0; visibility: hidden; }}
                }}
                </style>

                <div class="splash-door">
                    <img class="splash-logo" src="data:image/png;base64,{logo_b64}">
                </div>
                <div class="door-left"></div>
                <div class="door-right"></div>
                """,
                unsafe_allow_html=True,
            )     
    # ici tu affiches ton bloc splash avec le logo base64
    render_premium_sidebar()

    lang = st.session_state.agent1_language

    st.markdown(
        f"""
        <div class="axa-hero">
          <div class="axa-hero-label">{tr("hero_label", lang)}</div>
          <div class="axa-hero-title">{tr("hero_title", lang)}</div>
          <div class="axa-hero-sub">{tr("hero_sub", lang)}</div>
          <div style="margin-top:16px;display:flex;gap:8px;flex-wrap:wrap">
            <span class="tag-pill" style="background:rgba(255,255,255,.1);color:#fff;border-color:rgba(255,255,255,.15)">{tr("tag_1", lang)}</span>
            <span class="tag-pill" style="background:rgba(255,255,255,.1);color:#fff;border-color:rgba(255,255,255,.15)">{tr("tag_2", lang)}</span>
            <span class="tag-pill" style="background:rgba(255,255,255,.1);color:#fff;border-color:rgba(255,255,255,.15)">{tr("tag_3", lang)}</span>
            <span class="tag-pill" style="background:rgba(255,255,255,.1);color:#fff;border-color:rgba(255,255,255,.15)">{tr("tag_4", lang)}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not TAXONOMY_ROWS:
        st.warning(tr("taxonomy_missing", lang))

    if not REFERENCE_ROWS:
        st.warning(tr("reference_missing", lang))

    if st.session_state.get("main_section") == "dashboard":
        with st.container(border=True):

            st.markdown(f"**{tr('settings', lang)}**")

            col0, col1, col2 = st.columns([1.3, 2, 1])

            with col0:

                previous_language = st.session_state.agent1_language

                selected_language = st.selectbox(
                    tr("language", lang),
                    options=["fr", "en", "es"],
                    format_func=lambda x: {
                        "fr": "Français",
                        "en": "English",
                        "es": "Español",
                    }[x],
                    index=["fr", "en", "es"].index(
                        st.session_state.agent1_language
                    ),
                    key="app_language",
                )

                if selected_language != previous_language:

                    st.session_state.agent1_language = selected_language
                    lang = selected_language

                    if st.session_state.get("agent1_result") is not None:
                        run_qualification_analysis(lang)

                    st.rerun()

                else:
                    lang = selected_language

            with col1:

                input_mode = st.radio(
                    tr("input_mode", lang),
                    [
                        tr("text", lang),
                        tr("micro", lang),
                        tr("audio_file", lang),
                    ],
                    horizontal=True,
                    key="input_mode_tab1",
                )

            with col2:

                st.markdown("<br>", unsafe_allow_html=True)

                if st.button(
                    tr("reset", lang),
                    use_container_width=True,
                    key="reset_main_btn",
                ):

                    reset_agent1()
                    st.rerun()

        rerun_analysis_if_language_changed(lang)

    else:
        input_mode = tr("text", lang)
    if not st.session_state.agent1_conversation:
        with st.container(border=True):
            st.markdown(f"**{tr('step1', lang)}**")

            source_text = ""

            if input_mode == tr("text", lang):
                source_text = st.text_area(
                    tr("content_to_analyze", lang),
                    height=220,
                    key="qualification_text",
                    placeholder=tr("real_need_placeholder", lang),
                )

                min_chars = 100
                current_text = st.session_state.get("qualification_text", "")
                current_chars = len(current_text.strip())
                progress = min(current_chars / min_chars, 1.0)

                st.progress(progress)

                if current_chars < min_chars:
                    missing_chars = min_chars - current_chars
                    st.info(tr("chars_remaining_info", lang).format(count=missing_chars))
                    button_label = tr("chars_remaining_button", lang).format(count=missing_chars)
                else:
                    st.success(tr("analysis_ready", lang))
                    button_label = tr("analyze_with_ai", lang)

                if st.button(
                    button_label,
                    use_container_width=True,
                    key="analyze_need_btn",
                ):
                    current_text = st.session_state.get("qualification_text", "").strip()

                    if len(current_text) < min_chars:
                        st.toast("Ajoutez encore quelques détails : contexte, missions, profil ou localisation.")
                        st.stop()

                    st.session_state.agent1_invalid_input = False
                    st.session_state.agent1_pipeline_output = {}
                    st.session_state.agent1_initial_missing = []
                    st.session_state.agent1_initial_questions = []
                    st.session_state.agent1_initial_termes_flous = []
                    st.session_state.agent1_initial_score = None
                    st.session_state.agent1_ignored_items = []
                    st.session_state.rh_active_input = None

                    st.session_state.agent1_conversation.append({
                        "type": "initial",
                        "content": current_text
                    })

                    run_qualification_analysis(lang)
                    st.rerun()

            elif input_mode == tr("micro", lang):
                st.info(tr("micro_info", lang))

                if "micro_transcription_text" not in st.session_state:
                    st.session_state.micro_transcription_text = ""

                if hasattr(st, "audio_input"):
                    audio_value = st.audio_input(tr("audio_record", lang))

                    if audio_value and st.button(
                        "Transcrire",
                        use_container_width=True,
                        key="micro_transcribe_only_btn",
                    ):
                        try:
                            suffix = Path(audio_value.name).suffix if getattr(audio_value, "name", None) else ".wav"
                            tmp_path = save_uploaded_audio_to_temp(audio_value, suffix)

                            with st.spinner(tr("audio_transcribing", lang)):
                                transcription = transcribe_audio_file(
                                    tmp_path,
                                    language=lang if lang in ["fr", "en", "es"] else "fr",
                                )

                            st.session_state.micro_transcription_text = transcription
                            st.session_state.micro_transcription_editor = transcription
                            st.rerun()

                        except Exception as e:
                            st.error(f"Erreur : {e}")

                        finally:
                            try:
                                if "tmp_path" in locals() and os.path.exists(tmp_path):
                                    os.remove(tmp_path)
                            except Exception:
                                pass

                    if "micro_transcription_editor" not in st.session_state:
                        st.session_state.micro_transcription_editor = st.session_state.get(
                            "micro_transcription_text",
                            ""
                        )

                    transcription_text = st.text_area(
                        "Transcription modifiable",
                        height=220,
                        key="micro_transcription_editor",
                        placeholder="La transcription apparaîtra ici. Vous pouvez la corriger avant analyse.",
                    )

                    if st.button(
                        tr("analyze_need", lang),
                        use_container_width=True,
                        key="micro_analyze_transcription_btn",
                    ):
                        if len(transcription_text.strip()) < 100:
                            st.warning("Veuillez compléter la transcription avant l’analyse.")
                            st.stop()

                        st.session_state.agent1_conversation.append({
                            "type": "initial",
                            "content": transcription_text.strip(),
                        })

                        run_qualification_analysis(lang)
                        st.rerun()

                else:
                    st.warning(tr("audio_input_warning", lang))
            elif input_mode == tr("audio_file", lang):
                uploaded_audio = st.file_uploader(
                    tr("upload_audio", lang),
                    type=["wav", "mp3", "m4a", "mp4", "mpeg", "webm", "ogg"],
                    key="audio_file_upload",
                )

                if uploaded_audio:
                    st.audio(uploaded_audio)

                    if st.button(
                        tr("transcribe_analyze", lang),
                        use_container_width=True,
                        key="file_transcribe_btn",
                    ):
                        try:
                            suffix = Path(uploaded_audio.name).suffix or ".wav"
                            tmp_path = save_uploaded_audio_to_temp(uploaded_audio, suffix)

                            with st.spinner(tr("audio_transcribing", lang)):
                                source_text = transcribe_audio_file(
                                    tmp_path,
                                    language=lang if lang in ["fr", "en", "es"] else "fr",
                                )

                            v = validate_recruitment_input(source_text)

                            if not v["valid"]:
                                reject_invalid_need(v.get("reason", STRICT_INVALID_MESSAGE))
                            else:
                                st.session_state.agent1_conversation.append({
                                    "type": "initial",
                                    "content": source_text,
                                })
                                run_qualification_analysis(lang)

                            st.rerun()

                        except Exception as e:
                            st.error(f"Erreur : {e}")

                        finally:
                            try:
                                if "tmp_path" in locals() and os.path.exists(tmp_path):
                                    os.remove(tmp_path)
                            except Exception:
                                pass

    if st.session_state.agent1_invalid_input:
        error_message = STRICT_INVALID_MESSAGE

        if (
            st.session_state.agent1_pipeline_output
            and st.session_state.agent1_pipeline_output.get("error")
        ):
            error_message = st.session_state.agent1_pipeline_output["error"]

        render_invalid_input_block(error_message)

    if st.session_state.agent1_result is not None:
        source_text = build_consolidated_text()

        prioritized_risks_data = prioritize_risks(
            st.session_state.agent1_result.get("risques_detectes", [])
        )

        with st.expander(tr("view_analyzed_need", lang), expanded=False):
            st.text_area(
                "Texte utilisé pour l'analyse",
                value=source_text,
                height=220,
                disabled=True,
                key="analyzed_need_view",
                placeholder=tr("real_need_placeholder", lang),
                on_change=lambda: st.session_state.update(
                    {"qualification_text_dirty": True}
                ),
            )

        market_benchmark = None
        if st.session_state.agent1_pipeline_output:
            market_benchmark = st.session_state.agent1_pipeline_output.get("market_benchmark")

        render_markdown = generate_qualification_report_markdown(
            source_text=source_text,
            job_family=st.session_state.agent1_job_family,
            job_subfamily=st.session_state.agent1_job_subfamily,
            result=st.session_state.agent1_result,
            computed_score=st.session_state.agent1_score,
            confidence=st.session_state.agent1_confidence,
            prioritized_risks=prioritized_risks_data,
            lang=lang,
        )

        render_analysis_block(
            source_text=source_text,
            job_family=st.session_state.agent1_job_family,
            job_subfamily=st.session_state.agent1_job_subfamily,
            raw_result=st.session_state.agent1_result,
            display_result=st.session_state.agent1_display_result,
            computed_score=st.session_state.agent1_score,
            confidence=st.session_state.agent1_confidence,
            lang=lang,
            prioritized_risks_data=prioritized_risks_data,
            render_markdown=render_markdown,
            market_benchmark=market_benchmark,
            on_followup_submit=run_qualification_analysis,
        )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # with st.container(border=True):
        #     st.markdown(f"**{tr('step2', lang)}**")
        #     st.caption(tr("step2_caption", lang))

        #     followup_text = st.text_area(
        #         tr("new_precisions", lang),
        #         height=140,
        #         key="agent1_followup_text",
        #         placeholder=tr("followup_placeholder", lang),
        #     )

        #     if st.button(tr("update_analysis", lang), use_container_width=True, key="update_analysis_btn"):
        #         v = validate_recruitment_input(followup_text)

        #         if not v["valid"]:
        #             reject_invalid_need(v.get("reason", STRICT_INVALID_MESSAGE))
        #         else:
        #             st.session_state.agent1_conversation.append({
        #                 "type": "followup",
        #                 "content": followup_text,
        #             })
        #             run_qualification_analysis(lang)

        #         st.rerun()
if __name__ == "__main__":
    main()