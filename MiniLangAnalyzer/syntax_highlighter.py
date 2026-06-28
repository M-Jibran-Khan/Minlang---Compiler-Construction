"""
syntax_highlighter.py — Real-time Syntax Highlighting
CS3510 Compiler Construction — Semester Project

Provides a QSyntaxHighlighter subclass that colours keywords,
strings, numbers, comments, and operators in the code editor.
Supports both dark and light themes.
"""

import re
from PyQt6.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QFont
from PyQt6.QtCore import Qt

from lexer import KEYWORDS


# ─────────────────────────────────────────────
# THEME PALETTES
# ─────────────────────────────────────────────

DARK_THEME = {
    'keyword':    '#569CD6',   # VS Code blue
    'string':     '#CE9178',   # warm orange
    'number':     '#B5CEA8',   # soft green
    'comment':    '#6A9955',   # muted green
    'operator':   '#D4D4D4',   # light grey
    'identifier': '#9CDCFE',   # cyan
    'delimiter':  '#FFD700',   # gold
    'error':      '#F44747',   # bright red
}

LIGHT_THEME = {
    'keyword':    '#0000FF',   # classic blue
    'string':     '#A31515',   # dark red
    'number':     '#098658',   # dark green
    'comment':    '#008000',   # green
    'operator':   '#222222',   # near-black
    'identifier': '#001080',   # dark navy
    'delimiter':  '#7B2D00',   # brown
    'error':      '#FF0000',   # red
}


def _fmt(color_hex: str, bold: bool = False,
         italic: bool = False) -> QTextCharFormat:
    """Build a QTextCharFormat from a hex colour string."""
    fmt = QTextCharFormat()
    fmt.setForeground(QColor(color_hex))
    if bold:
        fmt.setFontWeight(QFont.Weight.Bold)
    if italic:
        fmt.setFontItalic(True)
    return fmt


# ─────────────────────────────────────────────
# HIGHLIGHTING RULES
# ─────────────────────────────────────────────

# Each rule: (compiled_regex, format_key)
def _build_rules():
    """
    Returns a list of (pattern, format_key) tuples.
    Order matters: earlier rules take visual priority.
    """
    kw_pattern = r'\b(' + '|'.join(sorted(KEYWORDS, key=len, reverse=True)) + r')\b'
    return [
        # Single-line comments
        (re.compile(r'//[^\n]*'),                        'comment'),
        # Block comments
        (re.compile(r'/\*[\s\S]*?\*/'),                  'comment'),
        # String literals (including escape sequences)
        (re.compile(r'"([^"\\]|\\.)*"'),                 'string'),
        # Float numbers
        (re.compile(r'\b\d+\.\d+([eE][+-]?\d+)?\b'),   'number'),
        # Integer numbers
        (re.compile(r'\b\d+\b'),                         'number'),
        # Keywords  (bold)
        (re.compile(kw_pattern),                         'keyword'),
        # Multi-char operators
        (re.compile(r'==|!=|<=|>=|&&|\|\||<<|>>|\+\+|--|->|\+=|-=|\*=|/=|%='), 'operator'),
        # Single-char operators
        (re.compile(r'[+\-*/%=<>!&|^~]'),               'operator'),
        # Delimiters
        (re.compile(r'[;,(){}[\]]'),                     'delimiter'),
    ]


RULES = _build_rules()


# ─────────────────────────────────────────────
# HIGHLIGHTER CLASS
# ─────────────────────────────────────────────

class MiniLangHighlighter(QSyntaxHighlighter):
    """
    Qt syntax highlighter for MiniLang source code.

    Usage:
        highlighter = MiniLangHighlighter(editor.document())
        highlighter.set_theme('dark')   # or 'light'
    """

    def __init__(self, document):
        super().__init__(document)
        self._theme = 'dark'
        self._formats: dict[str, QTextCharFormat] = {}
        self._apply_theme(DARK_THEME)

    # ── Public API ────────────────────────────

    def set_theme(self, theme: str) -> None:
        """
        Switch colour theme.

        Args:
            theme: 'dark' or 'light'
        """
        self._theme = theme
        palette = DARK_THEME if theme == 'dark' else LIGHT_THEME
        self._apply_theme(palette)
        self.rehighlight()

    # ── Qt override ───────────────────────────

    def highlightBlock(self, text: str) -> None:
        """Called by Qt for every text block that needs highlighting."""
        for pattern, fmt_key in RULES:
            fmt = self._formats.get(fmt_key)
            if fmt is None:
                continue
            for mo in pattern.finditer(text):
                self.setFormat(mo.start(), mo.end() - mo.start(), fmt)

    # ── Private helpers ───────────────────────

    def _apply_theme(self, palette: dict) -> None:
        """Rebuild format objects from a colour palette dict."""
        self._formats = {
            'keyword':    _fmt(palette['keyword'],    bold=True),
            'string':     _fmt(palette['string']),
            'number':     _fmt(palette['number']),
            'comment':    _fmt(palette['comment'],    italic=True),
            'operator':   _fmt(palette['operator']),
            'identifier': _fmt(palette['identifier']),
            'delimiter':  _fmt(palette['delimiter']),
            'error':      _fmt(palette['error'],      bold=True),
        }
