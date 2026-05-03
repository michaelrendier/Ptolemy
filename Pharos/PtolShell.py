#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

# PtolShell — QTermWidget-backed shell with MetaPrompt mode routing
#
# MetaPrompt modes (commit on Enter):
#   (none) → Ptolemy C/O   — Commandow handler        — color: ROYAL_BLUE
#   >>>    → Python3 REPL  — python3 pty               — color: GREEN
#   $      → System C/O   — bash pty                  — color: YELLOW
#   #      → Root C/O     — bash pty (root)            — color: RED
#   @Name  → Face C/O     — Face speaks in shell       — color: Face color
#            e.g. @Archimedes: index rebuild complete
#            Face → Face: @Callimachus→@Archimedes: index ready
#
# QTermWidget owns ALL display, pty, ANSI, interactive programs.
# Mode detector intercepts only the input bar — QTermWidget is never replaced.
#
# Faces are shell users. Daemons POST at boot (see FaceIdentity.py).

from PyQt5.QtCore    import Qt, pyqtSignal, QProcess
from PyQt5.QtGui     import QFont, QColor, QKeyEvent
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout,
                              QLineEdit, QLabel, QSizePolicy)

try:
    import QTermWidget
    _HAS_QTERM = True
except ImportError:
    _HAS_QTERM = False

try:
    from Pharos.FaceIdentity import get_face, ShellPrompt, DaemonIdentity
    from Pharos.PtolColor import PtolColor, ShellModeColor
    _HAS_FACE_IDENTITY = True
except ImportError:
    _HAS_FACE_IDENTITY = False

# ── Mode definitions ──────────────────────────────────────────────────────────
# prefix : (label_text, label_color, pty_program, pty_args)
# '@' is the Face mode prefix — resolved dynamically per Face name.
_MODES = {
    ''   : ('Ptolemy', '#1a2a6c', None,        None),
    '>>>': ('Python3', '#00ff66', 'python3',  ['-i']),
    '$'  : ('Shell',   '#ffcc00', '/bin/bash', []),
    '#'  : ('Root',    '#ff4444', '/bin/bash', ['--login']),
}
_DEFAULT_MODE = ''
_FACE_PREFIX  = '@'   # @Archimedes: message  or  @Callimachus→@Archimedes: msg


