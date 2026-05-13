import uuid
import streamlit as st
import streamlit.components.v1 as components
import re
from i18n import tr
from domain.scoring import build_quality_checklist, build_screening_recommendations
from ui.reporting import generate_recruiter_brief_email, generate_outlook_meeting_link
from data.data_layer import filter_taxonomy_rows, extract_reference_examples


def render_section_title(title: str):
    st.markdown(f'<div class="section-title">{title}</div>', unsafe_allow_html=True)


def render_flip_card(title, score, max_score, details, badge_text="", is_decision=False):
    card_id = str(uuid.uuid4()).replace("-", "")
    details_html = "".join(f"<div style='margin-bottom:8px;'>• {d}</div>" for d in details)

    front_main = (
        f'<div class="flip-score-text">{score}<span class="flip-score-suffix">/{max_score}</span></div>'
        if not is_decision
        else f'<div class="flip-decision-text">{score}</div>'
    )

    badge_html = f'<div class="flip-badge">{badge_text}</div>' if badge_text else ""

    html = f"""
    <html>
    <head>
    <style>
        body {{
            margin: 0;
            padding: 0;
            background: transparent;
            font-family: "DM Sans", Arial, sans-serif;
        }}

        .flip-container {{
            perspective: 1200px;
            width: 100%;
            height: 210px;
        }}

        .flip-card {{
            width: 100%;
            height: 100%;
            position: relative;
            transform-style: preserve-3d;
            transition: transform 0.7s ease;
            cursor: pointer;
        }}

        .flip-card.flipped {{
            transform: rotateY(180deg);
        }}

        .flip-face {{
            position: absolute;
            inset: 0;
            backface-visibility: hidden;
            border-radius: 18px;
            border: 1px solid #DDE3EF;
            box-shadow: 0 4px 20px rgba(0,0,0,0.06);
            padding: 24px;
            box-sizing: border-box;
            background: white;
        }}

        .flip-front {{
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
        }}

        .flip-back {{
            background: #F5F7FB;
            transform: rotateY(180deg);
            overflow-y: auto;
        }}

        .flip-score-text {{
            font-family: Georgia, "Times New Roman", serif;
            font-size: 62px;
            font-weight: 700;
            color: #16337A;
            line-height: 1;
            margin-bottom: 10px;
        }}

        .flip-score-suffix {{
            font-size: 24px;
            color: #6B7280;
            margin-left: 4px;
        }}

        .flip-decision-text {{
            font-family: Georgia, "Times New Roman", serif;
            font-size: 34px;
            font-weight: 700;
            color: #16337A;
            line-height: 1.2;
            margin-bottom: 10px;
        }}

        .flip-label {{
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.12em;
            text-transform: uppercase;
            color: #6B7280;
            margin-bottom: 14px;
        }}

        .flip-badge {{
            display: inline-block;
            background: #CFEEDB;
            color: #0B6B4B;
            border-radius: 999px;
            padding: 10px 18px;
            font-size: 14px;
            font-weight: 700;
            margin-top: 2px;
        }}

        .flip-hint {{
            margin-top: 10px;
            font-size: 13px;
            color: #94A3B8;
        }}

        .flip-back-title {{
            font-size: 20px;
            font-weight: 700;
            color: #16337A;
            margin-bottom: 14px;
        }}

        .flip-back-content {{
            font-size: 15px;
            line-height: 1.55;
            color: #1A1A3E;
        }}
    </style>
    </head>
    <body>
        <div class="flip-container">
            <div id="card-{card_id}" class="flip-card" onclick="flip_{card_id}()">
                <div class="flip-face flip-front">
                    {front_main}
                    <div class="flip-label">{title}</div>
                    {badge_html}
                    <div class="flip-hint">{tr("kpi_click_hint", st.session_state.get("agent1_language", "fr"))}</div>
                </div>

                <div class="flip-face flip-back">
                    <div class="flip-back-title">{tr("detail", st.session_state.get("agent1_language", "fr"))}</div>
                    <div class="flip-back-content">
                        {details_html}
                    </div>
                </div>
            </div>
        </div>

        <script>
            function flip_{card_id}() {{
                const card = document.getElementById("card-{card_id}");
                card.classList.toggle("flipped");
            }}
        </script>
    </body>
    </html>
    """

    components.html(html, height=230)
