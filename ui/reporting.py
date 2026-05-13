import urllib.parse

from validation.validation import build_display_result
from domain.scoring import build_quality_checklist, build_screening_recommendations, score_color


TXT = {
    "fr": {
        "report_title": "Rapport - Qualification du besoin de recrutement",
        "job_family": "Famille métier AXA",
        "job_subfamily": "Sous-famille métier",
        "source_maturity": "Nature du texte source détectée",
        "need": "Besoin consolidé analysé",
        "summary": "Résumé du besoin",
        "score_title": "Score d'exploitabilité recrutement",
        "global_score": "Score global",
        "maturity": "Niveau de maturité",
        "decision": "Décision",
        "confidence": "Indice de fiabilité de l'analyse",
        "level": "Niveau",
        "comment": "Commentaire",
        "kpi": "KPI détaillés",
        "purpose": "Utilité",
        "job_sheet": "Fiche de poste AXA consolidée",
        "title": "Intitulé",
        "contract": "Contrat",
        "experience": "Expérience",
        "location": "Localisation",
        "missions": "Missions",
        "profile": "Profil",
        "why_join": "Pourquoi nous rejoindre ?",
        "work_env": "Votre environnement de travail",
        "clarification": "Questions de clarification",
        "checklist": "Checklist qualité",
        "missing": "Informations manquantes",
        "risks": "Risques priorisés",
        "criteria": "Critères d'évaluation",
        "interview": "Questions d'entretien",
        "screening_reco": "Recommandations pour le screening",
        "none": "Aucune",
        "no_blocking": "Aucun point bloquant",
        "to_define": "À préciser",
        "email_subject": "Objet : Brief recrutement",
        "hello": "Bonjour,",
        "email_intro": "Suite à la qualification du besoin, voici le brief structuré pour ce poste.",
        "role": "POSTE",
        "main_missions": "MISSIONS PRINCIPALES",
        "required_profile": "PROFIL RECHERCHÉ",
        "screening_criteria": "CRITÈRES DE SCREENING",
        "key_questions": "QUESTIONS CLÉS POUR L'ENTRETIEN",
        "attention": "POINTS D'ATTENTION",
        "hr_level": "NIVEAU D'EXPLOITABILITÉ RH",
        "company": "Société",
        "family": "Famille métier",
        "bye": "Cordialement,\n[Votre nom]",
        "meeting_subject": "Brief recrutement",
        "meeting_suffix": "Réunion de cadrage (30 min)",
        "points_to_clarify": "POINTS À CLARIFIER AVEC LE MANAGER",
        "duration": "Durée suggérée : 30 minutes",
        "confirm": "Merci de confirmer votre disponibilité.",
    },
    "en": {
        "report_title": "Report - Recruitment need qualification",
        "job_family": "AXA job family",
        "job_subfamily": "Job subfamily",
        "source_maturity": "Detected source text maturity",
        "need": "Consolidated need analyzed",
        "summary": "Need summary",
        "score_title": "Recruitment readiness score",
        "global_score": "Global score",
        "maturity": "Maturity level",
        "decision": "Decision",
        "confidence": "Analysis reliability score",
        "level": "Level",
        "comment": "Comment",
        "kpi": "Detailed KPIs",
        "purpose": "Purpose",
        "job_sheet": "Consolidated AXA job description",
        "title": "Job title",
        "contract": "Contract",
        "experience": "Experience",
        "location": "Location",
        "missions": "Responsibilities",
        "profile": "Profile",
        "why_join": "Why join us?",
        "work_env": "Work environment",
        "clarification": "Clarification questions",
        "checklist": "Quality checklist",
        "missing": "Missing information",
        "risks": "Prioritized risks",
        "criteria": "Evaluation criteria",
        "interview": "Interview questions",
        "screening_reco": "Screening recommendations",
        "none": "None",
        "no_blocking": "No blocking point",
        "to_define": "To be defined",
        "email_subject": "Subject: Recruitment brief",
        "hello": "Hello,",
        "email_intro": "Following the qualification of the need, here is the structured brief for this role.",
        "role": "ROLE",
        "main_missions": "MAIN RESPONSIBILITIES",
        "required_profile": "REQUIRED PROFILE",
        "screening_criteria": "SCREENING CRITERIA",
        "key_questions": "KEY INTERVIEW QUESTIONS",
        "attention": "POINTS OF ATTENTION",
        "hr_level": "HR READINESS LEVEL",
        "company": "Company",
        "family": "Job family",
        "bye": "Best regards,\n[Your name]",
        "meeting_subject": "Recruitment brief",
        "meeting_suffix": "Scoping meeting (30 min)",
        "points_to_clarify": "POINTS TO CLARIFY WITH THE MANAGER",
        "duration": "Suggested duration: 30 minutes",
        "confirm": "Please confirm your availability.",
    },
    "es": {
        "report_title": "Informe - Cualificación de la necesidad de contratación",
        "job_family": "Familia profesional AXA",
        "job_subfamily": "Subfamilia profesional",
        "source_maturity": "Madurez detectada del texto fuente",
        "need": "Necesidad consolidada analizada",
        "summary": "Resumen de la necesidad",
        "score_title": "Puntuación de explotabilidad de reclutamiento",
        "global_score": "Puntuación global",
        "maturity": "Nivel de madurez",
        "decision": "Decisión",
        "confidence": "Índice de fiabilidad del análisis",
        "level": "Nivel",
        "comment": "Comentario",
        "kpi": "KPI detallados",
        "purpose": "Utilidad",
        "job_sheet": "Descripción de puesto AXA consolidada",
        "title": "Título",
        "contract": "Contrato",
        "experience": "Experiencia",
        "location": "Ubicación",
        "missions": "Responsabilidades",
        "profile": "Perfil",
        "why_join": "¿Por qué unirse a nosotros?",
        "work_env": "Entorno de trabajo",
        "clarification": "Preguntas de aclaración",
        "checklist": "Checklist de calidad",
        "missing": "Información faltante",
        "risks": "Riesgos priorizados",
        "criteria": "Criterios de evaluación",
        "interview": "Preguntas de entrevista",
        "screening_reco": "Recomendaciones para el screening",
        "none": "Ninguna",
        "no_blocking": "Ningún punto bloqueante",
        "to_define": "Por definir",
        "email_subject": "Asunto: Brief de reclutamiento",
        "hello": "Hola,",
        "email_intro": "Tras la cualificación de la necesidad, aquí está el brief estructurado para este puesto.",
        "role": "PUESTO",
        "main_missions": "RESPONSABILIDADES PRINCIPALES",
        "required_profile": "PERFIL REQUERIDO",
        "screening_criteria": "CRITERIOS DE SCREENING",
        "key_questions": "PREGUNTAS CLAVE DE ENTREVISTA",
        "attention": "PUNTOS DE ATENCIÓN",
        "hr_level": "NIVEL DE EXPLOTABILIDAD RH",
        "company": "Empresa",
        "family": "Familia profesional",
        "bye": "Saludos,\n[Tu nombre]",
        "meeting_subject": "Brief de reclutamiento",
        "meeting_suffix": "Reunión de encuadre (30 min)",
        "points_to_clarify": "PUNTOS A ACLARAR CON EL MANAGER",
        "duration": "Duración sugerida: 30 minutos",
        "confirm": "Gracias por confirmar tu disponibilidad.",
    },
}


