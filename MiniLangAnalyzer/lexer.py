"""
lexer.py — Core Lexical Analyzer for MiniLang Analyzer
CS3510 Compiler Construction — Semester Project

Performs tokenization, identifies lexemes, token types, line numbers,
detects lexical errors, and populates the symbol table.
"""

import re
from dataclasses import dataclass, field
from typing import List, Tuple, Optional


# ─────────────────────────────────────────────
# DATA CLASSES
# ─────────────────────────────────────────────

@dataclass
class Token:
    """Represents a single token produced by the lexer."""
    lexeme: str
    token_type: str
    line: int


@dataclass
class SymbolEntry:
    """Represents a single entry in the symbol table."""
    name: str
    category: str
    line: int


@dataclass
class LexicalError:
    """Represents a lexical error found during analysis."""
    error_type: str
    description: str
    line: int


@dataclass
class LexerResult:
    """Aggregated result of a full lexical analysis pass."""
    tokens: List[Token] = field(default_factory=list)
    symbol_table: List[SymbolEntry] = field(default_factory=list)
    errors: List[LexicalError] = field(default_factory=list)

    # Statistics counters
    total_tokens: int = 0
    total_keywords: int = 0
    total_identifiers: int = 0
    total_numbers: int = 0
    total_operators: int = 0
    total_delimiters: int = 0
    total_strings: int = 0
    total_errors: int = 0


# ─────────────────────────────────────────────
# KEYWORD SET
# ─────────────────────────────────────────────

KEYWORDS = {
    "int", "float", "double", "char", "string", "bool",
    "if", "else", "for", "while", "return", "break",
    "continue", "class", "public", "private", "void",
    "true", "false", "null", "new", "this", "static",
}

# ─────────────────────────────────────────────
# TOKEN PATTERNS  (order matters — longest match first)
# ─────────────────────────────────────────────

# Each tuple: (pattern, token_type)
# Using named groups for clarity.
TOKEN_SPEC: List[Tuple[str, str]] = [
    # Comments (skip, but track line count)
    (r'//[^\n]*',                           'COMMENT'),
    (r'/\*[\s\S]*?\*/',                     'COMMENT_BLOCK'),

    # String literals
    (r'"([^"\\]|\\.)*"',                    'STRING'),
    (r'"([^"\\]|\\.)*$',                    'UNCLOSED_STRING'),   # error

    # Floating-point numbers (must come before INTEGER)
    (r'\b\d+\.\d+([eE][+-]?\d+)?\b',       'FLOAT'),

    # Integer numbers
    (r'\b\d+\b',                            'INTEGER'),

    # Identifiers / keywords  (word chars starting with letter or _)
    (r'\b[A-Za-z_][A-Za-z0-9_]*\b',        'IDENTIFIER'),

    # Multi-char operators (must come before single-char)
    (r'==|!=|<=|>=|&&|\|\||<<|>>|\+\+|--|->|\+=|-=|\*=|/=|%=',  'OPERATOR'),

    # Single-char operators
    (r'[+\-*/%=<>!&|^~]',                  'OPERATOR'),

    # Delimiters
    (r'[;,(){}[\]]',                        'DELIMITER'),

    # Whitespace (skip)
    (r'[ \t\r]+',                           'WHITESPACE'),

    # Newline (track lines)
    (r'\n',                                 'NEWLINE'),

    # Invalid identifier starting with digit  (e.g. 2abc)
    (r'\d+[A-Za-z_][A-Za-z0-9_]*',        'INVALID_IDENTIFIER'),

    # Any remaining unknown character → error
    (r'.',                                  'UNKNOWN'),
]

# Compile the master regex (alternation of all patterns)
MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<T{i}>{pat})' for i, (pat, _) in enumerate(TOKEN_SPEC))
)

# Map group name back to token type
GROUP_TO_TYPE = {f'T{i}': ttype for i, (_, ttype) in enumerate(TOKEN_SPEC)}

# Invalid / error-producing types
ERROR_TYPES = {'UNKNOWN', 'UNCLOSED_STRING', 'INVALID_IDENTIFIER'}

# Types to skip silently (whitespace, newlines, comments)
SKIP_TYPES = {'WHITESPACE', 'NEWLINE', 'COMMENT', 'COMMENT_BLOCK'}


# ─────────────────────────────────────────────
# LEXER CLASS
# ─────────────────────────────────────────────

