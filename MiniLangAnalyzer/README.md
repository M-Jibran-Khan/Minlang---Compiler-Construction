# MiniLang Analyzer
### Visual Lexical Analysis Tool
**CS3510 — Compiler Construction | Option B: Lexical Analysis**

---

## Overview

MiniLang Analyzer is a fully interactive desktop application that performs **lexical analysis** on source code written in C, C++, Python, or plain text. It is built with **Python 3.12+** and **PyQt6**.

The tool tokenises input source code in real time, populates a symbol table, detects lexical errors, and presents the results in a professional IDE-like interface with syntax highlighting and dark/light mode support.

---

## Features

| Feature | Description |
|---|---|
| **Source Code Editor** | Syntax-highlighted editor with line/column tracking |
| **Token Stream Table** | Every token with lexeme, type, and line number |
| **Symbol Table** | Unique identifiers with category and first-seen line |
| **Error Detection** | Invalid characters, bad identifiers, unclosed strings |
| **Statistics Dashboard** | Live counts for all token categories |
| **Dark / Light Mode** | Toggle with one click or Ctrl+D |
| **Export Results** | tokens.txt, symbol_table.txt, analysis_report.txt |
| **Open Files** | Load .c, .cpp, .py, .txt source files |

---

## Project Structure

```
MiniLangAnalyzer/
├── main.py               ← Entry point — run this
├── gui.py                ← MainWindow, widgets, layout
├── lexer.py              ← Tokenizer & error detection
├── syntax_highlighter.py ← QSyntaxHighlighter subclass
├── symbol_table.py       ← Symbol table manager
├── exporter.py           ← File export (txt reports)
├── utils.py              ← Stylesheets, colour tokens, helpers
├── requirements.txt      ← Python dependencies
└── README.md             ← This file
```

---

## Installation

### 1. Prerequisites
- Python **3.12** or newer
- pip (bundled with Python)

### 2. Install Dependencies

Open a terminal in the project folder and run:

```bash
pip install -r requirements.txt
```

> On some Linux systems you may need:
> ```bash
> pip install --break-system-packages -r requirements.txt
> ```

### 3. Run the Application

```bash
python main.py
```

---

## Usage Guide

### Analysing Code
1. **Type** source code in the editor, **or** click **📂 Open File** to load a `.c`, `.cpp`, `.py`, or `.txt` file.
2. Press **F5** or click **▶ Analyze**.
3. Results appear instantly in the three tabs at the bottom right.

### Reading Results
| Tab | Contents |
|---|---|
| 🔑 Token Stream | All tokens in order: lexeme, type, line |
| 📋 Symbol Table | All unique identifiers |
| ⚠ Errors | Lexical errors with type, description, and line |

### Exporting
1. Click **💾 Export**.
2. Choose a destination folder.
3. Three files are written:
   - `tokens.txt` — full token stream
   - `symbol_table.txt` — all identifiers
   - `analysis_report.txt` — combined report with statistics

### Keyboard Shortcuts
| Shortcut | Action |
|---|---|
| `F5` | Run analysis |
| `Ctrl+O` | Open file |
| `Ctrl+L` | Clear editor |
| `Ctrl+E` | Export results |
| `Ctrl+D` | Toggle dark/light mode |

---

## Recognised Tokens

### Keywords
`int` `float` `double` `char` `string` `bool` `if` `else` `for` `while`
`return` `break` `continue` `class` `public` `private` `void`
`true` `false` `null` `new` `this` `static`

### Operators
`+` `-` `*` `/` `%` `=` `==` `!=` `<` `>` `<=` `>=` `&&` `||` `!`
`++` `--` `->` `+=` `-=` `*=` `/=` `%=`

### Delimiters
`; , ( ) { } [ ]`

---

## Error Detection

| Error Type | Example |
|---|---|
| Invalid Character | `@` `#` `$` |
| Invalid Identifier | `2abc` `3name` |
| Unclosed String | `"hello world` |
| Unknown Symbol | Any unrecognised character |

---

## Technology Stack

- **Python 3.12+**
- **PyQt6** — GUI framework (QMainWindow, QTextEdit, QTableWidget, QSplitter, QTabWidget, QSyntaxHighlighter)
- **re** (standard library) — Regular-expression tokenisation
- **dataclasses** (standard library) — Clean data structures

---

## Author

**Course:** CS3510 — Compiler Construction  
**Project:** Option B — Lexical Analysis  
**Tool:** MiniLang Analyzer v1.0
