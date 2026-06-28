"""
gui.py — Main Application Window
CS3510 Compiler Construction — Semester Project

Builds the full PyQt6 GUI:
  - Source code editor with syntax highlighting
  - Clear (bottom-left) and Analyze (bottom-right) buttons inside the editor panel
  - Token table, Symbol table, Error table (tabbed)
  - Statistics dashboard
  - Toolbar with Open / Export / Dark-mode toggle
  - Status bar with contextual messages
"""

import os
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QSplitter, QTextEdit, QTableWidget, QTableWidgetItem,
    QPushButton, QStatusBar, QTabWidget, QToolBar,
    QFileDialog, QLabel, QGroupBox, QGridLayout,
    QSizePolicy, QHeaderView, QFrame, QMessageBox,
    QApplication,
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import (
    QAction, QColor, QFont, QIcon, QKeySequence,
    QTextOption,
)

from lexer import Lexer, LexerResult
from symbol_table import SymbolTable
from syntax_highlighter import MiniLangHighlighter
from exporter import Exporter
from utils import build_stylesheet, token_type_colour, DARK, LIGHT, truncate


# ─────────────────────────────────────────────
# BACKGROUND WORKER
# ─────────────────────────────────────────────

class AnalysisWorker(QThread):
    """
    Runs lexical analysis in a background thread so the GUI
    stays responsive on large files.
    """
    finished = pyqtSignal(object)   # emits LexerResult
    error    = pyqtSignal(str)      # emits error message

    def __init__(self, source: str):
        super().__init__()
        self._source = source

    def run(self):
        try:
            lexer = Lexer()
            result = lexer.analyze(self._source)
            self.finished.emit(result)
        except Exception as exc:
            self.error.emit(str(exc))


# ─────────────────────────────────────────────
# STATISTICS CARD WIDGET
# ─────────────────────────────────────────────

class StatCard(QFrame):
    """
    A small card showing a label (title) and a large number (value).
    Used in the statistics dashboard.
    """

    def __init__(self, title: str, value: int = 0,
                 accent: str = '#7C6AF7', parent=None):
        super().__init__(parent)
        self._accent = accent
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setMinimumWidth(130)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 12)
        layout.setSpacing(4)

        self._title_lbl = QLabel(title.upper())
        self._title_lbl.setObjectName("stat_title")

        self._value_lbl = QLabel(str(value))
        self._value_lbl.setObjectName("stat_value")
        font = QFont()
        font.setPointSize(22)
        font.setBold(True)
        self._value_lbl.setFont(font)

        layout.addWidget(self._title_lbl)
        layout.addWidget(self._value_lbl)

    def set_value(self, value: int) -> None:
        self._value_lbl.setText(str(value))

    def set_accent(self, colour: str) -> None:
        self._accent = colour
        self._value_lbl.setStyleSheet(f"color: {colour};")


