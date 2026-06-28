"""
symbol_table.py — Symbol Table Manager
CS3510 Compiler Construction — Semester Project

Manages the symbol table produced by the lexer.
Provides lookup, insertion, and export utilities.
"""

from typing import List, Optional
from lexer import SymbolEntry


class SymbolTable:
    """
    A simple ordered symbol table with O(1) name lookup.

    The lexer populates it; this class provides a clean
    interface for the GUI and exporter to query it.
    """

    def __init__(self):
        self._entries: List[SymbolEntry] = []
        self._index: dict[str, SymbolEntry] = {}   # name → entry

    # ── Population ────────────────────────────

    def load(self, entries: List[SymbolEntry]) -> None:
        """
        Replace the current table with *entries* from a LexerResult.

        Args:
            entries: list of SymbolEntry objects produced by the lexer.
        """
        self._entries = []
        self._index = {}
        for entry in entries:
            self._insert(entry)

    def _insert(self, entry: SymbolEntry) -> None:
        """Insert without duplicating (first-occurrence wins)."""
        if entry.name not in self._index:
            self._entries.append(entry)
            self._index[entry.name] = entry

    # ── Queries ───────────────────────────────

    def lookup(self, name: str) -> Optional[SymbolEntry]:
        """
        Return the SymbolEntry for *name*, or None if absent.

        Args:
            name: Identifier name to look up.
        """
        return self._index.get(name)

    def all_entries(self) -> List[SymbolEntry]:
        """Return all symbol table entries in insertion order."""
        return list(self._entries)

    def count(self) -> int:
        """Return the number of unique identifiers in the table."""
        return len(self._entries)

    # ── Export ────────────────────────────────

    def to_text(self) -> str:
        """
        Serialize the symbol table to a human-readable string.

        Returns:
            Formatted text suitable for writing to symbol_table.txt.
        """
        lines = [
            "=" * 55,
            "  SYMBOL TABLE — MiniLang Analyzer",
            "=" * 55,
            f"  {'Name':<25} {'Category':<15} {'Line'}",
            "-" * 55,
        ]
        for entry in self._entries:
            lines.append(f"  {entry.name:<25} {entry.category:<15} {entry.line}")
        lines.append("=" * 55)
        lines.append(f"  Total Symbols: {self.count()}")
        return "\n".join(lines)

    def __len__(self) -> int:
        return self.count()

    def __repr__(self) -> str:
        return f"SymbolTable({self.count()} entries)"
