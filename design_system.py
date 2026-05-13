# ============================================================================
# DESIGN SYSTEM PREMIUM - Need2Hire Consulting AI RH
# ============================================================================
# Inspired by: Notion AI, Linear, Stripe, Vercel
# Sensation: Premium, Intelligent, Reassuring, Modern, Fluid, High-end
# ============================================================================

# === COULEURS PALETTE PREMIUM IA/SaaS ===
COLORS = {
    # Primary - Deep Navy/Slate (fondations premium)
    "primary": "#0F172A",          # Slate 900 - principal
    "primary_light": "#1E293B",    # Slate 800
    "primary_lighter": "#334155",     # Slate 700
    
    # Accent Principal - Indigo (IA moderne)
    "accent": "#6366F1",          # Indigo 500 - accent IA principal
    "accent_light": "#818CF8",      # Indigo 400
    "accent_dark": "#4F46E5",    # Indigo 600
    
    # Accents Alternatifs - IA Glow
    "ai_glow": "#8B5CF6",         # Violet 500 - glow IA
    "ai_cyan": "#06B6D4",         # Cyan 500 - accent alternatif
    
    # Status Colors
    "success": "#10B981",          # Emerald 500
    "success_light": "#34D399",     # Emerald 400
    "success_bg": "#D1FAE5",      # Emerald 100
    
    "warning": "#F59E0B",         # Amber 500
    "warning_light": "#FBBF24",    # Amber 400
    "warning_bg": "#FEF3C7",      # Amber 100
    
    "danger": "#EF4444",           # Red 500
    "danger_light": "#F87171",      # Red 400
    "danger_bg": "#FEE2E2",        # Red 100
    
    "info": "#3B82F6",          # Blue 500
    "info_bg": "#DBEAFE",         # Blue 100
    
    # Backgrounds - Tons neutres premium
    "bg_primary": "#FAFBFC",       # Blanc cassé très clair
    "bg_secondary": "#F1F5F9",   # Slate 100
    "bg_tertiary": "#E2E8F0",    # Slate 200
    "bg_card": "#FFFFFF",          # Blanc pur pour cartes
    "bg_dark": "#0F172A",        # Fond sombre pour hero
    
    # Text - Hiérarchie
    "text_primary": "#0F172A",      # Texte principal
    "text_secondary": "#475569",     # Slate 600
    "text_tertiary": "#64748B",     # Slate 500
    "text_muted": "#94A3B8",      # Slate 400
    "text_inverse": "#FFFFFF",      # Texte sur fond sombre
    
    # Bordures
    "border": "#E2E8F0",         # Border default
    "border_light": "#F1F5F9",   # Border light
    "border_focus": "#6366F1",    # Border focus
    
    # Gradient definitions
    "gradient_hero": "linear-gradient(135deg, #0F172A 0%, #1E293B 50%, #312E81 100%)",
    "gradient_accent": "linear-gradient(135deg, #6366F1 0%, #8B5CF6 100%)",
    "gradient_card": "linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%)",
}

# === TYPOGRAPHIE ===
TYPOGRAPHY = {
    # Fontes (Google Fonts à charger)
    "font_primary": "'Satoshi', 'DM Sans', -apple-system, sans-serif",
    "font_display": "'Cabinet Grotesk', 'Playfair Display', serif",
    "font_mono": "'JetBrains Mono', 'Fira Code', monospace",
    
    # Tailles (rem-based)
    "size_hero": "2.5rem",       # 40px
    "size_h1": "2rem",           # 32px
    "size_h2": "1.5rem",         # 24px
    "size_h3": "1.25rem",        # 20px
    "size_h4": "1.125rem",       # 18px
    "size_body": "1rem",          # 16px
    "size_body_small": "0.9375rem", # 15px
    "size_small": "0.875rem",     # 14px
    "size_caption": "0.75rem",    # 12px
    "size_smallest": "0.6875rem", # 11px
    
    # Hauteurs de ligne
    "leading_tight": "1.25",
    "leading_normal": "1.5",
    "leading_relaxed": "1.75",
    
    # Poids
    "weight_regular": "400",
    "weight_medium": "500",
    "weight_semibold": "600",
    "weight_bold": "700",
    "weight_extrabold": "800",
}

