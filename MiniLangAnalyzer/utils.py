"""
utils.py — Shared Utilities
CS3510 Compiler Construction — Semester Project

Provides:
  - QSS stylesheet strings for dark / light themes
  - Colour constants
  - Miscellaneous helpers used by the GUI
"""

# ─────────────────────────────────────────────
# COLOUR TOKENS
# ─────────────────────────────────────────────

DARK = {
    'bg':          '#1E1E2E',
    'surface':     '#2A2A3E',
    'surface2':    '#313145',
    'border':      '#3E3E5E',
    'accent':      '#7C6AF7',      # purple-indigo
    'accent_h':    '#9D8FFF',
    'text':        '#CDD6F4',
    'text_muted':  '#7F849C',
    'header_bg':   '#1A1A2B',
    'token_kw':    '#569CD6',
    'token_str':   '#CE9178',
    'token_num':   '#B5CEA8',
    'token_op':    '#D4D4D4',
    'error':       '#F38BA8',
    'warning':     '#FAB387',
    'success':     '#A6E3A1',
    'editor_bg':   '#1A1A2B',
    'editor_text': '#CDD6F4',
    'line_num':    '#3B4261',
}

LIGHT = {
    'bg':          '#F5F5F0',
    'surface':     '#FFFFFF',
    'surface2':    '#EBEBEB',
    'border':      '#D0D0D0',
    'accent':      '#5A4FCF',
    'accent_h':    '#7C72E8',
    'text':        '#1E1E2E',
    'text_muted':  '#6E6E8E',
    'header_bg':   '#EAEAF5',
    'token_kw':    '#0000CC',
    'token_str':   '#A31515',
    'token_num':   '#098658',
    'token_op':    '#333333',
    'error':       '#CC0000',
    'warning':     '#D06000',
    'success':     '#007700',
    'editor_bg':   '#FFFFFF',
    'editor_text': '#1E1E2E',
    'line_num':    '#E0E0F0',
}


# ─────────────────────────────────────────────
# QSS STYLESHEET BUILDERS
# ─────────────────────────────────────────────

