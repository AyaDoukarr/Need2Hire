import urllib.parse

from validation.validation import build_display_result
from domain.scoring import build_quality_checklist, build_screening_recommendations, score_color


def generate_qualification_report_markdown(source_text, job_family, job_subfamily, result, computed_score, confidence, prioritized_risks):
    fiche = result.get("fiche_de_poste_axa", {})
    display_fiche = build_display_result(result).get("fiche_de_poste_axa", {})
    checklist = build_quality_checklist(result, computed_score)

    lines = [
        "# Rapport - Qualification du besoin de recrutement",
        "",
        f"**Famille métier AXA** : {job_family}",
        f"**Sous-famille métier** : {job_subfamily}",
        f"**Nature du texte source détectée** : {computed_score.get('source_maturity', '—')}",
        "",
        "## 1. Besoin consolidé analysé",
        source_text,
        "",
        "## 2. Résumé du besoin",
        result.get("resume_besoin", "—"),
        "",
        "## 3. Score d'exploitabilité recrutement",
        f"- Score global : {computed_score['score_global']}/100",
        f"- Niveau de maturité : {computed_score['niveau_maturite']}",
        f"- Décision : {computed_score['decision']}",
        "",
        "## 4. Indice de fiabilité de l'analyse",
        f"- Score : {confidence['score']}/100",
        f"- Niveau : {confidence['level']}",
        f"- Commentaire : {confidence['comment']}",
        "",
        "## 5. KPI détaillés",
    ]

    for d in computed_score["details"]:
        lines.append(f"- {d['dimension']} : {d['score']}/{d['sur']}")
        lines.append(f"  - Utilité : {d.get('purpose', '—')}")
        lines.append(f"  - Commentaire : {d['commentaire']}")
        for step in d.get("formule", []):
            lines.append(f"  - {step}")

    lines.extend([
        "",
        "## 6. Fiche de poste AXA consolidée",
        f"- Intitulé : {fiche.get('intitule_poste', '—')}",
        f"- Contrat : {fiche.get('type_contrat', '—')}",
        f"- Expérience : {fiche.get('niveau_experience', '—')}",
        f"- Localisation : {fiche.get('localisation', '—')}",
        "",
        "### Missions",
    ])

    for m in fiche.get("votre_role_et_vos_missions", []):
        lines.append(f"- {m}")

    lines.append("### Profil")
    for p in fiche.get("votre_profil", []):
        lines.append(f"- {p}")

    lines.extend(["", "### Pourquoi nous rejoindre ?"])
    for p in display_fiche.get("pourquoi_nous_rejoindre", []):
        lines.append(f"- {p}")

    lines.extend(["", "### Votre environnement de travail"])
    for e in display_fiche.get("votre_environnement_de_travail", []):
        lines.append(f"- {e}")

    lines.extend(["", "## 7. Questions de clarification"])
    for q in result.get("questions_de_clarification", []) or ["Aucune"]:
        lines.append(f"- {q}")

    lines.extend(["", "## 8. Checklist qualité"])
    for item in checklist:
        lines.append(f"- {item['critere']} : {item['statut']} — {item['commentaire']}")

    lines.extend(["", "## 9. Informations manquantes"])
    for info in result.get("informations_manquantes", []) or ["Aucune"]:
        lines.append(f"- {info}")

    lines.extend(["", "## 10. Risques priorisés"])
    for section, risks in prioritized_risks.items():
        lines.append(f"### {section}")
        if risks:
            for r in risks:
                lines.append(f"- {r.get('risque', '—')} — {r.get('explication', '—')}")
        else:
            lines.append("- Aucun")

    lines.extend(["", "## 11. Critères d'évaluation"])
    criteres = result.get("criteres_d_evaluation", [])
    if criteres:
        for c in criteres:
            lines.append(f"- {c.get('critere', '—')} : {c.get('objectif', '—')}")
    else:
        lines.append("- Aucun")

    lines.extend(["", "## 12. Questions d'entretien"])
    for q in result.get("questions_entretien", []) or ["Aucune"]:
        lines.append(f"- {q}")

    lines.extend(["", "## 13. Recommandations pour le screening"])
    for r in build_screening_recommendations(result):
        lines.append(f"- {r}")

    return "\n".join(lines)


def generate_recruiter_brief_email(job_family, job_subfamily, result, computed_score):
    fiche = result.get("fiche_de_poste_axa", {})
    missions = fiche.get("votre_role_et_vos_missions", [])[:4]
    profil = fiche.get("votre_profil", [])[:4]
    criteres = result.get("criteres_d_evaluation", [])[:3]
    questions = result.get("questions_entretien", [])[:3]
    infos_manquantes = result.get("informations_manquantes", [])[:3]

    missions_txt = "\n".join(f"  • {m}" for m in missions) or "  • À préciser"
    profil_txt = "\n".join(f"  • {p}" for p in profil) or "  • À préciser"
    criteres_txt = "\n".join(f"  • {c['critere']} : {c['objectif']}" for c in criteres) or "  • À préciser"
    questions_txt = "\n".join(f"  • {q}" for q in questions) or "  • À préciser"
    manquants_txt = "\n".join(f"  • {i}" for i in infos_manquantes) if infos_manquantes else "  • Aucun point bloquant"

    return f"""Objet : Brief recrutement — {fiche.get('intitule_poste', 'Poste à pourvoir')} | {job_family}

Bonjour,

Suite à la qualification du besoin, voici le brief structuré pour ce poste.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POSTE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Intitulé       : {fiche.get('intitule_poste', '—')}
Contrat        : {fiche.get('type_contrat', '—')}
Expérience     : {fiche.get('niveau_experience', '—')}
Localisation   : {fiche.get('localisation', '—')}
Famille métier : {job_family} > {job_subfamily}
Société        : {fiche.get('societe_du_groupe', '—')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MISSIONS PRINCIPALES
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{missions_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PROFIL RECHERCHÉ
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{profil_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITÈRES DE SCREENING
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{criteres_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
QUESTIONS CLÉS POUR L'ENTRETIEN
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{questions_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POINTS D'ATTENTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{manquants_txt}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NIVEAU D'EXPLOITABILITÉ RH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Score global   : {computed_score['score_global']}/100 {score_color(computed_score['score_global'])}
Décision       : {computed_score['decision']}

Cordialement,
[Votre nom]""".strip()


def generate_outlook_meeting_link(intitule, brief_email, questions_clarification):
    subject = f"Brief recrutement — {intitule} | Réunion de cadrage (30 min)"
    questions_txt = "\n".join(f"  • {q}" for q in questions_clarification) if questions_clarification else "  • Aucune question en attente"
    body = f"""{brief_email}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
POINTS À CLARIFIER AVEC LE MANAGER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
{questions_txt}

Durée suggérée : 30 minutes

Merci de confirmer votre disponibilité.
[Votre nom]"""
    return f"mailto:?subject={urllib.parse.quote(subject)}&body={urllib.parse.quote(body)}"