# === OMBRES ===
SHADOWS = {
    "xs": "0 1px 2px 0 rgba(0, 0, 0, 0.05)",
    "sm": "0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px -1px rgba(0, 0, 0, 0.1)",
    "md": "0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -2px rgba(0, 0, 0, 0.1)",
    "lg": "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -4px rgba(0, 0, 0, 0.1)",
    "xl": "0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)",
    "2xl": "0 25px 50px -12px rgba(0, 0, 0, 0.25)",
    
    # Glow effects
    "glow_accent": "0 0 40px -10px rgba(99, 102, 241, 0.25)",
    "glow_accent_strong": "0 0 60px -15px rgba(99, 102, 241, 0.4)",
    "glow_success": "0 0 30px -8px rgba(16, 185, 129, 0.2)",
    "glow_success_strong": "0 0 50px -12px rgba(16, 185, 129, 0.35)",
    "glow_danger": "0 0 30px -8px rgba(239, 68, 68, 0.2)",
}

# !== BORDURES & RAYONS ===
STYLE = {
    # Rayons
    "radius_none": "0",
    "radius_sm": "6px",
    "radius_md": "10px",
    "radius_lg": "14px",
    "radius_xl": "20px",
    "radius_2xl": "28px",
    "radius_full": "9999px",
    
    # Espacements
    "space_1": "0.25rem",    # 4px
    "space_2": "0.5rem",     # 8px
    "space_3": "0.75rem",   # 12px
    "space_4": "1rem",       # 16px
    "space_5": "1.25rem",    # 20px
    "space_6": "1.5rem",     # 24px
    "space_8": "2rem",       # 32px
    "space_10": "2.5rem",   # 40px
    "space_12": "3rem",      # 48px
    
    # Transitions
    "transition_fast": "150ms ease",
    "transition_normal": "250ms ease",
    "transition_slow": "350ms ease",
    "transition_bounce": "400ms cubic-bezier(0.34, 1.56, 0.64, 1)",
}

# !== EFFETS ===
EFFECTS = {
    # Glassmorphism
    "glass_light": "backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px); background: rgba(255, 255, 255, 0.75)",
    "glass_medium": "backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); background: rgba(255, 255, 255, 0.85)",
    "glass_dark": "backdrop-filter: blur(20px); -webkit-backdrop-filter: blur(20px); background: rgba(15, 23, 42, 0.85)",
    "glass_accent": "backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px); background: rgba(99, 102, 241, 0.15)",
    
    # Sheen effect (pour hover)
    "sheen": "linear-gradient(135deg, rgba(255,255,255,0) 0%, rgba(255,255,255,0.3) 50%, rgba(255,255,255,0) 100%)",
    
    # Mesh gradient background
    "mesh_gradient": "radial-gradient(at 40% 20%, rgba(99, 102, 241, 0.15) 0px, transparent 50%), radial-gradient(at 80% 0%, rgba(139, 92, 246, 0.1) 0px, transparent 50%), radial-gradient(at 0% 50%, rgba(6, 182, 212, 0.08) 0px, transparent 50%), radial-gradient(at 80% 50%, rgba(16, 185, 129, 0.08) 0px, transparent 50%)",
}

# !== Z-INDEX LAYERS ===
ZINDEX = {
    "base": "1",
    "dropdown": "100",
    "sticky": "200",
    "modal": "300",
    "popover": "400",
    "tooltip": "500",
    "toast": "600",
}

# !== RESPONSIVE BREAKPOINTS ===
BREAKPOINTS = {
    "sm": "640px",
    "md": "768px",
    "lg": "1024px",
    "xl": "1280px",
    "2xl": "1536px",
}


# ============================================================================
# FONCTIONS UTILITAIRES
# ============================================================================

def get_accent_color(score: float, max_score: float = 100) -> str:
    """Retourne une couleur basée sur le score (rouge -> orange -> vert)"""
    pct = (score / max_score) * 100
    if pct < 40:
        return COLORS["danger"]
    elif pct < 70:
        return COLORS["warning"]
    else:
        return COLORS["success"]


def get_shadow_class(size: str = "md") -> str:
    """Retourne la classe d'ombre correspondante"""
    return SHADOWS.get(size, SHADOWS["md"])


def get_radius_class(size: str = "md") -> str:
    """Retourne le rayon correspondant"""
    return STYLE.get(f"radius_{size}", STYLE["radius_md"])