import os
from pathlib import Path
from auth import render_login, render_logout
import streamlit as st

from styles import AXA_STYLES, FLIP_CARD_STYLE
from i18n import tr
from config import STRICT_INVALID_MESSAGE
from data.data_layer import TAXONOMY_ROWS, REFERENCE_ROWS
from orchestration.pipeline import run_pipeline
from validation.validation import validate_recruitment_input, build_display_result
from domain.scoring import prioritize_risks
from ui.reporting import generate_qualification_report_markdown
from ui.ui_components import render_analysis_block, render_invalid_input_block
from services.audio_service import transcribe_audio_file, save_uploaded_audio_to_temp


EXAMPLE_QUALIFICATION = (
    "Nous recherchons un chef de projet data senior pour piloter des cas d’usage IA et analytics au sein d’une équipe transformation. "
    "Le poste est basé à Nanterre, en CDI. Le candidat doit avoir une expérience en gestion de projet, coordination métier/IT, gouvernance de données, "
    "suivi de roadmap et animation d’ateliers. Une connaissance de Power BI, SQL et des environnements cloud est souhaitée."
)


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

    niveau_experience_value = normalize_simple(fiche.get("niveau_experience", ""))
    localisation_value = normalize_simple(fiche.get("localisation", ""))
    contrat_value = normalize_simple(fiche.get("type_contrat", ""))

    seniority_present = (
        any(
            x in text
            for x in [
                "senior", "junior", "confirmé", "confirme", "expérimenté", "experimente",
                "1 an", "2 ans", "3 ans", "4 ans", "5 ans", "6 ans", "7 ans", "8 ans", "9 ans", "10 ans",
                "year", "years", "experience",
            ]
        )
        or any(
            x in niveau_experience_value
            for x in [
                "senior", "junior", "confirmé", "confirme", "expérimenté", "experimente",
                "1 an", "2 ans", "3 ans", "4 ans", "5 ans", "6 ans", "7 ans", "8 ans", "9 ans", "10 ans",
                "year", "years", "experience",
            ]
        )
    )

    contract_present = (
        any(
            x in text
            for x in ["cdi", "cdd", "freelance", "stage", "alternance", "contract", "internship"]
        )
        or any(
            x in contrat_value
            for x in ["cdi", "cdd", "freelance", "stage", "alternance", "contract", "internship"]
        )
    )

    location_present = (
        any(
            x in text
            for x in [
                "nanterre", "paris", "lyon", "marseille", "lille", "toulouse",
                "bordeaux", "nantes", "remote", "hybride", "hybrid",
            ]
        )
        or len(localisation_value) > 0
    )

    ai_analytics_domain_present = any(
        x in text
        for x in [
            "data analytics", "analytics", "analyse de données", "analyse de donnees",
            "data visualisation", "power bi", "tableau", "machine learning", "ml",
            "intelligence artificielle", "ia", "sql", "data engineering", "gouvernance",
            "qualité des données", "qualite des donnees", "segmentation", "scoring",
            "prédiction", "prediction",
        ]
    )

    cleaned = []

    for item in missing_list or []:
        item_norm = normalize_simple(item)

        if any(
            x in item_norm
            for x in [
                "famille métier", "famille metier",
                "sous-famille métier", "sous-famille metier",
                "sous famille métier", "sous famille metier",
                "mots-clés métier", "mots cles metier",
                "mots-clés", "mots cles",
                "job family", "sub-family", "sub family", "keywords", "key words",
            ]
        ):
            continue

        if any(
            x in item_norm
            for x in [
                "niveau d’expérience",
                "niveau d'experience",
                "niveau d experience",
                "niveau experience",
                "seniority",
                "number of years",
                "années d'expérience",
                "annees d'experience",
                "nombre d'années",
                "nombre d annees",
                "années exactes",
                "annees exactes",
                "niveau d'expérience précis",
                "niveau d experience precis",
                "préciser l'expérience",
                "preciser l experience",
                "préciser le niveau d'expérience",
                "preciser le niveau d experience",
                "experience precise",
                "exact years",
                "years of experience",
                "précision sur l'expérience",
                "precision sur l experience",
            ]
        ) and seniority_present:
            continue

        if any(
            x in item_norm
            for x in ["durée du contrat", "duree du contrat", "type de contrat", "contract duration"]
        ) and contract_present:
            continue

        if any(
            x in item_norm
            for x in ["localisation", "location", "based in", "préférence de localisation", "preference de localisation"]
        ) and location_present:
            continue

        if any(
            x in item_norm
            for x in [
                "ia", "analytics", "analyt", "gouvernance",
                "qualité des données", "qualite des donnees",
                "domaines spécifiques", "domaines specifiques",
                "machine learning", "data", "sql", "power bi",
            ]
        ) and ai_analytics_domain_present:
            continue

        cleaned.append(item)

    return cleaned