# ─────────────────────────────────────────────
# MAIN WINDOW
# ─────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    Primary application window for MiniLang Analyzer.

    Layout
    ──────
    ┌─────────────────────────────────────────────┐
    │  Toolbar: [Open File]  [Export]  [Dark Mode]│
    ├─────────────────┬───────────────────────────┤
    │  Source Code    │   Statistics Panel        │
    │  Editor         ├───────────────────────────┤
    │  (QTextEdit)    │   Tabs:                   │
    │                 │   Token | Symbol | Error  │
    │─────────────────│                           │
    │ [Clear] [Anlyz] │                           │
    ├─────────────────┴───────────────────────────┤
    │  Status Bar                                 │
    └─────────────────────────────────────────────┘
    """

    SUPPORTED_EXTENSIONS = "Source Files (*.c *.cpp *.py *.txt);;All Files (*)"

    def __init__(self):
        super().__init__()
        self._dark_mode = True
        self._current_file: Optional[str] = None
        self._last_result: Optional[LexerResult] = None
        self._symbol_table = SymbolTable()
        self._worker: Optional[AnalysisWorker] = None

        self.setWindowTitle("MiniLang Analyzer  —  CS3510 Compiler Construction")
        self.resize(1350, 800)
        self.setMinimumSize(900, 600)

        self._build_ui()
        self._apply_theme()
        self._set_status("Ready  —  Open a file or type source code to begin.")

    # ══════════════════════════════════════════
    # UI CONSTRUCTION
    # ══════════════════════════════════════════

    def _build_ui(self):
        """Assemble all widgets and layouts."""
        self._build_toolbar()
        self._build_central_widget()
        self._build_status_bar()

    # ── Toolbar ───────────────────────────────

    def _build_toolbar(self):
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setIconSize(tb.iconSize().__class__(20, 20))
        self.addToolBar(tb)

        def action(label: str, tooltip: str, shortcut: Optional[str] = None):
            act = QAction(label, self)
            act.setToolTip(tooltip)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            tb.addAction(act)
            return act

        self._act_open  = action("📂  Open File", "Open source file (Ctrl+O)", "Ctrl+O")
        tb.addSeparator()
        self._act_export = action("💾  Export",   "Export results (Ctrl+E)",   "Ctrl+E")
        tb.addSeparator()
        self._act_theme  = action("🌙  Dark Mode","Toggle dark / light theme",  "Ctrl+D")

        self._act_open.triggered.connect(self._open_file)
        self._act_export.triggered.connect(self._export_results)
        self._act_theme.triggered.connect(self._toggle_theme)

    # ── Central widget ────────────────────────

    def _build_central_widget(self):
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QVBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # Outer horizontal splitter: editor | right panel
        h_split = QSplitter(Qt.Orientation.Horizontal)
        h_split.setHandleWidth(3)
        root_layout.addWidget(h_split)

        # ── Left: editor ──────────────────────
        editor_frame = self._build_editor_panel()
        h_split.addWidget(editor_frame)

        # ── Right: stats + tabs ───────────────
        right_frame = QWidget()
        right_layout = QVBoxLayout(right_frame)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        right_layout.addWidget(self._build_stats_panel())
        right_layout.addWidget(self._build_tabs_panel(), stretch=1)

        h_split.addWidget(right_frame)
        h_split.setSizes([550, 800])

    # ── Editor panel ──────────────────────────

    def _build_editor_panel(self) -> QWidget:
        panel = QWidget()
        panel.setObjectName("editor_panel")
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(8, 8, 4, 8)
        layout.setSpacing(6)

        # Title bar
        title_row = QHBoxLayout()
        lbl = QLabel("Source Code Editor")
        lbl.setStyleSheet("font-weight: 700; font-size: 13px;")
        title_row.addWidget(lbl)
        title_row.addStretch()

        self._line_col_lbl = QLabel("Ln 1, Col 1")
        self._line_col_lbl.setObjectName("stat_title")
        title_row.addWidget(self._line_col_lbl)
        layout.addLayout(title_row)

        # Code editor
        self._editor = QTextEdit()
        self._editor.setAcceptRichText(False)
        self._editor.setWordWrapMode(QTextOption.WrapMode.NoWrap)
        self._editor.setPlaceholderText(
            "// Type or paste your source code here...\n"
            "// Supported: C, C++, Python, plain text\n"
            "// Press F5 or click ▶ Analyze to begin."
        )
        self._editor.cursorPositionChanged.connect(self._update_cursor_pos)

        # Attach syntax highlighter
        self._highlighter = MiniLangHighlighter(self._editor.document())

        layout.addWidget(self._editor, stretch=1)

        # ── Button bar (below editor) ──────────
        btn_row = QHBoxLayout()
        btn_row.setContentsMargins(0, 4, 0, 0)
        btn_row.setSpacing(8)

        self._btn_clear = QPushButton("✕  Clear")
        self._btn_clear.setToolTip("Clear editor and reset tables (Ctrl+L)")
        self._btn_clear.setShortcut(QKeySequence("Ctrl+L"))
        self._btn_clear.setFixedHeight(34)
        self._btn_clear.setMinimumWidth(110)

        self._btn_analyze = QPushButton("▶  Analyze")
        self._btn_analyze.setToolTip("Run lexical analysis (F5)")
        self._btn_analyze.setShortcut(QKeySequence("F5"))
        self._btn_analyze.setObjectName("btn_analyze")   # accent style from QSS
        self._btn_analyze.setFixedHeight(34)
        self._btn_analyze.setMinimumWidth(120)

        btn_row.addWidget(self._btn_clear)
        btn_row.addStretch()                             # pushes Analyze to the right
        btn_row.addWidget(self._btn_analyze)

        self._btn_clear.clicked.connect(self._clear_editor)
        self._btn_analyze.clicked.connect(self._run_analysis)

        layout.addLayout(btn_row)

        return panel

    # ── Stats panel ───────────────────────────

    def _build_stats_panel(self) -> QGroupBox:
        box = QGroupBox("Analysis Statistics")
        grid = QGridLayout(box)
        grid.setContentsMargins(10, 16, 10, 10)
        grid.setSpacing(8)

        c = DARK if self._dark_mode else LIGHT

        def card(title, accent=None):
            sc = StatCard(title, accent=accent or c['accent'])
            return sc

        self._sc_tokens     = card("Tokens",     c['accent'])
        self._sc_keywords   = card("Keywords",   c['token_kw'])
        self._sc_identifiers= card("Identifiers",c['token_str'])
        self._sc_numbers    = card("Numbers",    c['token_num'])
        self._sc_operators  = card("Operators",  c['text_muted'])
        self._sc_delimiters = card("Delimiters", c['warning'])
        self._sc_errors     = card("Errors",     c['error'])

        cards = [
            self._sc_tokens, self._sc_keywords, self._sc_identifiers,
            self._sc_numbers, self._sc_operators, self._sc_delimiters,
            self._sc_errors,
        ]
        for i, c_widget in enumerate(cards):
            grid.addWidget(c_widget, 0, i)

        return box

    # ── Tabs panel ────────────────────────────

    def _build_tabs_panel(self) -> QTabWidget:
        tabs = QTabWidget()
        tabs.setObjectName("result_tabs")

        # Token table
        self._token_table = self._make_table(["Lexeme", "Token Type", "Line"])
        tabs.addTab(self._wrap(self._token_table), "🔑  Token Stream")

        # Symbol table
        self._sym_table_widget = self._make_table(["Identifier", "Category", "Line"])
        tabs.addTab(self._wrap(self._sym_table_widget), "📋  Symbol Table")

        # Error table
        self._error_table = self._make_table(["Error Type", "Description", "Line"])
        tabs.addTab(self._wrap(self._error_table), "⚠  Errors")

        return tabs

    # ── Status bar ────────────────────────────

    def _build_status_bar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        self._status_msg = QLabel()
        self._status_right = QLabel()
        sb.addWidget(self._status_msg, 1)
        sb.addPermanentWidget(self._status_right)

    # ══════════════════════════════════════════
    # SLOT HANDLERS
    # ══════════════════════════════════════════

    def _open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Source File", "", self.SUPPORTED_EXTENSIONS
        )
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8', errors='replace') as f:
                source = f.read()
            self._editor.setPlainText(source)
            self._current_file = path
            filename = os.path.basename(path)
            self._set_status(f"File loaded: {filename}")
            self._status_right.setText(filename)
            self.setWindowTitle(f"MiniLang Analyzer — {filename}")
        except OSError as exc:
            QMessageBox.critical(self, "Error", f"Cannot open file:\n{exc}")

    def _run_analysis(self):
        source = self._editor.toPlainText().strip()
        if not source:
            self._set_status("⚠  No source code to analyse. Type or open a file first.")
            return

        self._set_status("Analysing source code…")
        QApplication.processEvents()

        # Disable button during analysis to prevent double-submit
        self._btn_analyze.setEnabled(False)

        self._worker = AnalysisWorker(source)
        self._worker.finished.connect(self._on_analysis_done)
        self._worker.error.connect(self._on_analysis_error)
        self._worker.start()

    def _on_analysis_done(self, result: LexerResult):
        self._last_result = result
        self._symbol_table.load(result.symbol_table)

        self._populate_token_table(result)
        self._populate_symbol_table(result)
        self._populate_error_table(result)
        self._update_stats(result)

        self._btn_analyze.setEnabled(True)
        err_suffix = f"  |  ⚠ {result.total_errors} error(s)" if result.total_errors else ""
        self._set_status(f"Analysis complete — {result.total_tokens} tokens found{err_suffix}")

    def _on_analysis_error(self, msg: str):
        self._btn_analyze.setEnabled(True)
        self._set_status(f"Error during analysis: {msg}")
        QMessageBox.critical(self, "Analysis Error", msg)

    def _clear_editor(self):
        self._editor.clear()
        self._token_table.setRowCount(0)
        self._sym_table_widget.setRowCount(0)
        self._error_table.setRowCount(0)
        self._reset_stats()
        self._current_file = None
        self._last_result = None
        self._status_right.setText("")
        self.setWindowTitle("MiniLang Analyzer  —  CS3510 Compiler Construction")
        self._set_status("Editor cleared.")

    def _export_results(self):
        if not self._last_result:
            self._set_status("⚠  Nothing to export — run analysis first.")
            return

        out_dir = QFileDialog.getExistingDirectory(
            self, "Choose Export Folder", os.path.expanduser("~")
        )
        if not out_dir:
            return

        try:
            exporter = Exporter(out_dir)
            paths = exporter.export_all(
                self._last_result,
                self._symbol_table,
                self._current_file,
            )
            names = ", ".join(os.path.basename(p) for p in paths.values())
            self._set_status(f"Export successful → {names}")
            QMessageBox.information(
                self, "Export Successful",
                f"Files written to:\n{out_dir}\n\n" + "\n".join(paths.values())
            )
        except OSError as exc:
            QMessageBox.critical(self, "Export Error", str(exc))

    def _toggle_theme(self):
        self._dark_mode = not self._dark_mode
        self._apply_theme()
        label = "☀  Light Mode" if not self._dark_mode else "🌙  Dark Mode"
        self._act_theme.setText(label)
        mode_name = "dark" if self._dark_mode else "light"
        self._highlighter.set_theme(mode_name)
        self._set_status(f"Switched to {'dark' if self._dark_mode else 'light'} theme.")

    # ══════════════════════════════════════════
    # TABLE POPULATION
    # ══════════════════════════════════════════

    def _populate_token_table(self, result: LexerResult):
        tbl = self._token_table
        tbl.setRowCount(0)
        tbl.setRowCount(len(result.tokens))
        dark = self._dark_mode

        for row, tok in enumerate(result.tokens):
            colour = token_type_colour(tok.token_type, dark)

            items = [
                self._item(truncate(tok.lexeme, 35)),
                self._item(tok.token_type),
                self._item(str(tok.line), align=Qt.AlignmentFlag.AlignCenter),
            ]
            for col, item in enumerate(items):
                if col == 1:   # colour the token-type cell
                    item.setForeground(QColor(colour))
                    item.setFont(self._mono_font())
                tbl.setItem(row, col, item)

        tbl.resizeColumnsToContents()

    def _populate_symbol_table(self, result: LexerResult):
        tbl = self._sym_table_widget
        tbl.setRowCount(0)
        tbl.setRowCount(len(result.symbol_table))

        for row, entry in enumerate(result.symbol_table):
            tbl.setItem(row, 0, self._item(entry.name))
            tbl.setItem(row, 1, self._item(entry.category))
            tbl.setItem(row, 2, self._item(
                str(entry.line), align=Qt.AlignmentFlag.AlignCenter))

        tbl.resizeColumnsToContents()

    def _populate_error_table(self, result: LexerResult):
        tbl = self._error_table
        tbl.setRowCount(0)
        tbl.setRowCount(len(result.errors))
        c = DARK if self._dark_mode else LIGHT

        for row, err in enumerate(result.errors):
            e_item = self._item(err.error_type)
            e_item.setForeground(QColor(c['error']))
            tbl.setItem(row, 0, e_item)
            tbl.setItem(row, 1, self._item(err.description))
            tbl.setItem(row, 2, self._item(
                str(err.line), align=Qt.AlignmentFlag.AlignCenter))

        tbl.resizeColumnsToContents()

    # ══════════════════════════════════════════
    # STATS
    # ══════════════════════════════════════════

    def _update_stats(self, result: LexerResult):
        self._sc_tokens.set_value(result.total_tokens)
        self._sc_keywords.set_value(result.total_keywords)
        self._sc_identifiers.set_value(result.total_identifiers)
        self._sc_numbers.set_value(result.total_numbers)
        self._sc_operators.set_value(result.total_operators)
        self._sc_delimiters.set_value(result.total_delimiters)
        self._sc_errors.set_value(result.total_errors)

    def _reset_stats(self):
        for card in (self._sc_tokens, self._sc_keywords, self._sc_identifiers,
                     self._sc_numbers, self._sc_operators, self._sc_delimiters,
                     self._sc_errors):
            card.set_value(0)

    # ══════════════════════════════════════════
    # THEME
    # ══════════════════════════════════════════

    def _apply_theme(self):
        QApplication.instance().setStyleSheet(
            build_stylesheet(self._dark_mode)
        )
        # Update stat-card accent colours
        c = DARK if self._dark_mode else LIGHT
        accents = [
            c['accent'], c['token_kw'], c['token_str'],
            c['token_num'], c['text_muted'], c['warning'], c['error'],
        ]
        cards = [
            self._sc_tokens, self._sc_keywords, self._sc_identifiers,
            self._sc_numbers, self._sc_operators, self._sc_delimiters,
            self._sc_errors,
        ]
        for card, acc in zip(cards, accents):
            card.set_accent(acc)

    # ══════════════════════════════════════════
    # HELPERS
    # ══════════════════════════════════════════

    @staticmethod
    def _make_table(headers: list) -> QTableWidget:
        """Create a styled, read-only QTableWidget."""
        tbl = QTableWidget()
        tbl.setColumnCount(len(headers))
        tbl.setHorizontalHeaderLabels(headers)
        tbl.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        tbl.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        tbl.setAlternatingRowColors(True)
        tbl.verticalHeader().setDefaultSectionSize(28)
        tbl.verticalHeader().setVisible(False)
        tbl.horizontalHeader().setStretchLastSection(True)
        tbl.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Interactive
        )
        tbl.setSortingEnabled(True)
        return tbl

    @staticmethod
    def _wrap(widget: QWidget) -> QWidget:
        """Wrap a widget in a container with small margins."""
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.addWidget(widget)
        return container

    @staticmethod
    def _item(text: str,
              align: Qt.AlignmentFlag = Qt.AlignmentFlag.AlignLeft
              ) -> QTableWidgetItem:
        item = QTableWidgetItem(text)
        item.setTextAlignment(
            align | Qt.AlignmentFlag.AlignVCenter  # type: ignore[operator]
        )
        return item

    @staticmethod
    def _mono_font() -> QFont:
        f = QFont("JetBrains Mono, Cascadia Code, Consolas, Courier New")
        f.setPointSize(11)
        return f

    def _set_status(self, msg: str, timeout: int = 0):
        """Show *msg* in the status bar. timeout=0 means permanent."""
        self._status_msg.setText(msg)

    def _update_cursor_pos(self):
        cursor = self._editor.textCursor()
        line = cursor.blockNumber() + 1
        col  = cursor.columnNumber() + 1
        self._line_col_lbl.setText(f"Ln {line}, Col {col}")