def render_clickable_score_bar(detail, lang):
    label = detail["dimension"]
    score = detail["score"]
    max_score = detail["sur"]
    commentaire = detail.get("commentaire", "—")
    formule = detail.get("formule", [])
    purpose = detail.get("purpose", "—")

    pct = int((score / max_score) * 100)
    color = "#DC2626" if pct < 40 else "#D97706" if pct < 70 else "#059669"

    with st.expander(f"{label} — {score}/{max_score}", expanded=False):
        st.markdown(
            f"""
            <div class="score-row">
              <div class="score-label">
                <span>{label}</span>
                <span style="font-weight:700;color:{color}">{score}/{max_score}</span>
              </div>
              <div class="score-bar-track">
                <div class="score-bar-fill" style="width:{pct}%;background:{color}"></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(f"**{tr('kpi_purpose', lang)}**")
        st.write(purpose)

        st.markdown(f"**{tr('kpi_score_reason', lang)}**")
        for step in formule:
            st.write(f"• {step}")



def render_fiche_poste(fiche, lang):
    intitule = fiche.get("intitule_poste", "Non précisé")
    st.markdown(
        f"""
        <div class="fiche-header">
          <div style="font-size:0.72rem;letter-spacing:.12em;text-transform:uppercase;color:rgba(255,255,255,.5);margin-bottom:6px">{tr("job_sheet", lang)}</div>
          <div class="fiche-header-title">{intitule}</div>
          <div class="fiche-header-meta">{fiche.get('societe_du_groupe','AXA')} · {fiche.get('localisation','—')} · {fiche.get('type_contrat','—')}</div>
        </div>
        <div class="fiche-body">
          <div class="fiche-meta-grid">
            <div><div class="fiche-meta-key">{tr("reference", lang)}</div><div class="fiche-meta-val">{fiche.get('reference_offre','—')}</div></div>
            <div><div class="fiche-meta-key">{tr("experience", lang)}</div><div class="fiche-meta-val">{fiche.get('niveau_experience','—')}</div></div>
            <div><div class="fiche-meta-key">{tr("job_family", lang)}</div><div class="fiche-meta-val">{fiche.get('famille_metier','—')}</div></div>
          </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(f'<div class="fiche-section-title">{tr("intro", lang)}</div>', unsafe_allow_html=True)
    st.write(fiche.get("introduction_poste", "Non précisé"))

    st.markdown(f'<div class="fiche-section-title">{tr("missions", lang)}</div>', unsafe_allow_html=True)
    st.write(fiche.get("accroche_missions", ""))
    for m in fiche.get("votre_role_et_vos_missions", []):
        st.markdown(
            f'<div class="mission-item"><div class="mission-dot"></div><div>{m}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(f'<div class="fiche-section-title">{tr("profile", lang)}</div>', unsafe_allow_html=True)
    for p in fiche.get("votre_profil", []):
        st.markdown(
            f'<div class="mission-item"><div class="mission-dot"></div><div>{p}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(f'<div class="fiche-section-title">{tr("why_join", lang)}</div>', unsafe_allow_html=True)
    for item in fiche.get("pourquoi_nous_rejoindre", []):
        st.markdown(
            f'<div class="mission-item"><div class="mission-dot"></div><div>{item}</div></div>',
            unsafe_allow_html=True
        )

    st.markdown(f'<div class="fiche-section-title">{tr("work_env", lang)}</div>', unsafe_allow_html=True)
    for item in fiche.get("votre_environnement_de_travail", []):
        st.markdown(
            f'<div class="mission-item"><div class="mission-dot"></div><div>{item}</div></div>',
            unsafe_allow_html=True
        )


def render_checklist(result, computed_score, lang: str = "fr"):
    checklist = build_quality_checklist(result, computed_score, lang)
    
    # Get translated status values
    oui = tr("checklist_oui", lang)
    non = tr("checklist_non", lang)
    partiel = tr("checklist_partiel", lang)
    
    for item in checklist:
        statut = item["statut"]
        css_class = "check-oui" if statut == oui else "check-non" if statut == non else "check-partiel"
        icon = "✓" if statut == oui else "✗" if statut == non else "~"
        st.markdown(
            f"""
            <div class="axa-card" style="padding:14px 18px;margin-bottom:8px">
              <div style="display:flex;justify-content:space-between;align-items:center">
                <span style="font-weight:600;font-size:0.9rem">{item['critere']}</span>
                <span class="{css_class}">{icon} {statut}</span>
              </div>
              <div style="font-size:0.82rem;color:var(--axa-muted);margin-top:4px">{item['commentaire']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )


def render_risks(prioritized_risks, lang="fr"):
    section_map = {
    "Bloquant": tr("risk_blocking", lang),
    "Important": tr("risk_important", lang),
    "Amélioration": tr("risk_improvement", lang),
}

    for section in ["Bloquant", "Important", "Amélioration"]:
        section_label = section_map[section]
        risks = prioritized_risks[section]
        css = {
            "Bloquant": "risk-bloquant",
            "Important": "risk-important",
            "Amélioration": "risk-amelioration"
        }[section]
        if risks:
            for r in risks:
                st.markdown(
                    f"""
                    <div class="axa-card" style="padding:14px 18px;margin-bottom:8px">
                      <div style="display:flex;align-items:center;gap:10px;margin-bottom:4px">
                        <span class="{css}">{section_label}</span>
                        <span style="font-weight:600;font-size:0.9rem">{r.get('risque','—')}</span>
                      </div>
                      <div style="font-size:0.82rem;color:var(--axa-muted)">{r.get('explication','—')}</div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )


def render_taxonomy_panel(job_family: str, job_subfamily: str, lang: str):
    refs = filter_taxonomy_rows(job_family, job_subfamily)
    detailed_examples = extract_reference_examples(job_family, job_subfamily)

    with st.container(border=True):
        st.markdown(f"### {tr('reference_panel', lang)}")

        if not refs and not detailed_examples:
            st.warning(tr("reference_not_found", lang))
            return

        if refs:
            for row in refs:
                with st.expander(f"{row.get('famille_metier_axa', '—')} — {row.get('sous_famille_metier', '—')}"):
                    st.markdown(f"**{tr('examples_jobs', lang)}** : {row.get('exemples_postes', '—')}")
                    st.markdown(f"**{tr('business_keywords', lang)}** : {row.get('mots_cles', '—')}")

        if detailed_examples:
            st.markdown(f"#### {tr('detailed_examples', lang)}")
            for example in detailed_examples:
                st.write(f"- {example}")

def render_analysis_block(
    source_text,
    job_family,
    job_subfamily,
    raw_result,
    display_result,
    computed_score,
    confidence,
    lang,
    prioritized_risks_data,
    render_markdown,
    market_benchmark=None,
    on_followup_submit=None,
):
    fiche = display_result.get("fiche_de_poste_axa", {})
    section = st.session_state.get("main_section", "dashboard")

    if section == "dashboard":
        col1, col2, col3 = st.columns(3)

        with col1:
            render_flip_card(
                title=tr("score_expl", lang),
                score=computed_score["score_global"],
                max_score=100,
                badge_text=computed_score["niveau_maturite"],
                details=[
                    tr("score_card_detail", lang),
                    f"{tr('current_level', lang)} : {computed_score['niveau_maturite']}"
                ],
            )

        with col2:
            render_flip_card(
                title=tr("confidence_score", lang),
                score=confidence["score"],
                max_score=100,
                badge_text=confidence["level"],
                details=[tr("confidence_card_detail", lang)],
            )

        with col3:
            render_flip_card(
                title=tr("decision", lang),
                score=computed_score["decision"],
                max_score="",
                badge_text=computed_score["decision"],
                is_decision=True,
                details=[f"{tr('current_decision', lang)} : {computed_score['decision']}",],
            )

        st.markdown(
            f'<div class="small-note"><strong>{tr("score_note", lang)}</strong></div>',
            unsafe_allow_html=True,
        )

        render_section_title(tr("executive_summary", lang))
        st.markdown(
            f'<div class="info-box">{raw_result.get("resume_besoin", "—")}</div>',
            unsafe_allow_html=True,
        )

        render_section_title(tr("detailed_score", lang))
        st.caption(tr("click_kpi_caption", lang))

        for d in computed_score["details"]:
            render_clickable_score_bar(d, lang)

        if computed_score.get("recommandations"):
            st.markdown(
                '<div class="warn-box"><strong>'
                + tr("recommendations", lang)
                + " :</strong><br>"
                + "<br>".join(f"• {r}" for r in computed_score["recommandations"])
                + "</div>",
                unsafe_allow_html=True,
            )

        return

    if section == "fiche":
        render_fiche_poste(fiche, lang)

    elif section == "analyse":
    # 1. Nouvelle page Figma
        render_rh_analysis_page(
            lang=lang,
            on_followup_submit=on_followup_submit,
        )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        # 2. Ancien contenu Analyse RH
        render_analysis_details_section(
            raw_result=raw_result,
            prioritized_risks_data=prioritized_risks_data,
            market_benchmark=market_benchmark,
            lang=lang,
        )
    elif section == "checklist":
        st.markdown(f"#### {tr('quality_checklist', lang)}")
        render_checklist(raw_result, computed_score, lang)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown(f"#### {tr('screening_reco', lang)}")
        for reco in build_screening_recommendations(raw_result, lang):
            st.markdown(
                f'<div class="axa-card axa-card-green" style="padding:12px 16px;margin-bottom:8px;font-size:0.88rem">• {reco}</div>',
                unsafe_allow_html=True,
            )

    elif section == "brief":
        st.markdown(f"#### {tr('recruiter_brief', lang)}")
        brief_email = generate_recruiter_brief_email(
            job_family, job_subfamily, raw_result, computed_score, lang
        )

        brief_email_edited = st.text_area(
            tr("editable_before_send", lang),
            value=brief_email,
            height=420,
            key="brief_email_area",
        )

        st.download_button(
            label=tr("download_brief", lang),
            data=brief_email_edited.encode("utf-8"),
            file_name=f"brief_recruteur_{job_family.replace(' ', '_').replace('/', '').lower()}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_brief_email",
        )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(f"#### {tr('meeting_plan', lang)}")

        meeting_link = generate_outlook_meeting_link(
            fiche.get("intitule_poste", "Poste à pourvoir"),
            brief_email_edited,
            raw_result.get("questions_de_clarification", []),
            lang,
        )

        st.markdown(
            f'<a href="{meeting_link}" class="outlook-btn">{tr("open_outlook", lang)}</a>',
            unsafe_allow_html=True,
        )
        st.caption(tr("outlook_caption", lang))

    elif section == "references":
        render_taxonomy_panel(job_family, job_subfamily, lang)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.download_button(
        label=tr("download_report", lang),
        data=render_markdown.encode("utf-8"),
        file_name="rapport_qualification_besoin_axa.md",
        mime="text/markdown",
        use_container_width=True,
        key="download_tab1_conversation",
    )
def render_analysis_details_section(raw_result, prioritized_risks_data, market_benchmark, lang):
    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown(
            f"""
            <div class="clarify-card">
                <div class="clarify-header">
                    <div class="clarify-icon">?</div>
                    <div class="clarify-title">{tr('fuzzy_terms', lang)}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )

        for idx, item in enumerate(raw_result.get("termes_flous", [])):
            terme = item.get("terme", "—")
            detail = item.get("pourquoi_c_est_flou", "—")

            with st.expander(terme, expanded=False):
                st.markdown(
                    f"""
                    <div class="clarify-answer">
                        {detail}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

        st.markdown("</div>", unsafe_allow_html=True)

        #st.markdown(f"#### {tr('missing_info', lang)}")
        #for info in raw_result.get("informations_manquantes", []):
        #   st.markdown(f"- {info}")
        st.markdown(
            f"""
            <div class="clarify-card">
                <div class="clarify-header">
                    <div class="clarify-icon">?</div>
                    <div class="clarify-title">{tr('clarification_questions', lang)}</div>
                </div>
            """,
            unsafe_allow_html=True,
        )
        #st.markdown(f"#### {tr('clarification_questions', lang)}")

        for i, q in enumerate(raw_result.get("questions_de_clarification", []), 1):
            html = f"""
        <div class="question-card">
            <div class="question-tag">Clarification {i}</div>
            <div class="question-text">{q}</div>
        </div>
        """
            st.markdown(html, unsafe_allow_html=True)

    with col_right:
        st.markdown(f"#### {tr('prioritized_risks', lang)}")
        render_risks(prioritized_risks_data, lang)

        st.markdown(f"#### {tr('evaluation_criteria', lang)}")

        for crit in raw_result.get("criteres_d_evaluation", []):
            critere = crit.get("critere", "—")
            objectif = crit.get("objectif", "—")

            html = f"""<div class="criteria-card">
        <div class="criteria-checkbox"></div>
        <div class="criteria-content">
        <div class="criteria-title">{critere}</div>
        <div class="criteria-desc">{objectif}</div>
        </div>
        </div>"""

            st.markdown(html, unsafe_allow_html=True)

        st.markdown(
        f"""
        <div class="interview-header">
            <div class="interview-icon">🗂</div>
            <div class="interview-title">
                {tr('interview_questions', lang)}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
        for i, q in enumerate(raw_result.get("questions_entretien", []), 1):
            st.markdown(f"{i}. {q}")
def render_invalid_input_block(message: str):
    st.markdown(f'<div class="invalid-box">{message}</div>', unsafe_allow_html=True)
def get_user_name_from_email(email: str) -> str:
    local = (email or "").split("@")[0]
    local = local.replace(".external", "")
    local = re.sub(r"\d+", "", local)

    parts = [p.capitalize() for p in local.split(".") if p]
    return " ".join(parts) if parts else "Utilisateur"
def render_premium_sidebar(user_name: str = None, user_role: str = "RH Manager", offers_count: int = 12):
    user_email = st.session_state.get("user_email", "")
    user_name = user_name or get_user_name_from_email(user_email)
    initials = "".join([part[0] for part in user_name.split()[:2]]).upper()
    with st.sidebar:
        st.markdown(
            """
            <style>
                section[data-testid="stSidebar"] nav,
                [data-testid="stSidebarNav"],
                div[data-testid="stSidebarNavItems"],
               

                [data-testid="stSidebar"] {
                    background: #22314d;
                }

                .sidebar-brand {
                    padding: 22px 12px 18px 12px;
                    margin-bottom: 18px;
                    border-bottom: 1px solid rgba(255,255,255,0.12);
                    color: white;
                }
                .sidebar-user-card {
                    position: fixed;
                    bottom: 28px;
                    left: 20px;
                    width: 245px;
                    display: flex;
                    align-items: center;
                    gap: 14px;
                    padding: 16px;
                    border-top: 1px solid rgba(255,255,255,0.12);
                    color: white;
                }

                .sidebar-avatar {
                    width: 52px;
                    height: 52px;
                    border-radius: 999px;
                    background: linear-gradient(135deg, #7C3AED, #6D3DF5);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-weight: 900;
                    font-size: 18px;
                    color: white;
                }

                .sidebar-user-name {
                    font-size: 17px;
                    font-weight: 900;
                    color: white;
                }

                .sidebar-user-role {
                    font-size: 14px;
                    color: #B8C2D6;
                }

                .sidebar-chevron {
                    margin-left: auto;
                    color: #94A3B8;
                    font-size: 18px;
                }
                .sidebar-brand-title {
                    font-size: 24px;
                    font-weight: 900;
                    color: white;
                    margin-bottom: 4px;
                }

                .sidebar-brand-subtitle {
                    font-size: 13px;
                    color: #dbeafe;
                }

                .sidebar-group {
                    color: #94a3b8;
                    font-size: 12px;
                    font-weight: 800;
                    text-transform: uppercase;
                    letter-spacing: .08em;
                    margin: 22px 0 8px 0;
                }

                div.stButton > button {
                    border-radius: 14px !important;
                    min-height: 46px !important;
                    font-weight: 800 !important;
                    justify-content: flex-start !important;
                    padding-left: 18px !important;
                }

                div.stButton > button[data-testid="baseButton-primary"] {
                    background: linear-gradient(90deg, #6D3DF5, #5147F5) !important;
                    color: white !important;
                    border: none !important;
                    box-shadow: 0 10px 24px rgba(91, 61, 245, 0.35) !important;
                }

                div.stButton > button[data-testid="baseButton-secondary"] {
                    background: transparent !important;
                    color: #B8C2D6 !important;
                    border: none !important;
                }

                div.stButton > button[data-testid="baseButton-secondary"]:hover {
                    background: rgba(255,255,255,0.08) !important;
                    color: white !important;
                }
            </style>

            <div class="sidebar-brand">
                <div class="sidebar-brand-title">Need2Hire</div>
                <div class="sidebar-brand-subtitle">AI HR Copilot</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if "main_section" not in st.session_state:
            st.session_state["main_section"] = "dashboard"

        def sidebar_button(label, section_key, icon=""):
            active = st.session_state.get("main_section") == section_key
            button_type = "primary" if active else "secondary"

            if st.button(
                f"{icon}  {label}",
                use_container_width=True,
                key=f"sidebar_{section_key}",
                type=button_type,
            ):
                st.session_state["agent1_current_page"] = "dashboard"
                st.session_state["main_section"] = section_key
                st.rerun()

        st.markdown('<div class="sidebar-group">Production</div>', unsafe_allow_html=True)

        current_lang = st.session_state.get("agent1_language", "fr")

        sidebar_button("Dashboard", "dashboard", "▦")
        sidebar_button(tr("job_sheet", current_lang), "fiche", "📄")
        sidebar_button(tr("hr_analysis", current_lang), "analyse", "▥")
        sidebar_button(tr("checklist_screening", current_lang), "checklist", "✓")
        sidebar_button(tr("brief_meeting", current_lang), "brief", "✉")
        sidebar_button(tr("reference_history", current_lang), "references", "⌘")
        initials = "".join([part[0] for part in user_name.split()[:2]]).upper()

        st.markdown(
            f"""
            <div style="height:40px"></div>
            <div class="sidebar-user-card">
                <div class="sidebar-avatar">{initials}</div>
                <div>
                    <div class="sidebar-user-name">{user_name}</div>
                    <div class="sidebar-user-role">{user_role}</div>
                </div>
                <div class="sidebar-chevron">⌄</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <style>
            .logout-zone + div button {
                background: #DC2626 !important;
                color: white !important;
                border: none !important;
                border-radius: 14px !important;
                font-weight: 700 !important;
            }

            .logout-zone + div button:hover {
                background: #B91C1C !important;
                color: white !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="logout-zone"></div>', unsafe_allow_html=True)
        if st.button("Se déconnecter", use_container_width=True, key="sidebar_logout_btn"):
            st.session_state.clear()
            st.rerun()
@st.dialog(tr("add_precision", st.session_state.get("agent1_language", "fr")))
def render_missing_precision_dialog(item_text, idx, lang="fr", on_followup_submit=None):
    st.markdown(f"### {item_text}")
    st.caption(tr("add_precision_caption", lang))

    user_txt = st.text_area(
        tr("your_answer", lang),
        key=f"missing_dialog_text_{idx}",
        placeholder=tr("precision_example_placeholder", lang),
        height=120,
    )

    col1, col2 = st.columns(2)

    with col1:
        if st.button(tr("validate", lang), key=f"missing_dialog_validate_{idx}", use_container_width=True):
            if user_txt and user_txt.strip():

                st.session_state.agent1_conversation.append({
                    "type": "followup",
                    "content": f"{item_text} : {user_txt.strip()}"
                })

                item_key = f"missing::{item_text}"

                if "agent1_ignored_items" not in st.session_state:
                    st.session_state.agent1_ignored_items = []

                if item_key not in st.session_state.agent1_ignored_items:
                    st.session_state.agent1_ignored_items.append(item_key)
                if "agent1_completed_items" not in st.session_state:
                    st.session_state.agent1_completed_items = []

                if item_key not in st.session_state.agent1_completed_items:
                    st.session_state.agent1_completed_items.append(item_key)

                st.session_state.agent1_initial_missing = [
                    m for m in st.session_state.get("agent1_initial_missing", [])
                    if str(m).strip().lower() != str(item_text).strip().lower()
                ]

                st.session_state.rh_active_input = None

                if callable(on_followup_submit):
                    on_followup_submit(lang)

                st.rerun()

    with col2:
        if st.button(tr("cancel", lang), key=f"missing_dialog_cancel_{idx}", use_container_width=True):
            st.session_state.rh_active_input = None
            st.rerun()

def render_rh_analysis_page(lang: str = "fr", on_followup_submit=None):
    if "agent1_ignored_items" not in st.session_state:
        st.session_state.agent1_ignored_items = []

    result = st.session_state.get("agent1_result")
    if not result:
        st.markdown(tr("no_analysis_available", lang))
        return

    informations_manquantes = result.get("informations_manquantes", []) or []
    termes_flous = result.get("termes_flous", []) or []

    if "agent1_total_rh_items" not in st.session_state:
        st.session_state.agent1_total_rh_items = (
            len(informations_manquantes) + len(termes_flous)
        )

    total_items = st.session_state.agent1_total_rh_items

    if "agent1_completed_items" not in st.session_state:
         st.session_state.agent1_completed_items = []

    completed = len(
     st.session_state.agent1_completed_items
    )

    remaining_items = max(total_items - completed, 0)

    ignored = set(map(str, st.session_state.agent1_ignored_items or []))

    visible_missing = [
        info for info in informations_manquantes
        if f"missing::{str(info)}" not in ignored
    ]

    visible_fuzzy = [
        item for item in termes_flous
        if f"fuzzy::{item.get('terme', '')}" not in ignored
    ]

    
    hero_html = f"""
    <style>
    .rh-hero-card {{
        background:#fff;
        border-radius:28px;
        padding:34px 42px;
        border:1px solid #E5EAF3;
        box-shadow:0 12px 34px rgba(15,23,42,.10);
        margin-bottom:34px;
        font-family: Arial, sans-serif;
    }}
    .rh-hero-grid {{
        display:grid;
        grid-template-columns:1fr 130px;
        gap:28px;
        align-items:center;
    }}
    .rh-hero-title {{
        font-size:32px;
        font-weight:900;
        color:#061837;
        margin-bottom:10px;
    }}
    .rh-hero-subtitle {{
        font-size:18px;
        color:#536987;
    }}
    .rh-progress-wrapper {{
    position: relative;
    width: 120px;
    height: 120px;
    margin: auto;
    }}

    .rh-progress-svg {{
        transform: rotate(-90deg);
    }}

    .rh-progress-bg {{
        fill: none;
        stroke: #EEF2F7;
        stroke-width: 10;
    }}

    .rh-progress-bar {{
        fill: none;
        stroke: #16337A;
        stroke-width: 10;
        stroke-linecap: round;
        transition: stroke-dashoffset 0.7s ease;
    }}

    .rh-progress-text {{
        position: absolute;
        inset: 0;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size: 30px;
        font-weight: 900;
        color:#061837;
    }}
    .rh-progress-label {{
        text-align:center;
        color:#64748B;
        font-size:14px;
        margin-top:10px;
    }}
    .rh-stat-row {{
        border-top:1px solid #E5EAF3;
        margin-top:28px;
        padding-top:26px;
        display:grid;
        grid-template-columns:repeat(3,1fr);
        gap:26px;
    }}
    .rh-stat {{
        display:flex;
        align-items:center;
        gap:14px;
    }}
    .rh-stat-icon {{
        width:56px;
        height:56px;
        border-radius:16px;
        display:flex;
        align-items:center;
        justify-content:center;
        font-size:22px;
        font-weight:900;
    }}
    .rh-red {{ background:#FFE1E5;color:#F00012; }}
    .rh-yellow {{ background:#FFF2C8;color:#EA8A00; }}
    .rh-green {{ background:#D9FBE6;color:#069B4F; }}
    .rh-stat-value {{
        font-size:28px;
        font-weight:900;
        color:#061837;
    }}
    .rh-stat-label {{
        color:#536987;
        font-size:15px;
    }}
    </style>

    <div class="rh-hero-card">
        <div class="rh-hero-grid">
            <div>
                <div class="rh-hero-title">{tr("refine_talent_search", lang)}</div>
                <div class="rh-hero-subtitle">
                   {tr("matching_opportunities", lang).format(total_items=total_items)}
                </div>
            </div>
            <div>
                <div class="rh-progress-wrapper">
                    <svg class="rh-progress-svg" width="120" height="120">
                        <circle
                            class="rh-progress-bg"
                            cx="60"
                            cy="60"
                            r="48"
                        ></circle>

                        <circle
                            class="rh-progress-bar"
                            cx="60"
                            cy="60"
                            r="48"
                            style="
                                stroke-dasharray: 301.59;
                                stroke-dashoffset: {301.59 - ((completed / max(total_items,1)) * 301.59)};
                            "
                        ></circle>
                    </svg>

                    <div class="rh-progress-text">
                        {completed}/{total_items}
                    </div>
                </div>
                <div class="rh-progress-label">{tr("completed", lang)}</div>
            </div>
        </div>

        <div class="rh-stat-row">
            <div class="rh-stat">
                <div class="rh-stat-icon rh-red">!</div>
                <div>
                    <div class="rh-stat-value">{len(visible_missing)}</div>
                    <div class="rh-stat-label">{tr("missing_info_short", lang)}</div>
                </div>
            </div>

            <div class="rh-stat">
                <div class="rh-stat-icon rh-yellow">?</div>
                <div>
                    <div class="rh-stat-value">{len(visible_fuzzy)}</div>
                    <div class="rh-stat-label">{tr("unclear_terms", lang)}</div>
                </div>
            </div>

            <div class="rh-stat">
                <div class="rh-stat-icon rh-green">✓</div>
                <div>
                    <div class="rh-stat-value">{completed}</div>
                    <div class="rh-stat-label">{tr("completed_plural", lang)}</div>
                </div>
            </div>
        </div>
    </div>
    """

    components.html(hero_html, height=360)
    st.markdown(
        """
        <style>
            .rh-section-heading {
                display:flex;
                align-items:center;
                gap:10px;
                font-size:1.25rem;
                font-weight:900;
                color:#061837;
                margin:28px 0 18px;
            }

            .rh-card {
                background:#fff;
                border-radius:24px;
                padding:28px 30px;
                margin-bottom:14px;
            }

            .rh-card-missing {
                border:2px solid #FFC3C8;
                box-shadow:0 10px 26px rgba(240,0,18,.08);
            }

            .rh-card-fuzzy {
                border:2px solid #FFDCA3;
                box-shadow:0 10px 26px rgba(234,138,0,.08);
            }

            .rh-card-layout {
                display:grid;
                grid-template-columns:58px 1fr;
                gap:18px;
                align-items:start;
            }

            .rh-stat-icon {
                width:56px;
                height:56px;
                border-radius:16px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-size:1.3rem;
                font-weight:900;
            }

            .rh-red { background:#FFE1E5;color:#F00012; }
            .rh-yellow { background:#FFF2C8;color:#EA8A00; }

            .rh-card-title {
                font-size:1.15rem;
                font-weight:900;
                color:#061837;
                margin-bottom:8px;
            }

            .rh-card-tip {
                color:#536987;
                font-size:.98rem;
            }

            div.stButton > button {
                border-radius:14px !important;
                font-weight:800 !important;
                min-height:48px !important;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )
    def ignore_item(item_key: str):
        if item_key not in st.session_state.agent1_ignored_items:
            st.session_state.agent1_ignored_items.append(item_key)

    st.markdown(
    f'<div class="rh-section-heading"><span style="color:#F00012">!</span> {tr("missing_information", lang)}</div>',
    unsafe_allow_html=True,
)

    if not visible_missing:
        st.markdown(
            """
            <div class="rh-empty-state rh-empty-success">
                ✓ {tr("all_important_info_completed", lang)}
            </div>
            """,
            unsafe_allow_html=True,
        )

    for idx, info in enumerate(visible_missing):
        item_text = str(info)
        item_key = f"missing::{item_text}"

        st.markdown(
            f"""
            <div class="rh-card rh-card-missing">
                <div class="rh-card-layout">
                    <div class="rh-stat-icon rh-red">!</div>
                    <div>
                        <div class="rh-card-title">{item_text}</div>
                        <div class="rh-card-tip">
                            {tr("missing_card_description", lang)}
                        </div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button( tr("add_precision", lang), key=f"rh_missing_precise_{idx}", use_container_width=True):
                render_missing_precision_dialog(item_text, f"missing_{idx}", lang, on_followup_submit)
            
        with c2:
            if st.button(tr("ignore", lang), key=f"rh_missing_ignore_{idx}", use_container_width=True):
                ignore_item(item_key)

                if "agent1_completed_items" not in st.session_state:
                    st.session_state.agent1_completed_items = []

                if item_key not in st.session_state.agent1_completed_items:
                    st.session_state.agent1_completed_items.append(item_key)

                st.rerun()

    st.markdown(
        f'<div class="rh-section-heading"><span style="color:#EA8A00">?</span> {tr("clarification_points", lang)}</div>',
        unsafe_allow_html=True,
    )

    for idx, item in enumerate(visible_fuzzy):
        terme = item.get("terme", "")
        contexte = item.get("pourquoi_c_est_flou", "") or item.get("contexte", "") or "—"
        item_key = f"fuzzy::{terme}"

        st.markdown(
            f"""
            <div class="rh-card rh-card-fuzzy">
                <div class="rh-card-layout">
                    <div class="rh-stat-icon rh-yellow">?</div>
                    <div>
                        <div class="rh-card-title">"{terme}"</div>
                        <div class="rh-card-tip">{contexte}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        c1, c2 = st.columns([5, 1])
        with c1:
            if st.button(tr("clarify", lang), key=f"rh_fuzzy_precise_{idx}", use_container_width=True):
                render_missing_precision_dialog(
                    f"{tr('unclear_term_prefix', lang)} : {terme}",
                    f"fuzzy_{idx}",
                    lang,
                    on_followup_submit,
                )

        with c2:
            if st.button(tr("ignore", lang), key=f"rh_fuzzy_ignore_{idx}", use_container_width=True):
                ignore_item(item_key)

                if "agent1_completed_items" not in st.session_state:
                    st.session_state.agent1_completed_items = []

                if item_key not in st.session_state.agent1_completed_items:
                    st.session_state.agent1_completed_items.append(item_key)

                st.rerun()