def get_txt(lang: str):
    return TXT.get(lang, TXT["fr"])


def generate_qualification_report_markdown(
    source_text,
    job_family,
    job_subfamily,
    result,
    computed_score,
    confidence,
    prioritized_risks,
    lang="fr",
):
    t = get_txt(lang)

    fiche = result.get("fiche_de_poste_axa", {})
    display_fiche = build_display_result(result).get("fiche_de_poste_axa", {})
    checklist = build_quality_checklist(result, computed_score, lang)

    lines = [
        f"# {t['report_title']}",
        "",
        f"**{t['job_family']}** : {job_family}",
        f"**{t['job_subfamily']}** : {job_subfamily}",
        f"**{t['source_maturity']}** : {computed_score.get('source_maturity', '—')}",
        "",
        f"## 1. {t['need']}",
        source_text,
        "",
        f"## 2. {t['summary']}",
        result.get("resume_besoin", "—"),
        "",
        f"## 3. {t['score_title']}",
        f"- {t['global_score']} : {computed_score['score_global']}/100",
        f"- {t['maturity']} : {computed_score['niveau_maturite']}",
        f"- {t['decision']} : {computed_score['decision']}",
        "",
        f"## 4. {t['confidence']}",
        f"- {t['global_score']} : {confidence['score']}/100",
        f"- {t['level']} : {confidence['level']}",
        f"- {t['comment']} : {confidence['comment']}",
        "",
        f"## 5. {t['kpi']}",
    ]

    for d in computed_score["details"]:
        lines.append(f"- {d['dimension']} : {d['score']}/{d['sur']}")
        lines.append(f"  - {t['purpose']} : {d.get('purpose', '—')}")
        lines.append(f"  - {t['comment']} : {d['commentaire']}")
        for step in d.get("formule", []):
            lines.append(f"  - {step}")

    lines.extend([
        "",
        f"## 6. {t['job_sheet']}",
        f"- {t['title']} : {fiche.get('intitule_poste', '—')}",
        f"- {t['contract']} : {fiche.get('type_contrat', '—')}",
        f"- {t['experience']} : {fiche.get('niveau_experience', '—')}",
        f"- {t['location']} : {fiche.get('localisation', '—')}",
        "",
        f"### {t['missions']}",
    ])

    for m in fiche.get("votre_role_et_vos_missions", []):
        lines.append(f"- {m}")

    lines.append(f"### {t['profile']}")
    for p in fiche.get("votre_profil", []):
        lines.append(f"- {p}")

    lines.extend(["", f"### {t['why_join']}"])
    for p in display_fiche.get("pourquoi_nous_rejoindre", []):
        lines.append(f"- {p}")

    lines.extend(["", f"### {t['work_env']}"])
    for e in display_fiche.get("votre_environnement_de_travail", []):
        lines.append(f"- {e}")

    lines.extend(["", f"## 7. {t['clarification']}"])
    for q in result.get("questions_de_clarification", []) or [t["none"]]:
        lines.append(f"- {q}")

    lines.extend(["", f"## 8. {t['checklist']}"])
    for item in checklist:
        lines.append(f"- {item['critere']} : {item['statut']} — {item['commentaire']}")

    lines.extend(["", f"## 9. {t['missing']}"])
    for info in result.get("informations_manquantes", []) or [t["none"]]:
        lines.append(f"- {info}")

    lines.extend(["", f"## 10. {t['risks']}"])
    for section, risks in prioritized_risks.items():
        lines.append(f"### {section}")
        if risks:
            for r in risks:
                lines.append(f"- {r.get('risque', '—')} — {r.get('explication', '—')}")
        else:
            lines.append(f"- {t['none']}")

    lines.extend(["", f"## 11. {t['criteria']}"])
    criteres = result.get("criteres_d_evaluation", [])
    if criteres:
        for c in criteres:
            lines.append(f"- {c.get('critere', '—')} : {c.get('objectif', '—')}")
    else:
        lines.append(f"- {t['none']}")

    lines.extend(["", f"## 12. {t['interview']}"])
    for q in result.get("questions_entretien", []) or [t["none"]]:
        lines.append(f"- {q}")

    lines.extend(["", f"## 13. {t['screening_reco']}"])
    for r in build_screening_recommendations(result, lang):
        lines.append(f"- {r}")

    return "\n".join(lines)