class PtolShell(QWidget):
    """
    In-scene Ptolemy shell.
    Input bar at bottom detects MetaPrompt prefix on Enter.
    QTermWidget above handles all pty I/O and display.
    Falls back to QProcess widget if QTermWidget not installed.
    """

    mode_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumSize(600, 360)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._mode = _DEFAULT_MODE

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Terminal area ─────────────────────────────────────────────────────
        if _HAS_QTERM:
            self._term = QTermWidget.QTermWidget()
            self._term.setColorScheme('Linux')
            self._term.setScrollBarPosition(QTermWidget.QTermWidget.NoScrollBar)
            self._term.setTerminalFont(QFont('Monospace', 10))
            self._term.startShellProgram()
            self._term.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
            layout.addWidget(self._term)
        else:
            self._term = _FallbackTerm(self)
            layout.addWidget(self._term)

        # ── Mode indicator + input bar ────────────────────────────────────────
        bar = QHBoxLayout()
        bar.setContentsMargins(2, 2, 2, 2)
        bar.setSpacing(4)

        self._mode_label = QLabel('Ptolemy')
        self._mode_label.setFixedWidth(62)
        self._mode_label.setAlignment(Qt.AlignCenter)
        self._mode_label.setFont(QFont('Monospace', 9))

        self._input = _ModeInput(self)
        self._input.setFont(QFont('Monospace', 10))
        self._input.setPlaceholderText('MetaPrompt  >>>  $  #  @FaceName')
        self._input.mode_commit.connect(self._on_commit)

        bar.addWidget(self._mode_label)
        bar.addWidget(self._input)

        bar_widget = QWidget()
        bar_widget.setLayout(bar)
        bar_widget.setStyleSheet('background: #0a0a12;')
        bar_widget.setFixedHeight(32)
        layout.addWidget(bar_widget)

        self._apply_mode_color(_DEFAULT_MODE)

    # ── Mode commit ───────────────────────────────────────────────────────────

    def _on_commit(self, text: str):
        stripped = text.strip()

        # ── Face mode: @FaceName: message  or  @Sender→@Recipient: message ──
        if stripped.startswith(_FACE_PREFIX) and _HAS_FACE_IDENTITY:
            self._dispatch_face_message(stripped)
            self._input.clear()
            return

        new_mode = _DEFAULT_MODE
        command  = stripped
        for prefix in ('>>>', '$', '#'):
            if stripped.startswith(prefix):
                new_mode = prefix
                command  = stripped[len(prefix):].strip()
                break
        if new_mode != self._mode:
            self._mode = new_mode
            self._apply_mode_color(new_mode)
            self.mode_changed.emit(new_mode)
            if new_mode != _DEFAULT_MODE:
                self._start_pty(new_mode)
            if not command:
                self._input.clear()
                return
        self._dispatch(new_mode, command)
        self._input.clear()

    def _dispatch_face_message(self, text: str):
        """
        Parse and emit a Face shell message.
        Formats:
          @Archimedes: index rebuild complete
          @Callimachus→@Archimedes: index ready
        """
        body = text[1:]  # strip leading @
        # Face → Face?
        if '→' in body or '->' in body:
            sep = '→' if '→' in body else '->'
            parts = body.split(sep, 1)
            sender_raw   = parts[0].strip().lstrip('@')
            rest         = parts[1].strip().lstrip('@') if len(parts) > 1 else ''
            colon_idx    = rest.find(':')
            recipient_raw = rest[:colon_idx].strip() if colon_idx >= 0 else rest.strip()
            message       = rest[colon_idx+1:].strip() if colon_idx >= 0 else ''
            out = ShellPrompt.face_to_face(sender_raw, recipient_raw, message)
            # color mode label with sender's color
            face = get_face(sender_raw)
            label_color = face.color if face else '#c9a227'
            self._set_transient_label(face.display if face else sender_raw, label_color)
        else:
            colon_idx  = body.find(':')
            face_name  = body[:colon_idx].strip().lstrip('@') if colon_idx >= 0 else body.strip().lstrip('@')
            message    = body[colon_idx+1:].strip() if colon_idx >= 0 else ''
            out        = ShellPrompt.face_say(face_name, message)
            face = get_face(face_name)
            label_color = face.color if face else '#c9a227'
            self._set_transient_label(face.display if face else face_name, label_color)

        if _HAS_QTERM:
            self._term.sendText(out + '\n')
        else:
            self._term.write(out + '\n')

    def _set_transient_label(self, name: str, color: str):
        """Briefly show Face name as mode label (does not persist)."""
        self._mode_label.setText(name[:10])
        self._mode_label.setStyleSheet(
            f'color: {color}; font-weight: bold; background: #0a0a12; border: 1px solid {color};')
                new_mode = prefix
                command  = stripped[len(prefix):].strip()
                break
        if new_mode != self._mode:
            self._mode = new_mode
            self._apply_mode_color(new_mode)
            self.mode_changed.emit(new_mode)
            if new_mode != _DEFAULT_MODE:
                self._start_pty(new_mode)
            if not command:
                self._input.clear()
                return
        self._dispatch(new_mode, command)
        self._input.clear()

    def _dispatch(self, mode: str, command: str):
        if not command:
            return
        if mode == _DEFAULT_MODE:
            self._ptolemy_command(command)
        else:
            if _HAS_QTERM:
                self._term.sendText(command + '\n')
            else:
                self._term.send(command)

    def _start_pty(self, mode: str):
        if not _HAS_QTERM:
            return
        _, _, program, args = _MODES[mode]
        if program:
            self._term.setShellProgram(program)
            self._term.setArgs(args or [])
            self._term.startShellProgram()

    def _ptolemy_command(self, command: str):
        try:
            from Pharos.Commandow.Commandow import Tools
            if _HAS_QTERM:
                self._term.sendText(f'# Ptolemy: {command}\n')
            else:
                self._term.write(f'Ptolemy > {command}\n', '#00ccff')
        except Exception as ex:
            if not _HAS_QTERM:
                self._term.write(f'Commandow error: {ex}\n', '#ff5555')

    def _apply_mode_color(self, mode: str):
        label, color, _, _ = _MODES.get(mode, _MODES[_DEFAULT_MODE])
        self._mode_label.setText(label)
        self._mode_label.setStyleSheet(
            f'color: {color}; font-weight: bold; background: #0a0a12; border: 1px solid {color};')
        self._input.setStyleSheet(
            f'background: #050510; color: {color}; border: 1px solid #333;')

    def set_focused(self, focused: bool):
        self.setWindowOpacity(1.0 if focused else 0.30)


# ── MetaPrompt input widget ───────────────────────────────────────────────────

class _ModeInput(QLineEdit):
    """Emits mode_commit on Enter. Does not forward keys to QTermWidget."""
    mode_commit = pyqtSignal(str)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.mode_commit.emit(self.text())
        else:
            super().keyPressEvent(event)


# ── Fallback terminal (QTermWidget not installed) ─────────────────────────────

class _FallbackTerm(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        from PyQt5.QtWidgets import QTextEdit
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._out = QTextEdit()
        self._out.setReadOnly(True)
        self._out.setFont(QFont('Monospace', 10))
        self._out.setStyleSheet('background: #050510; color: #aaffcc; border: none;')
        layout.addWidget(self._out)
        self._proc = QProcess(self)
        self._proc.readyReadStandardOutput.connect(self._on_stdout)
        self._proc.readyReadStandardError.connect(self._on_stderr)
        self.write('[QTermWidget not found — install SIP build for full pty]\n', '#ff8800')

    def send(self, command: str):
        self._proc.start('/bin/bash', ['-c', command])

    def write(self, text: str, color: str = '#aaffcc'):
        self._out.setTextColor(QColor(color))
        self._out.insertPlainText(text)
        self._out.ensureCursorVisible()

    def _on_stdout(self):
        self.write(bytes(self._proc.readAllStandardOutput()).decode('utf-8', errors='replace'))

    def _on_stderr(self):
        self.write(bytes(self._proc.readAllStandardError()).decode('utf-8', errors='replace'), '#ff5555')
