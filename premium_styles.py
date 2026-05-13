# ============================================================================
# PREMIUM STYLES CSS - Need2Hire Consulting AI RH
# ============================================================================
# Global CSS premium pour Streamlit
#风格 professionnel RH : moderne, premium, lisible, pas gaming
# ============================================================================

PREMIUM_CSS = """
<style>
/* === IMPORT FONTS === */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&family=DM+Serif+Display:ital@0;1&display=swap');

/* === CSS CUSTOM PROPERTIES === */
:root {
    /* Couleurs Primary */
    --premium-primary: #0F172A;
    --premium-primary-light: #1E293B;
    --premium-accent: #6366F1;
    --premium-accent-light: #818CF8;
    
    /* Status */
    --premium-success: #10B981;
    --premium-warning: #F59E0B;
    --premium-danger: #EF4444;
    
    /* Backgrounds */
    --premium-bg: #FAFBFC;
    --premium-bg-card: #FFFFFF;
    --premium-bg-dark: #0F172A;
    
    /* Text */
    --premium-text: #0F172A;
    --premium-text-secondary: #475569;
    --premium-text-muted: #94A3B8;
    
    /* Bordures */
    --premium-border: #E2E8F0;
    
    /* Rayons */
    --premium-radius-sm: 8px;
    --premium-radius-md: 12px;
    --premium-radius-lg: 16px;
    --premium-radius-xl: 24px;
    
    /* Ombres */
    --premium-shadow-sm: 0 1px 3px rgba(0,0,0,0.08);
    --premium-shadow-md: 0 4px 12px rgba(0,0,0,0.08);
    --premium-shadow-lg: 0 8px 24px rgba(0,0,0,0.12);
    --premium-shadow-glow: 0 0 30px rgba(99,102,241,0.15);
    
    /* Transitions */
    --premium-transition: 250ms ease;
}

/* === BASE STYLES === */
html, body, [class*="css"] {
    font-family: 'DM Sans', -apple-system, sans-serif !important;
    color: var(--premium-text) !important;
    background: var(--premium-bg) !important;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}

/* === PREMIUM HERO === */
.premium-hero {
    background: linear-gradient(135deg, #0F172A 0%, #1E293B 60%, #312E81 100%);
    border-radius: var(--premium-radius-lg);
    padding: 40px 48px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}

/* Background decorative shapes */
.premium-hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 240px; height: 240px;
    background: radial-gradient(circle, rgba(255,255,255,0.06) 0%, transparent 70%);
    border-radius: 50%;
}

.premium-hero::after {
    content: '';
    position: absolute;
    bottom: -80px; left: 20%;
    width: 180px; height: 180px;
    background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%);
    border-radius: 50%;
}

/* === PREMIUM CARDS === */
.premium-card {
    background: var(--premium-bg-card);
    border: 1px solid var(--premium-border);
    border-radius: var(--premium-radius-md);
    padding: 24px;
    box-shadow: var(--premium-shadow-sm);
    transition: all var(--premium-transition);
}

.premium-card:hover {
    box-shadow: var(--premium-shadow-md);
    transform: translateY(-2px);
}

/* Card accent colors */
.premium-card-accent {
    border-left: 4px solid var(--premium-accent);
}

.premium-card-success {
    border-left: 4px solid var(--premium-success);
}

.premium-card-warning {
    border-left: 4px solid var(--premium-warning);
}

.premium-card-danger {
    border-left: 4px solid var(--premium-danger);
}

/* === PREMIUM METRICS / KPI CARDS === */
.metric-card {
    background: var(--premium-bg-card);
    border: 1px solid var(--premium-border);
    border-radius: var(--premium-radius-md);
    padding: 20px;
    text-align: center;
    box-shadow: var(--premium-shadow-sm);
}

.premium-metric-value {
    font-family: 'DM Serif Display', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--premium-primary);
    line-height: 1;
    margin-bottom: 8px;
}

.premium-metric-label {
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--premium-text-muted);
}

/* Metric with glow on hover */
.premium-metric-glow:hover {
    box-shadow: var(--premium-shadow-glow);
    border-color: var(--premium-accent-light);
}

/* === PROGRESS BARS === */
.premium-progress-track {
    height: 8px;
    background: var(--premium-bg);
    border-radius: 999px;
    overflow: hidden;
}

.premium-progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}

/* Progress colors */
.premium-progress-success {
    background: linear-gradient(90deg, #10B981 0%, #34D399 100%);
}

.premium-progress-warning {
    background: linear-gradient(90deg, #F59E0B 0%, #FBBF24 100%);
}

.premium-progress-danger {
    background: linear-gradient(90deg, #EF4444 0%, #F87171 100%);
}

.premium-progress-accent {
    background: linear-gradient(90deg, #6366F1 0%, #818CF8 100%);
}

/* === PREMIUM BADGES === */
.premium-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.premium-badge-success {
    background: #D1FAE5;
    color: #065F46;
}

.premium-badge-warning {
    background: #FEF3C7;
    color: #92400E;
}

.premium-badge-danger {
    background: #FEE2E2;
    color: #991B1B;
}

.premium-badge-accent {
    background: #EEF2FF;
    color: #4338CA;
}

/* Badge with glow */
.premium-badge-glow {
    box-shadow: 0 0 12px rgba(99,102,241,0.2);
}

/* === PREMIUM TAGS === */
.premium-tag {
    display: inline-block;
    padding: 5px 12px;
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    background: #F1F5F9;
    color: #475569;
    border: 1px solid #E2E8F0;
}

/* === PREMIUM SECTIONS === */
.premium-section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.25rem;
    color: var(--premium-primary);
    margin: 32px 0 16px 0;
    padding-bottom: 12px;
    border-bottom: 2px solid #EF4444;
    display: inline-block;
}

/* === PREMIUM SIDEBAR === */
.premium-sidebar {
    background: linear-gradient(180deg, #F1F5F9 0%, #E2E8F0 100%);
    border-right: 1px solid var(--premium-border);
    padding: 24px 16px;
}

.premium-sidebar-logo {
    font-size: 0.7rem;
    font-weight: 700;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: var(--premium-accent);
    margin-bottom: 4px;
}

.premium-sidebar-product {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--premium-primary);
}

.premium-sidebar-user {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: white;
    border-radius: var(--premium-radius-md);
    border: 1px solid var(--premium-border);
}

.premium-sidebar-avatar {
    width: 40px;
    height: 40px;
    border-radius: 50%;
    background: linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.875rem;
    font-weight: 700;
}

/* === PREMIUM INPUTS === */
.premium-input textarea {
    background: white !important;
    border: 1px solid var(--premium-border) !important;
    border-radius: var(--premium-radius-md) !important;
    padding: 16px !important;
    font-family: 'DM Sans', sans-serif !important;
    transition: all var(--premium-transition);
}

.premium-input textarea:focus {
    border-color: var(--premium-accent) !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.1) !important;
}

/* === PREMIUM BUTTONS === */
.premium-button button {
    background: var(--premium-accent) !important;
    color: white !important;
    border: none !important;
    border-radius: var(--premium-radius-md) !important;
    font-weight: 600 !important;
    padding: 12px 24px !important;
    transition: all var(--premium-transition);
}

.premium-button button:hover {
    background: #4F46E5 !important;
    transform: translateY(-1px);
    box-shadow: var(--premium-shadow-sm);
}

/* === PREMIUM CHECKLIST === */
.premium-checklist-item {
    display: flex;
    align-items: center;
    gap: 12px;
    padding: 16px;
    background: white;
    border: 1px solid var(--premium-border);
    border-radius: var(--premium-radius-md);
    margin-bottom: 12px;
    transition: all var(--premium-transition);
}

.premium-checklist-item:hover {
    box-shadow: var(--premium-shadow-sm);
}

.premium-check-icon {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.75rem;
    font-weight: 700;
}

.premium-check-oui {
    background: #D1FAE5;
    color: #065F46;
}

.premium-check-non {
    background: #FEE2E2;
    color: #991B1B;
}

.premium-check-partiel {
    background: #FEF3C7;
    color: #92400E;
}

/* === PREMIUM INFO/WARN BOXES === */
.premium-info-box {
    background: #EEF2FF;
    border: 1px solid #C7D9F5;
    border-radius: var(--premium-radius-md);
    padding: 16px 20px;
    color: #3730A3;
    font-size: 0.9rem;
}

.premium-warn-box {
    background: #FFFBEB;
    border: 1px solid #FDE68A;
    border-radius: var(--premium-radius-md);
    padding: 16px 20px;
    color: #92400E;
    font-size: 0.9rem;
}

/* === PREMIUM DIVIDER === */
.premium-divider {
    height: 1px;
    background: var(--premium-border);
    margin: 32px 0;
}

/* === PREMIUM EMPTY STATE === */
.premium-empty {
    color: var(--premium-text-muted);
    font-style: italic;
    font-size: 0.875rem;
    padding: 16px;
    text-align: center;
}

/* === ANIMATIONS SUBTILES === */

/* Fade in */
@keyframes premium-fade-in {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

.premium-animate-fade {
    animation: premium-fade-in 0.4s ease-out forwards;
}

/* Slide up */
@keyframes premium-slide-up {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}

.premium-animate-slide {
    animation: premium-slide-up 0.5s ease-out forwards;
}

/* Subtle pulse glow - hover only */
@keyframes premium-glow-pulse {
    0%, 100% { box-shadow: 0 0 15px rgba(99,102,241,0.1); }
    50% { box-shadow: 0 0 20px rgba(99,102,241,0.15); }
}

.premium-animate-glow:hover {
    animation: premium-glow-pulse 0.5s ease-in-out;
}

/* === GLASSMORPHISM SUBTIL === */
.premium-glass {
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    background: rgba(255,255,255,0.85);
}

/* === RESPONSIVE === */
@media (max-width: 768px) {
    .premium-hero {
        padding: 24px;
    }
    
    .premium-metric-value {
        font-size: 2rem;
    }
}

/* === OVERRIDES Streamlit === */
div[data-testid="stExpander"] {
    border: 1px solid var(--premium-border) !important;
    border-radius: var(--premium-radius-md) !important;
    box-shadow: none !important;
}

div[data-testid="stMetric"] {
    background: transparent;
}

.stRadio > div {
    gap: 8px;
}
</style>
"""