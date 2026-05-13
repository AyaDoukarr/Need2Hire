import re
import streamlit as st
import base64
from pathlib import Path
from ui.ui_components import render_premium_sidebar



AXA_EMAIL_PATTERN = r"^[a-zA-ZÀ-ÿ0-9'_-]+\.[a-zA-ZÀ-ÿ0-9'_-]+(\.external)?@axa\.com$"

def is_valid_axa_email(email: str) -> bool:
    email = (email or "").strip().lower()
    return re.match(AXA_EMAIL_PATTERN, email) is not None

def image_to_base64(path: str) -> str:
    img_path = Path(__file__).parent / path
    if not img_path.exists():
        st.error(f"Logo introuvable : {img_path}")
        return ""
    return base64.b64encode(img_path.read_bytes()).decode()
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

        if st.button(
            "Accéder au prototype",
            use_container_width=True,
            key="login_access_btn"
        ):
            if is_valid_axa_email(email):
                st.session_state.is_authenticated = True
                st.session_state.user_email = email.strip().lower()
                st.session_state.show_splash = True
                st.rerun()
            else:
                st.error("Accès refusé. Veuillez utiliser une adresse professionnelle AXA.")
        st.markdown("</div>", unsafe_allow_html=True)

    return False


def render_logout():
    if not st.session_state.get("is_authenticated"):
        return

    # Get user info from session
    user_email = st.session_state.get("user_email", "utilisateur@exemple.com")
    # Extract name from email for display
    user_name = user_email.split("@")[0].replace(".", " ").title()
    user_role = "RH Manager"
    
    # Render premium sidebar (function handles sidebar internally)
    render_premium_sidebar(user_name=user_name, user_role=user_role, offers_count=12)
    
    # Keep the disconnect button in main content area
    if st.button("Se déconnecter", use_container_width=True):
        st.session_state.is_authenticated = False
        st.session_state.user_email = ""
        st.rerun()