class Lexer:
    """
    Tokenizes source code and populates a LexerResult with
    tokens, symbol table entries, and error diagnostics.
    """

    def __init__(self):
        self._symbol_seen: dict = {}   # name → first SymbolEntry, for deduplication

    def analyze(self, source: str) -> LexerResult:
        """
        Run lexical analysis on *source* and return a LexerResult.

        Args:
            source: Raw source code string.

        Returns:
            LexerResult populated with tokens, symbols, errors, and stats.
        """
        result = LexerResult()
        self._symbol_seen = {}

        line_num = 1

        for mo in MASTER_PATTERN.finditer(source):
            # Identify which group matched
            kind = GROUP_TO_TYPE[mo.lastgroup]
            value = mo.group()

            # ── Line tracking ──────────────────────────────
            if kind == 'NEWLINE':
                line_num += 1
                continue

            if kind in SKIP_TYPES:
                # Still count lines inside block comments
                if kind == 'COMMENT_BLOCK':
                    line_num += value.count('\n')
                continue

            # ── Error handling ─────────────────────────────
            if kind in ERROR_TYPES:
                self._handle_error(kind, value, line_num, result)
                continue

            # ── Keyword vs Identifier ──────────────────────
            if kind == 'IDENTIFIER':
                if value in KEYWORDS:
                    kind = 'KEYWORD'
                    result.total_keywords += 1
                else:
                    result.total_identifiers += 1
                    self._add_symbol(value, 'Identifier', line_num, result)

            elif kind in ('INTEGER', 'FLOAT'):
                result.total_numbers += 1

            elif kind == 'OPERATOR':
                result.total_operators += 1

            elif kind == 'DELIMITER':
                result.total_delimiters += 1

            elif kind == 'STRING':
                result.total_strings += 1

            # ── Emit token ─────────────────────────────────
            token = Token(lexeme=value, token_type=kind, line=line_num)
            result.tokens.append(token)
            result.total_tokens += 1

        # Final stats
        result.total_errors = len(result.errors)
        return result

    # ──────────────────────────────────────────
    # Private helpers
    # ──────────────────────────────────────────

    def _handle_error(self, kind: str, value: str,
                      line: int, result: LexerResult) -> None:
        """Create a LexicalError entry based on the error kind."""
        if kind == 'UNKNOWN':
            err = LexicalError(
                error_type='Invalid Character',
                description=f"Unknown symbol '{value}' encountered",
                line=line
            )
        elif kind == 'UNCLOSED_STRING':
            err = LexicalError(
                error_type='Unclosed String Literal',
                description=f"String literal starting with {value[:10]!r} is never closed",
                line=line
            )
        elif kind == 'INVALID_IDENTIFIER':
            err = LexicalError(
                error_type='Invalid Identifier',
                description=f"Identifier '{value}' cannot start with a digit",
                line=line
            )
        else:
            err = LexicalError(
                error_type='Lexical Error',
                description=f"Unexpected token '{value}'",
                line=line
            )
        result.errors.append(err)

    def _add_symbol(self, name: str, category: str,
                    line: int, result: LexerResult) -> None:
        """Add identifier to the symbol table (no duplicates)."""
        if name not in self._symbol_seen:
            entry = SymbolEntry(name=name, category=category, line=line)
            self._symbol_seen[name] = entry
            result.symbol_table.append(entry)


# ─────────────────────────────────────────────
# Quick self-test (run this file directly)
# ─────────────────────────────────────────────

if __name__ == '__main__':
    sample = """
int main() {
    float x = 3.14;
    string name = "Alice";
    int 2bad = 5;        // invalid identifier
    char c = @;          // invalid character
    string s = "unclosed;
    return 0;
}
"""
    lexer = Lexer()
    res = lexer.analyze(sample)

    print("=== TOKENS ===")
    for t in res.tokens:
        print(f"  Line {t.line:>3}  {t.token_type:<20}  {t.lexeme!r}")

    print("\n=== SYMBOL TABLE ===")
    for s in res.symbol_table:
        print(f"  {s.name:<20}  {s.category:<15}  Line {s.line}")

    print("\n=== ERRORS ===")
    for e in res.errors:
        print(f"  Line {e.line}  [{e.error_type}]  {e.description}")

    print(f"\n=== STATS ===")
    print(f"  Total Tokens     : {res.total_tokens}")
    print(f"  Keywords         : {res.total_keywords}")
    print(f"  Identifiers      : {res.total_identifiers}")
    print(f"  Numbers          : {res.total_numbers}")
    print(f"  Operators        : {res.total_operators}")
    print(f"  Delimiters       : {res.total_delimiters}")
    print(f"  Errors           : {res.total_errors}")