def run_qualification_analysis(lang):
    consolidated_text = build_consolidated_text()
    validation = validate_recruitment_input(consolidated_text)

    if not validation["valid"]:
        reject_invalid_need(STRICT_INVALID_MESSAGE)
        return

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

        raw_result["informations_manquantes"] = clean_missing_info(
            raw_result.get("informations_manquantes", []),
            consolidated_text,
            result=raw_result,
            job_family=pipeline_output.get("family", ""),
            job_subfamily=pipeline_output.get("subfamily", ""),
        )

        # Si aucun vrai manque bloquant, aucune question de clarification
        if not raw_result.get("informations_manquantes"):
            raw_result["questions_de_clarification"] = []

        # Sécurité supplémentaire : si le cœur du besoin est présent,
        # on supprime les faux manques et fausses questions générées par le LLM
        fiche = raw_result.get("fiche_de_poste_axa", {})

        has_core_info = all([
            fiche.get("intitule_poste"),
            fiche.get("type_contrat"),
            fiche.get("niveau_experience"),
            fiche.get("localisation"),
            fiche.get("votre_role_et_vos_missions"),
            fiche.get("votre_profil"),
        ])

        if has_core_info:
            raw_result["informations_manquantes"] = []
            raw_result["questions_de_clarification"] = []

        display_result = build_display_result(raw_result)
        computed_score = pipeline_output["score"]
        confidence = pipeline_output["confidence"]

    if raw_result is None or display_result is None:
        reject_invalid_need("Erreur pendant l’analyse. Veuillez réessayer.")
        return

    st.session_state.agent1_invalid_input = False
    st.session_state.agent1_result = raw_result
    st.session_state.agent1_display_result = display_result
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

    st.markdown(AXA_STYLES, unsafe_allow_html=True)
    st.markdown(FLIP_CARD_STYLE, unsafe_allow_html=True)
    if not render_login():
         st.stop()

    render_logout()
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

    with st.container(border=True):
        st.markdown(f"**{tr('settings', lang)}**")
        col0, col1, col2 = st.columns([1.3, 2, 1])

        with col0:
            lang = "fr"
            st.session_state.agent1_language = "fr"
            #selected_language = st.selectbox(
            #    tr("language", lang),
            #    options=["fr", "en", "es"],
            #   format_func=lambda x: {"fr": "Français", "en": "English", "es": "Español"}[x],
            #   index=["fr", "en", "es"].index(st.session_state.agent1_language),
            #   key="app_language",
            #)
            #st.session_state.agent1_language = selected_language
            #lang = selected_language

        with col1:
            input_mode = st.radio(
                tr("input_mode", lang),
                [tr("text", lang), tr("micro", lang), tr("audio_file", lang)],
                horizontal=True,
                key="input_mode_tab1",
            )

        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button(tr("reset", lang), use_container_width=True):
                reset_agent1()
                st.rerun()

    rerun_analysis_if_language_changed(lang)

    if st.session_state.agent1_result is not None:
        with st.container(border=True):
            st.markdown("**Famille et sous-famille détectées**")
            col_a, col_b = st.columns(2)
            with col_a:
                st.write(f"Famille : {st.session_state.agent1_job_family}")
            with col_b:
                st.write(f"Sous-famille : {st.session_state.agent1_job_subfamily}")

    if not st.session_state.agent1_conversation:
        with st.container(border=True):
            st.markdown(f"**{tr('step1', lang)}**")

            if input_mode == tr("text", lang):
                source_text = st.text_area(
                    tr("content_to_analyze", lang),
                    value=EXAMPLE_QUALIFICATION,
                    height=220,
                    key="qualification_text",
                    placeholder=tr("real_need_placeholder", lang),
                )
                if st.button(tr("analyze_need", lang), use_container_width=True):
                    v = validate_recruitment_input(source_text)
                    if not v["valid"]:
                        reject_invalid_need(STRICT_INVALID_MESSAGE)
                    else:
                        st.session_state.agent1_conversation.append({"type": "initial", "content": source_text})
                        run_qualification_analysis(lang)
                    st.rerun()

            elif input_mode == tr("micro", lang):
                st.info(tr("micro_info", lang))
                if hasattr(st, "audio_input"):
                    audio_value = st.audio_input(tr("audio_record", lang))
                    if audio_value and st.button(tr("transcribe_analyze", lang), use_container_width=True):
                        try:
                            suffix = Path(audio_value.name).suffix if getattr(audio_value, "name", None) else ".wav"
                            tmp_path = save_uploaded_audio_to_temp(audio_value, suffix)
                            with st.spinner(tr("audio_transcribing", lang)):
                                source_text = transcribe_audio_file(
                                    tmp_path,
                                    language=lang if lang in ["fr", "en", "es"] else "fr",
                                )
                            v = validate_recruitment_input(source_text)
                            if not v["valid"]:
                                reject_invalid_need(STRICT_INVALID_MESSAGE)
                            else:
                                st.session_state.agent1_conversation.append({"type": "initial", "content": source_text})
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
                else:
                    st.warning(tr("audio_input_warning", lang))

            elif input_mode == tr("audio_file", lang):
                uploaded_audio = st.file_uploader(
                    tr("upload_audio", lang),
                    type=["wav", "mp3", "m4a", "mp4", "mpeg", "webm", "ogg"],
                )
                if uploaded_audio:
                    st.audio(uploaded_audio)
                    if st.button(tr("transcribe_analyze", lang), use_container_width=True):
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
                                reject_invalid_need(STRICT_INVALID_MESSAGE)
                            else:
                                st.session_state.agent1_conversation.append({"type": "initial", "content": source_text})
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

        render_markdown = generate_qualification_report_markdown(
            source_text=source_text,
            job_family=st.session_state.agent1_job_family,
            job_subfamily=st.session_state.agent1_job_subfamily,
            result=st.session_state.agent1_result,
            computed_score=st.session_state.agent1_score,
            confidence=st.session_state.agent1_confidence,
            prioritized_risks=prioritized_risks_data,
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
        )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        with st.container(border=True):
            st.markdown(f"**{tr('step2', lang)}**")
            st.caption(tr("step2_caption", lang))

            followup_text = st.text_area(
                tr("new_precisions", lang),
                height=140,
                key="agent1_followup_text",
                placeholder=tr("followup_placeholder", lang),
            )

            if st.button(tr("update_analysis", lang), use_container_width=True):
                v = validate_recruitment_input(followup_text)
                if not v["valid"]:
                    reject_invalid_need(STRICT_INVALID_MESSAGE)
                else:
                    st.session_state.agent1_conversation.append({"type": "followup", "content": followup_text})
                    run_qualification_analysis(lang)
                st.rerun()


if __name__ == "__main__":
    main()