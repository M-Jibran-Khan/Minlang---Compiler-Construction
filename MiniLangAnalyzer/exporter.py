"""
exporter.py — Results Exporter
CS3510 Compiler Construction — Semester Project

Writes analysis results (tokens, symbol table, full report)
to text files in a chosen output directory.
"""

import os
from datetime import datetime
from typing import Optional

from lexer import LexerResult
from symbol_table import SymbolTable


class Exporter:
    """
    Serialises LexerResult and SymbolTable to text files.

    Generates three files:
        tokens.txt          — token stream
        symbol_table.txt    — symbol table
        analysis_report.txt — full combined report
    """

    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir

    # ── Public entry point ────────────────────

    def export_all(self, result: LexerResult,
                   sym_table: SymbolTable,
                   source_path: Optional[str] = None) -> dict[str, str]:
        """
        Export all three files.

        Args:
            result:      LexerResult from the lexer.
            sym_table:   Populated SymbolTable.
            source_path: Optional path of the original source file.

        Returns:
            Dict mapping file role → absolute path written.
        """
        os.makedirs(self.output_dir, exist_ok=True)
        paths = {}

        tokens_path = os.path.join(self.output_dir, "tokens.txt")
        with open(tokens_path, 'w', encoding='utf-8') as f:
            f.write(self._build_tokens_text(result))
        paths['tokens'] = tokens_path

        sym_path = os.path.join(self.output_dir, "symbol_table.txt")
        with open(sym_path, 'w', encoding='utf-8') as f:
            f.write(sym_table.to_text())
        paths['symbol_table'] = sym_path

        report_path = os.path.join(self.output_dir, "analysis_report.txt")
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(self._build_report(result, sym_table, source_path))
        paths['analysis_report'] = report_path

        return paths

    # ── Builders ──────────────────────────────

    def _build_tokens_text(self, result: LexerResult) -> str:
        """Format the token stream as a text table."""
        lines = [
            "=" * 60,
            "  TOKEN STREAM — MiniLang Analyzer",
            "=" * 60,
            f"  {'#':<5} {'Lexeme':<25} {'Token Type':<20} {'Line'}",
            "-" * 60,
        ]
        for i, tok in enumerate(result.tokens, 1):
            lexeme_display = repr(tok.lexeme) if '\n' in tok.lexeme else tok.lexeme
            lines.append(
                f"  {i:<5} {lexeme_display:<25} {tok.token_type:<20} {tok.line}"
            )
        lines.append("=" * 60)
        lines.append(f"  Total tokens: {result.total_tokens}")
        return "\n".join(lines)

    def _build_report(self, result: LexerResult,
                      sym_table: SymbolTable,
                      source_path: Optional[str]) -> str:
        """Build the comprehensive analysis report."""
        timestamp = datetime.now().strftime("%Y-%m-%d  %H:%M:%S")
        src_label = source_path or "<inline input>"

        sections = [
            self._header(timestamp, src_label),
            self._build_tokens_text(result),
            "",
            sym_table.to_text(),
            "",
            self._build_errors_text(result),
            "",
            self._build_stats_text(result),
        ]
        return "\n".join(sections)

    def _header(self, timestamp: str, src: str) -> str:
        return "\n".join([
            "=" * 60,
            "  MiniLang Analyzer — Full Analysis Report",
            "=" * 60,
            f"  Generated : {timestamp}",
            f"  Source    : {src}",
            "=" * 60,
            "",
        ])

    def _build_errors_text(self, result: LexerResult) -> str:
        lines = [
            "=" * 60,
            "  LEXICAL ERRORS",
            "=" * 60,
        ]
        if not result.errors:
            lines.append("  No lexical errors detected.")
        else:
            lines.append(f"  {'Line':<6} {'Error Type':<25} {'Description'}")
            lines.append("-" * 60)
            for err in result.errors:
                lines.append(f"  {err.line:<6} {err.error_type:<25} {err.description}")
        lines.append("=" * 60)
        return "\n".join(lines)

    def _build_stats_text(self, result: LexerResult) -> str:
        return "\n".join([
            "=" * 60,
            "  ANALYSIS STATISTICS",
            "=" * 60,
            f"  Total Tokens       : {result.total_tokens}",
            f"  Keywords           : {result.total_keywords}",
            f"  Identifiers        : {result.total_identifiers}",
            f"  Numbers            : {result.total_numbers}",
            f"  Operators          : {result.total_operators}",
            f"  Delimiters         : {result.total_delimiters}",
            f"  String Literals    : {result.total_strings}",
            f"  Lexical Errors     : {result.total_errors}",
            "=" * 60,
        ])