def build_stylesheet(dark: bool = True) -> str:
    """
    Return a comprehensive Qt stylesheet for the given theme.

    Args:
        dark: True → dark theme, False → light theme.

    Returns:
        A QSS string to pass to QApplication.setStyleSheet().
    """
    c = DARK if dark else LIGHT

    return f"""
/* ── Global ───────────────────────────────── */
QMainWindow, QDialog {{
    background-color: {c['bg']};
    color: {c['text']};
}}

QWidget {{
    background-color: {c['bg']};
    color: {c['text']};
    font-family: "Segoe UI", "Inter", "Helvetica Neue", sans-serif;
    font-size: 13px;
}}

/* ── Toolbar ──────────────────────────────── */
QToolBar {{
    background-color: {c['header_bg']};
    border-bottom: 1px solid {c['border']};
    padding: 4px 8px;
    spacing: 6px;
}}

QToolBar QToolButton {{
    background-color: transparent;
    color: {c['text']};
    border: none;
    padding: 6px 14px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 12px;
}}

QToolBar QToolButton:hover {{
    background-color: {c['surface2']};
}}

QToolBar QToolButton:pressed {{
    background-color: {c['accent']};
    color: #FFFFFF;
}}

/* ── Buttons ──────────────────────────────── */
QPushButton {{
    background-color: {c['surface2']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    padding: 6px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background-color: {c['accent']};
    color: #FFFFFF;
    border-color: {c['accent']};
}}

QPushButton:pressed {{
    background-color: {c['accent_h']};
}}

QPushButton#btn_analyze {{
    background-color: {c['accent']};
    color: #FFFFFF;
    border: none;
}}

QPushButton#btn_analyze:hover {{
    background-color: {c['accent_h']};
}}

/* ── Text Editor ──────────────────────────── */
QTextEdit {{
    background-color: {c['editor_bg']};
    color: {c['editor_text']};
    border: 1px solid {c['border']};
    border-radius: 6px;
    font-family: "JetBrains Mono", "Cascadia Code", "Consolas", "Courier New", monospace;
    font-size: 14px;
    selection-background-color: {c['accent']};
    padding: 4px;
}}

/* ── Tables ───────────────────────────────── */
QTableWidget {{
    background-color: {c['surface']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 4px;
    gridline-color: {c['border']};
    alternate-background-color: {c['surface2']};
    selection-background-color: {c['accent']};
    selection-color: #FFFFFF;
}}

QTableWidget::item {{
    padding: 5px 10px;
    border: none;
}}

QHeaderView::section {{
    background-color: {c['header_bg']};
    color: {c['text']};
    border: none;
    border-bottom: 2px solid {c['accent']};
    padding: 6px 10px;
    font-weight: 700;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

/* ── Tab widget ───────────────────────────── */
QTabWidget::pane {{
    border: 1px solid {c['border']};
    border-radius: 4px;
    background-color: {c['surface']};
}}

QTabBar::tab {{
    background-color: {c['surface2']};
    color: {c['text_muted']};
    border: none;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    font-weight: 600;
    font-size: 12px;
}}

QTabBar::tab:selected {{
    background-color: {c['accent']};
    color: #FFFFFF;
}}

QTabBar::tab:hover:!selected {{
    background-color: {c['border']};
    color: {c['text']};
}}

/* ── Splitter ─────────────────────────────── */
QSplitter::handle {{
    background-color: {c['border']};
    width: 2px;
    height: 2px;
}}

/* ── Status bar ───────────────────────────── */
QStatusBar {{
    background-color: {c['header_bg']};
    color: {c['text_muted']};
    border-top: 1px solid {c['border']};
    font-size: 12px;
    padding: 2px 8px;
}}

/* ── Scroll bars ──────────────────────────── */
QScrollBar:vertical {{
    background-color: {c['surface']};
    width: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:vertical {{
    background-color: {c['border']};
    border-radius: 5px;
    min-height: 20px;
}}

QScrollBar::handle:vertical:hover {{
    background-color: {c['accent']};
}}

QScrollBar:horizontal {{
    background-color: {c['surface']};
    height: 10px;
    border-radius: 5px;
}}

QScrollBar::handle:horizontal {{
    background-color: {c['border']};
    border-radius: 5px;
    min-width: 20px;
}}

QScrollBar::add-line, QScrollBar::sub-line {{
    border: none;
    background: none;
}}

/* ── Stats card labels ────────────────────── */
QLabel#stat_card {{
    background-color: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 8px;
    padding: 12px;
}}

QLabel#stat_title {{
    color: {c['text_muted']};
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}}

QLabel#stat_value {{
    color: {c['accent']};
    font-size: 28px;
    font-weight: 700;
}}

/* ── Group boxes ──────────────────────────── */
QGroupBox {{
    border: 1px solid {c['border']};
    border-radius: 6px;
    margin-top: 12px;
    font-weight: 700;
    color: {c['text_muted']};
    font-size: 11px;
    padding: 4px;
}}

QGroupBox::title {{
    subcontrol-origin: margin;
    left: 10px;
    padding: 0 6px;
    color: {c['text_muted']};
    font-size: 11px;
}}

/* ── Tooltip ──────────────────────────────── */
QToolTip {{
    background-color: {c['surface2']};
    color: {c['text']};
    border: 1px solid {c['border']};
    border-radius: 4px;
    padding: 4px 8px;
    font-size: 12px;
}}

/* ── Line number area (custom widget) ─────── */
QFrame#line_number_area {{
    background-color: {c['line_num']};
    border-right: 1px solid {c['border']};
}}
"""


# ─────────────────────────────────────────────
# MISC HELPERS
# ─────────────────────────────────────────────

def token_type_colour(token_type: str, dark: bool = True) -> str:
    """
    Return a hex colour string for a token type cell in the table.

    Args:
        token_type: e.g. 'KEYWORD', 'IDENTIFIER', 'OPERATOR' …
        dark: True for dark palette.

    Returns:
        Hex colour string.
    """
    c = DARK if dark else LIGHT
    mapping = {
        'KEYWORD':   c['token_kw'],
        'STRING':    c['token_str'],
        'INTEGER':   c['token_num'],
        'FLOAT':     c['token_num'],
        'OPERATOR':  c['token_op'],
        'DELIMITER': c['warning'],
        'IDENTIFIER': c['text'],
    }
    return mapping.get(token_type, c['text'])


def clamp(value: int, lo: int, hi: int) -> int:
    """Clamp *value* between *lo* and *hi* (inclusive)."""
    return max(lo, min(hi, value))


def truncate(text: str, max_len: int = 40) -> str:
    """Truncate *text* to *max_len* chars, adding ellipsis if needed."""
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"