def generate_recruiter_brief_email(job_family, job_subfamily, result, computed_score, lang="fr"):
    t = get_txt(lang)

    fiche = result.get("fiche_de_poste_axa", {})
    missions = fiche.get("votre_role_et_vos_missions", [])[:4]
    profil = fiche.get("votre_profil", [])[:4]
    criteres = result.get("criteres_d_evaluation", [])[:3]
    questions = result.get("questions_entretien", [])[:3]
    infos_manquantes = result.get("informations_manquantes", [])[:3]

    missions_txt = "\n".join(f"  • {m}" for m in missions) or f"  • {t['to_define']}"
    profil_txt = "\n".join(f"  • {p}" for p in profil) or f"  • {t['to_define']}"
    criteres_txt = "\n".join(
        f"  • {c.get('critere', '—')} : {c.get('objectif', '—')}" for c in criteres
    ) or f"  • {t['to_define']}"
    questions_txt = "\n".join(f"  • {q}" for q in questions) or f"  • {t['to_define']}"
    manquants_txt = "\n".join(f"  • {i}" for i in infos_manquantes) if infos_manquantes else f"  • {t['no_blocking']}"

    return f"""{t['email_subject']} — {fiche.get('intitule_poste', '—')} | {job_family}

{t['hello']}

{t['email_intro']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['role']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['title']}       : {fiche.get('intitule_poste', '—')}
{t['contract']}    : {fiche.get('type_contrat', '—')}
{t['experience']}  : {fiche.get('niveau_experience', '—')}
{t['location']}    : {fiche.get('localisation', '—')}
{t['family']}      : {job_family} > {job_subfamily}
{t['company']}     : {fiche.get('societe_du_groupe', '—')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['main_missions']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{missions_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['required_profile']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{profil_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['screening_criteria']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{criteres_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['key_questions']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{questions_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['attention']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{manquants_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['hr_level']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['global_score']} : {computed_score['score_global']}/100 {score_color(computed_score['score_global'])}
{t['decision']}     : {computed_score['decision']}

{t['bye']}""".strip()


def generate_outlook_meeting_link(intitule, brief_email, questions_clarification, lang="fr"):
    t = get_txt(lang)

    subject = f"{t['meeting_subject']} — {intitule} | {t['meeting_suffix']}"
    questions_txt = "\n".join(f"  • {q}" for q in questions_clarification) if questions_clarification else f"  • {t['none']}"

    body = f"""{brief_email}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{t['points_to_clarify']}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{questions_txt}

{t['duration']}

{t['confirm']}
[Votre nom]"""

    return f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"