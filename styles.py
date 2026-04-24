AXA_STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

:root {
    --axa-navy:    #0F2A6B;
    --axa-blue:    #185FA5;
    --axa-red:     #D71920;
    --axa-light:   #F5F7FB;
    --axa-border:  #DDE3EF;
    --axa-text:    #1A1A3E;
    --axa-muted:   #6B7280;
    --axa-success: #0F8B4C;
    --axa-warn:    #D97706;
    --axa-danger:  #DC2626;
    --radius:      14px;
    --shadow:      0 2px 16px rgba(0,0,56,0.07);
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    color: var(--axa-text) !important;
}

.axa-hero {
    background: linear-gradient(135deg, var(--axa-navy) 0%, var(--axa-blue) 100%);
    border-radius: var(--radius);
    padding: 32px 36px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.axa-hero::before {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 200px; height: 200px;
    background: rgba(255,255,255,0.08);
    border-radius: 50%;
}
.axa-hero::after {
    content: '';
    position: absolute;
    bottom: -60px; right: 80px;
    width: 140px; height: 140px;
    background: rgba(255,255,255,0.05);
    border-radius: 50%;
}
.axa-hero-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.55);
    margin-bottom: 8px;
}
.axa-hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.85rem;
    color: #FFFFFF;
    margin: 0 0 8px 0;
    line-height: 1.2;
}
.axa-hero-sub {
    color: rgba(255,255,255,0.82);
    font-size: 0.92rem;
    max-width: 760px;
    line-height: 1.6;
}

.section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.2rem;
    color: var(--axa-navy);
    margin: 32px 0 16px 0;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--axa-red);
    display: inline-block;
}

.axa-card {
    background: #FFFFFF;
    border: 1px solid var(--axa-border);
    border-radius: var(--radius);
    padding: 20px 24px;
    margin-bottom: 16px;
    box-shadow: var(--shadow);
}
.axa-card-accent { border-left: 4px solid var(--axa-blue); }
.axa-card-red { border-left: 4px solid var(--axa-red); }
.axa-card-green { border-left: 4px solid var(--axa-success); }
.axa-card-warn { border-left: 4px solid var(--axa-warn); }

