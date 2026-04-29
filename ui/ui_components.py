import uuid
import streamlit as st
import streamlit.components.v1 as components

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
                    <div class="flip-hint">Clique pour voir le détail</div>
                </div>

                <div class="flip-face flip-back">
                    <div class="flip-back-title">Détail</div>
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

        st.markdown(f"**{tr('business_comment', lang)}**")
        st.write(commentaire)


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
            <div><div class="fiche-meta-key">Référence</div><div class="fiche-meta-val">{fiche.get('reference_offre','—')}</div></div>
            <div><div class="fiche-meta-key">Expérience</div><div class="fiche-meta-val">{fiche.get('niveau_experience','—')}</div></div>
            <div><div class="fiche-meta-key">Famille métier</div><div class="fiche-meta-val">{fiche.get('famille_metier','—')}</div></div>
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


def render_risks(prioritized_risks):
    for section in ["Bloquant", "Important", "Amélioration"]:
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
                        <span class="{css}">{section}</span>
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
                    st.markdown(f"**Exemples de postes** : {row.get('exemples_postes', '—')}")
                    st.markdown(f"**Mots-clés métier** : {row.get('mots_cles', '—')}")

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
):
    fiche = display_result.get("fiche_de_poste_axa", {})

    col1, col2, col3 = st.columns(3)

    with col1:
        render_flip_card(
            title=tr("score_expl", lang),
            score=computed_score["score_global"],
            max_score=100,
            badge_text=computed_score["niveau_maturite"],
            details=[
                "Cette carte mesure la qualité globale du besoin de recrutement.",
                f"Niveau actuel : {computed_score['niveau_maturite']}",
                "Elle s'appuie sur les 5 KPI métier : complétude, précision, screening, missions et structure AXA."
            ]
        )

    with col2:
        render_flip_card(
            title=tr("confidence_score", lang),
            score=confidence["score"],
            max_score=100,
            badge_text=confidence["level"],
            details=[
                "Cette carte mesure le niveau de confiance que l’on peut avoir dans l’analyse.",
                f"Niveau actuel : {confidence['level']}",
                "Elle augmente quand le besoin contient peu de zones floues, peu d’informations manquantes et une structure claire."
            ]
        )

    with col3:
        render_flip_card(
            title=tr("decision", lang),
            score=computed_score["decision"],
            max_score="",
            badge_text=tr("go", lang) if tr("ready_to_publish", lang) in computed_score["decision"] else computed_score["decision"],
            is_decision=True,
            details=[
                f"Décision actuelle : {computed_score['decision']}",
                "Cette carte sert à donner l’action RH à prendre sur le brief.",
                "Plus le besoin est clair, structuré et exploitable, plus la décision est positive."
            ]
        )

    st.markdown(f'<div class="small-note"><strong>{tr("score_note", lang)}</strong></div>', unsafe_allow_html=True)

    render_section_title(tr("executive_summary", lang))
    st.markdown(f'<div class="info-box">{raw_result.get("resume_besoin", "—")}</div>', unsafe_allow_html=True)

    render_section_title(tr("detailed_score", lang))
    st.caption(tr("click_kpi_caption", lang))
    for d in computed_score["details"]:
        render_clickable_score_bar(d, lang)

    if computed_score.get("recommandations"):
        st.markdown(
            '<div class="warn-box"><strong>' + tr("recommendations", lang) + ' :</strong><br>' +
            "<br>".join(f"• {r}" for r in computed_score["recommandations"]) +
            '</div>',
            unsafe_allow_html=True
        )

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        tr("job_sheet", lang),
        tr("hr_analysis", lang),
        tr("checklist_screening", lang),
        tr("brief_meeting", lang),
        tr("reference_history", lang)
    ])

    with tab1:
        render_fiche_poste(fiche, lang)

    with tab2:
        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"#### {tr('fuzzy_terms', lang)}")
            termes_flous = raw_result.get("termes_flous", [])
            if termes_flous:
                for item in termes_flous:
                    st.markdown(
                        f"""
                        <div class="axa-card axa-card-warn" style="padding:12px 16px;margin-bottom:8px">
                          <div style="font-weight:600;font-size:0.88rem">"{item.get('terme','—')}"</div>
                          <div style="font-size:0.8rem;color:var(--axa-muted);margin-top:3px">{item.get('pourquoi_c_est_flou','—')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f'<div class="empty-state">{tr("no_fuzzy_terms", lang)}</div>', unsafe_allow_html=True)

            st.markdown(f"#### {tr('missing_info', lang)}")
            infos = raw_result.get("informations_manquantes", [])
            if infos:
                for info in infos:
                    st.markdown(
                        f'<div class="axa-card axa-card-red" style="padding:10px 16px;margin-bottom:6px;font-size:0.88rem">{info}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f'<div class="empty-state">{tr("no_missing_info", lang)}</div>', unsafe_allow_html=True)

            st.markdown(f"#### {tr('clarification_questions', lang)}")
            questions = raw_result.get("questions_de_clarification", [])
            if questions:
                for i, q in enumerate(questions, 1):
                    st.markdown(
                        f'<div class="axa-card axa-card-accent" style="padding:10px 16px;margin-bottom:6px;font-size:0.88rem"><span style="color:var(--axa-blue);font-weight:700">{i}.</span> {q}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f'<div class="empty-state">{tr("no_clarification_questions", lang)}</div>', unsafe_allow_html=True)

        with col_right:
            st.markdown(f"#### {tr('prioritized_risks', lang)}")
            render_risks(prioritized_risks_data)

            st.markdown(f"#### {tr('evaluation_criteria', lang)}")
            criteres = raw_result.get("criteres_d_evaluation", [])
            if criteres:
                for crit in criteres:
                    st.markdown(
                        f"""
                        <div class="axa-card" style="padding:12px 16px;margin-bottom:8px">
                          <div style="font-weight:600;font-size:0.88rem;color:var(--axa-navy)">{crit.get('critere','—')}</div>
                          <div style="font-size:0.8rem;color:var(--axa-muted);margin-top:3px">{crit.get('objectif','—')}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f'<div class="empty-state">{tr("no_criteria", lang)}</div>', unsafe_allow_html=True)

            st.markdown(f"#### {tr('interview_questions', lang)}")
            questions_entretien = raw_result.get("questions_entretien", [])
            if questions_entretien:
                for i, q in enumerate(questions_entretien, 1):
                    st.markdown(
                        f'<div class="axa-card" style="padding:10px 16px;margin-bottom:6px;font-size:0.88rem"><span style="color:var(--axa-blue);font-weight:700">{i}.</span> {q}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown(f'<div class="empty-state">{tr("no_interview_questions", lang)}</div>', unsafe_allow_html=True)

        # MARKET BENCHMARK
        st.markdown(f"#### {tr('market_benchmark', lang)}")
        
        if market_benchmark:
            # Helper to map values to CSS classes and labels
            def get_exigence_style(value):
                if value == "too demanding":
                    return "axa-card-warn", tr("too_demanding", lang)
                elif value == "balanced":
                    return "axa-card-green", tr("balanced", lang)
                else:
                    return "axa-card-accent", tr("not_demanding_enough", lang)

            def get_precision_style(value):
                if value == "too vague":
                    return "axa-card-warn", tr("too_vague", lang)
                elif value == "correct":
                    return "axa-card-green", tr("correct", lang)
                else:
                    return "axa-card-accent", tr("very_precise", lang)

            def get_attractivite_style(value):
                if value == "low":
                    return "axa-card-warn", tr("low", lang)
                elif value == "medium":
                    return "axa-card-accent", tr("medium", lang)
                else:
                    return "axa-card-green", tr("high", lang)

            def get_alignement_style(value):
                if value == "low":
                    return "axa-card-warn", tr("low", lang)
                elif value == "medium":
                    return "axa-card-accent", tr("medium", lang)
                else:
                    return "axa-card-green", tr("high", lang)

            # Display the 4 main metrics
            col_bm1, col_bm2, col_bm3, col_bm4 = st.columns(4)

            with col_bm1:
                cls, lbl = get_exigence_style(market_benchmark.get("niveau_exigence", ""))
                st.markdown(
                    f'<div class="axa-card {cls}" style="padding:12px 16px;text-align:center">'
                    f'<div style="font-size:0.72rem;color:var(--axa-muted)">{tr("niveau_exigence", lang)}</div>'
                    f'<div style="font-weight:700;font-size:0.9rem">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col_bm2:
                cls, lbl = get_precision_style(market_benchmark.get("niveau_precision", ""))
                st.markdown(
                    f'<div class="axa-card {cls}" style="padding:12px 16px;text-align:center">'
                    f'<div style="font-size:0.72rem;color:var(--axa-muted)">{tr("niveau_precision", lang)}</div>'
                    f'<div style="font-weight:700;font-size:0.9rem">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col_bm3:
                cls, lbl = get_attractivite_style(market_benchmark.get("attractivite_poste", ""))
                st.markdown(
                    f'<div class="axa-card {cls}" style="padding:12px 16px;text-align:center">'
                    f'<div style="font-size:0.72rem;color:var(--axa-muted)">{tr("attractivite_poste", lang)}</div>'
                    f'<div style="font-weight:700;font-size:0.9rem">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            with col_bm4:
                cls, lbl = get_alignement_style(market_benchmark.get("alignement_marche", ""))
                st.markdown(
                    f'<div class="axa-card {cls}" style="padding:12px 16px;text-align:center">'
                    f'<div style="font-size:0.72rem;color:var(--axa-muted)">{tr("alignement_marche", lang)}</div>'
                    f'<div style="font-weight:700;font-size:0.9rem">{lbl}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

            # Market risks
            risks = market_benchmark.get("risques_marche", [])
            if risks:
                st.markdown(f"**{tr('risques_marche', lang)}**")
                for risk in risks:
                    st.markdown(
                        f'<div class="axa-card axa-card-warn" style="padding:10px 16px;margin-bottom:6px;font-size:0.88rem">• {risk}</div>',
                        unsafe_allow_html=True
                    )

            # Recommendations
            recos = market_benchmark.get("recommandations", [])
            if recos:
                st.markdown(f"**{tr('recommandations', lang)}**")
                for reco in recos:
                    st.markdown(
                        f'<div class="axa-card axa-card-green" style="padding:10px 16px;margin-bottom:6px;font-size:0.88rem">• {reco}</div>',
                        unsafe_allow_html=True
                    )

            # Conclusion
            conclusion = market_benchmark.get("conclusion", "")
            if conclusion:
                st.markdown(f"**{tr('conclusion', lang)}**")
                st.markdown(
                    f'<div class="info-box">{conclusion}</div>',
                    unsafe_allow_html=True
                )
        else:
            st.markdown(
                f'<div class="axa-card" style="padding:14px 18px;color:var(--axa-muted)">{tr("benchmark_unavailable", lang)}</div>',
                unsafe_allow_html=True
            )

    with tab3:
        st.markdown(f"#### {tr('quality_checklist', lang)}")
        render_checklist(raw_result, computed_score, lang)

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

        st.markdown(f"#### {tr('screening_reco', lang)}")
        for reco in build_screening_recommendations(raw_result, lang):
            st.markdown(
                f'<div class="axa-card axa-card-green" style="padding:12px 16px;margin-bottom:8px;font-size:0.88rem">• {reco}</div>',
                unsafe_allow_html=True
            )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(f"#### {tr('before_after', lang)}")
        col_b, col_a = st.columns(2)

        with col_b:
            st.markdown(
                f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--axa-muted);margin-bottom:8px">{tr("before", lang)}</div>',
                unsafe_allow_html=True
            )
            st.markdown(
                f'<div class="axa-card" style="font-size:0.85rem;line-height:1.7;color:var(--axa-muted)">{source_text}</div>',
                unsafe_allow_html=True
            )

        with col_a:
            st.markdown(
                f'<div style="font-size:0.72rem;font-weight:700;letter-spacing:.1em;text-transform:uppercase;color:var(--axa-muted);margin-bottom:8px">{tr("after", lang)}</div>',
                unsafe_allow_html=True
            )
            missions_html = "".join(
                f"<div style='font-size:.82rem;padding:3px 0;border-bottom:1px solid var(--axa-light)'>• {m}</div>"
                for m in fiche.get("votre_role_et_vos_missions", [])[:3]
            )
            st.markdown(
                f'<div class="axa-card axa-card-accent">'
                f'<div class="fiche-meta-key">Intitulé</div><div style="font-weight:600;margin-bottom:8px">{fiche.get("intitule_poste","—")}</div>'
                f'<div class="fiche-meta-key">Niveau</div><div style="font-weight:600;margin-bottom:8px">{fiche.get("niveau_experience","—")}</div>'
                f'<div class="fiche-meta-key">Missions ({len(fiche.get("votre_role_et_vos_missions", []))})</div>{missions_html}</div>',
                unsafe_allow_html=True
            )

    with tab4:
        st.markdown(f"#### {tr('recruiter_brief', lang)}")
        brief_email = generate_recruiter_brief_email(job_family, job_subfamily, raw_result, computed_score)
        brief_email_edited = st.text_area(
            tr("editable_before_send", lang),
            value=brief_email,
            height=420,
            key="brief_email_area"
        )
        st.download_button(
            label=tr("download_brief", lang),
            data=brief_email_edited.encode("utf-8"),
            file_name=f"brief_recruteur_{job_family.replace(' ', '_').replace('/', '').lower()}.txt",
            mime="text/plain",
            use_container_width=True,
            key="download_brief_email"
        )

        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        st.markdown(f"#### {tr('meeting_plan', lang)}")
        meeting_link = generate_outlook_meeting_link(
            fiche.get("intitule_poste", "Poste à pourvoir"),
            brief_email_edited,
            raw_result.get("questions_de_clarification", [])
        )
        st.markdown(
            f'<a href="{meeting_link}" class="outlook-btn">{tr("open_outlook", lang)}</a>',
            unsafe_allow_html=True
        )
        st.caption(tr("outlook_caption", lang))

    with tab5:
        render_taxonomy_panel(job_family, job_subfamily, lang)

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.download_button(
        label=tr("download_report", lang),
        data=render_markdown.encode("utf-8"),
        file_name="rapport_qualification_besoin_axa.md",
        mime="text/markdown",
        use_container_width=True,
        key="download_tab1_conversation"
    )


def render_invalid_input_block(message: str):
    st.markdown(f'<div class="invalid-box">{message}</div>', unsafe_allow_html=True)