#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'
# PtolShell — lightweight in-scene terminal widget
# Sits beside Pharos on Windows/Menu key raise

from PyQt5.QtCore import Qt, QProcess, pyqtSignal
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLineEdit


class PtolShell(QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('PtolShell')
        self.setFixedSize(420, 280)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        self._focused = False

        font = QFont('Monospace', 9)

        self.output = QTextEdit(self)
        self.output.setReadOnly(True)
        self.output.setFont(font)
        self.output.setStyleSheet(
            "background: rgba(0,0,0,210); color: #00ff88; border: 1px solid #333;")

        self.input = QLineEdit(self)
        self.input.setFont(font)
        self.input.setStyleSheet(
            "background: rgba(0,0,0,230); color: #00ff88; border-top: 1px solid #444;")
        self.input.setPlaceholderText('ptolemy > ')
        self.input.returnPressed.connect(self._run)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self.output)
        layout.addWidget(self.input)

        self._proc = QProcess(self)
        self._proc.readyReadStandardOutput.connect(self._on_stdout)
        self._proc.readyReadStandardError.connect(self._on_stderr)

        self._write('PtolShell ready.\n', '#888888')

    # ── focus opacity (called by scene's focusItemChanged) ──────────────────

    def set_focused(self, focused: bool):
        self._focused = focused
        self.setWindowOpacity(1.0 if focused else 0.30)

    # ── internal ─────────────────────────────────────────────────────────────

    def _run(self):
        cmd = self.input.text().strip()
        if not cmd:
            return
        self._write(f'> {cmd}\n', '#00ccff')
        self.input.clear()
        self._proc.start('/bin/bash', ['-c', cmd])

    def _on_stdout(self):
        data = bytes(self._proc.readAllStandardOutput()).decode('utf-8', errors='replace')
        self._write(data, '#00ff88')

    def _on_stderr(self):
        data = bytes(self._proc.readAllStandardError()).decode('utf-8', errors='replace')
        self._write(data, '#ff5555')

    def _write(self, text: str, color: str = '#00ff88'):
        self.output.setTextColor(QColor(color))
        self.output.insertPlainText(text)
        self.output.ensureCursorVisible()
