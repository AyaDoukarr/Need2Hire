import re
import streamlit as st


AXA_EMAIL_PATTERN = r"^[a-zA-ZÀ-ÿ0-9'-]+(\.[a-zA-ZÀ-ÿ0-9'-]+)+(\.external)?@axa\.com$"

def is_valid_axa_email(email: str) -> bool:
    email = (email or "").strip().lower()
    return re.match(AXA_EMAIL_PATTERN, email) is not None


def render_login():
    if "is_authenticated" not in st.session_state:
        st.session_state.is_authenticated = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""

    if st.session_state.is_authenticated:
        return True

    _, center, _ = st.columns([1, 1.35, 1])

    with center:
        st.markdown("""
        <div class="login-wrapper">
            <div class="login-badge">ACCÈS PROTOTYPE SÉCURISÉ</div>
            <div class="login-title">Need2Hire</div>
            <div class="login-subtitle">
                Assistant IA de qualification du besoin de recrutement. Accès réservé aux utilisateurs disposant d'une adresse professionnelle AXA.
            </div>
            <hr class="login-separator">
        """, unsafe_allow_html=True)

        email = st.text_input("Adresse professionnelle")
        st.caption("Exemple attendu : adresse se terminant par @axa.com")

        if st.button("Accéder au prototype", use_container_width=True):
            if is_valid_axa_email(email):
                st.session_state.is_authenticated = True
                st.session_state.user_email = email.strip().lower()
                st.rerun()
            else:
                st.error("Accès refusé. Veuillez utiliser une adresse professionnelle AXA.")

        st.markdown("</div>", unsafe_allow_html=True)

    return False

def render_logout():
    if not st.session_state.get("is_authenticated"):
        return

    with st.sidebar:
        st.markdown("""
        <div class="sidebar-brand">
            <div class="sidebar-logo">SQORUS</div>
            <div class="sidebar-title">Démonstrateur IA RH</div>
        </div>

        <div class="sidebar-section-title">Configuration</div>
        <div class="sidebar-line"><b>Modèle texte :</b> llama-3.1-8b-instant</div>
        <div class="sidebar-line"><b>Modèle audio :</b> whisper-large-v3-turbo</div>
        <div class="sidebar-line"><b>Provider :</b> Groq</div>

        

        <div class="sidebar-section-title">Message clé</div>
        <div class="sidebar-message">
            Ces prototypes ne remplacent pas la décision RH. Ils aident à structurer,
            expliciter et sécuriser les décisions de recrutement.
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        st.caption(f"Connecté : {st.session_state.get('user_email')}")

        if st.button("Se déconnecter", use_container_width=True):
            st.session_state.is_authenticated = False
            st.session_state.user_email = ""
            st.rerun()