.metric-row {
    display: flex;
    gap: 16px;
    margin-bottom: 20px;
}
.metric-card {
    flex: 1;
    background: #FFFFFF;
    border: 1px solid var(--axa-border);
    border-radius: var(--radius);
    padding: 20px 24px;
    box-shadow: var(--shadow);
    text-align: center;
}
.metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    color: var(--axa-navy);
    line-height: 1;
    margin-bottom: 4px;
}
.metric-label {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--axa-muted);
}
.metric-badge {
    display: inline-block;
    margin-top: 8px;
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 0.75rem;
    font-weight: 700;
}
.badge-green  { background: #D1FAE5; color: #065F46; }
.badge-orange { background: #FEF3C7; color: #92400E; }
.badge-red    { background: #FEE2E2; color: #991B1B; }

.tag-pill {
    display: inline-block;
    background: var(--axa-light);
    color: var(--axa-blue);
    border: 1px solid var(--axa-border);
    padding: 5px 14px;
    border-radius: 99px;
    font-size: 0.8rem;
    font-weight: 600;
    margin: 3px 4px 3px 0;
}

.risk-bloquant { background:#FEE2E2; color:#991B1B; border-radius:6px; padding:2px 8px; font-size:0.75rem; font-weight:700; }
.risk-important { background:#FEF3C7; color:#92400E; border-radius:6px; padding:2px 8px; font-size:0.75rem; font-weight:700; }
.risk-amelioration { background:#D1FAE5; color:#065F46; border-radius:6px; padding:2px 8px; font-size:0.75rem; font-weight:700; }

.check-oui   { color: var(--axa-success); font-weight: 700; }
.check-non   { color: var(--axa-danger);  font-weight: 700; }
.check-partiel { color: var(--axa-warn);  font-weight: 700; }

.fiche-header {
    background: linear-gradient(135deg, var(--axa-navy) 0%, #173B86 100%);
    border-radius: var(--radius) var(--radius) 0 0;
    padding: 24px 28px;
    color: white;
}
.fiche-header-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.5rem;
    margin: 0 0 6px 0;
}
.fiche-header-meta {
    font-size: 0.82rem;
    color: rgba(255,255,255,0.7);
}
.fiche-body {
    background: #fff;
    border: 1px solid var(--axa-border);
    border-top: none;
    border-radius: 0 0 var(--radius) var(--radius);
    padding: 24px 28px;
}
.fiche-section-title {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--axa-blue);
    margin: 20px 0 8px 0;
}
.fiche-meta-grid {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 16px;
    margin: 16px 0;
}
.fiche-meta-key {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: var(--axa-muted);
    margin-bottom: 3px;
}
.fiche-meta-val {
    font-size: 0.9rem;
    font-weight: 600;
    color: var(--axa-text);
}
.mission-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 8px 0;
    border-bottom: 1px solid var(--axa-light);
}
.mission-dot {
    width: 6px; height: 6px;
    min-width: 6px;
    background: var(--axa-red);
    border-radius: 50%;
    margin-top: 7px;
}

.score-row { margin-bottom: 12px; }
.score-label {
    display: flex;
    justify-content: space-between;
    font-size: 0.9rem;
    font-weight: 700;
    margin-bottom: 6px;
}
.score-bar-track {
    height: 10px;
    background: var(--axa-light);
    border-radius: 99px;
    overflow: hidden;
}
.score-bar-fill {
    height: 100%;
    border-radius: 99px;
}

.outlook-btn {
    display: inline-flex;
    align-items: center;
    gap: 10px;
    background: var(--axa-navy);
    color: #FFFFFF !important;
    padding: 12px 24px;
    border-radius: var(--radius);
    font-size: 0.9rem;
    font-weight: 600;
    text-decoration: none !important;
    transition: background 0.2s;
    margin-top: 10px;
}
.outlook-btn:hover { background: var(--axa-blue); }

.divider {
    height: 1px;
    background: var(--axa-border);
    margin: 24px 0;
}
.empty-state {
    color: var(--axa-muted);
    font-style: italic;
    font-size: 0.88rem;
    padding: 8px 0;
}
.info-box {
    background: #EFF6FF;
    border: 1px solid #BFDBFE;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #1E40AF;
    margin: 12px 0;
}
.warn-box {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 0.88rem;
    color: #92400E;
    margin: 12px 0;
}
.small-note {
    background: #F9FAFB;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 0.82rem;
    color: #4B5563;
    margin: 10px 0 16px 0;
}
.invalid-box {
    background: #FFF1F2;
    border: 1px solid #FECDD3;
    color: #9F1239;
    border-radius: 10px;
    padding: 14px 16px;
    font-size: 0.95rem;
    font-weight: 700;
    margin: 10px 0;
}

div[data-testid="stMetric"] { display: none; }
div[data-testid="stExpander"] {
    border: 1px solid var(--axa-border) !important;
    border-radius: var(--radius) !important;
    box-shadow: none !important;
    margin-bottom: 10px !important;
}
.stDownloadButton > button {
    background: var(--axa-navy) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
    padding: 10px 20px !important;
}
.stButton > button {
    border-radius: var(--radius) !important;
    font-weight: 600 !important;
}
textarea { font-family: 'DM Sans', sans-serif !important; }

.login-wrapper {
    max-width: 720px;
    margin: 40px auto 0 auto;
    background: #F7F8FA;
    border: 1px solid #C7D9F5;
    border-radius: 16px;
    padding: 20px 24px;
}

.login-badge {
    display: inline-block;
    background: #EEF3FC;
    border: 1px solid #C7D9F5;
    color: #1E3A6E;
    border-radius: 999px;
    padding: 4px 12px;
    font-size: 0.78rem;
    font-weight: 700;
}

.login-title {
    font-family: Georgia, serif;
    color: #0F2248;
    font-size: 1.9rem;
    font-weight: 700;
    margin-top: 12px;
}

.login-subtitle {
    color: #4A5568;
    font-size: 0.95rem;
    line-height: 1.55;
}

.login-separator {
    border: none;
    border-top: 1px solid #C7D9F5;
    margin: 18px -24px 16px -24px;
}

/* Formulaire Streamlit dans la carte */
div[data-testid="stTextInput"] input {
    background: #F7F8FA !important;
    border: 1px solid #C7D9F5 !important;
    border-radius: 6px !important;
}

div[data-testid="stTextInput"] label {
    color: #0F2248 !important;
    font-weight: 600 !important;
}

div[data-testid="stCaptionContainer"] {
    color: #718096 !important;
}

.stButton > button {
    background: #1E3A6E !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 6px !important;
    font-weight: 700 !important;
    height: 46px !important;
}

.stButton > button:hover {
    background: #0F2248 !important;
    color: #FFFFFF !important;
}
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1F2A44 0%, #2C3E57 100%) !important;
}

section[data-testid="stSidebar"] * {
    color: #FFFFFF !important;
}

section[data-testid="stSidebar"] a {
    color: #D7E7FF !important;
}

.sidebar-brand {
    margin-top: 26px;
    margin-bottom: 42px;
}

.sidebar-logo {
    font-size: 1.05rem;
    font-weight: 800;
    letter-spacing: 0.02em;
    margin-bottom: 28px;
}

.sidebar-title {
    font-size: 1rem;
    font-weight: 700;
}

.sidebar-section-title {
    font-size: 1rem;
    font-weight: 800;
    margin-top: 36px;
    margin-bottom: 16px;
}

.sidebar-line {
    font-size: 0.88rem;
    line-height: 1.7;
    margin-bottom: 12px;
}

.sidebar-message {
    background: rgba(59, 92, 135, 0.55);
    border-radius: 8px;
    padding: 16px;
    font-size: 0.88rem;
    line-height: 1.55;
    font-weight: 600;
}

</style>

"""
FLIP_CARD_STYLE = """
<style>
.flip-container {
    perspective: 1200px;
    width: 100%;
    height: 190px;
    margin-bottom: 10px;
}

.flip-card {
    width: 100%;
    height: 100%;
    position: relative;
    transform-style: preserve-3d;
    transition: transform 0.7s ease;
    cursor: pointer;
}

.flip-card.flipped {
    transform: rotateY(180deg);
}

.flip-face {
    position: absolute;
    width: 100%;
    height: 100%;
    backface-visibility: hidden;
    border-radius: 14px;
    border: 1px solid #DDE3EF;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    padding: 20px;
    background: white;
}

.flip-front {
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.flip-back {
    background: #F5F7FB;
    transform: rotateY(180deg);
    overflow-y: auto;
}

.flip-title {
    font-weight: 700;
    font-size: 0.95rem;
    color: #0F2A6B;
    margin-bottom: 12px;
}

.flip-score {
    font-size: 2rem;
    font-weight: 700;
    color: #185FA5;
}

.flip-desc {
    font-size: 0.85rem;
    color: #6B7280;
    margin-top: 8px;
}
</style>
"""
