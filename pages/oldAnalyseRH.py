import streamlit as st

from styles import AXA_STYLES, FLIP_CARD_STYLE
from ui.ui_components import render_rh_analysis_page
from app import run_qualification_analysis

st.set_page_config(
    page_title="Analyse RH",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(AXA_STYLES, unsafe_allow_html=True)
st.markdown(FLIP_CARD_STYLE, unsafe_allow_html=True)

lang = st.session_state.get("agent1_language", "fr")

render_rh_analysis_page(
    lang=lang,
    on_followup_submit=run_qualification_analysis,
)