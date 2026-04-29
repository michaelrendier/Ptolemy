#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Ptolemy — System Tray Icon (Power Button)
==========================================
Pharos Face

Right-click menu:
  ┌─────────────────────────────┐
  │ ⚙  Settings                 │
  │ ─────────────────────────── │
  │ SENSORS                     │
  │   ● GPS           (active)  │
  │   ○ KVM           (grey)    │
  │   ○ Accelerometer (grey)    │
  │   ... (all Tesla sensors)   │
  │ ─────────────────────────── │
  │    Hide                     │
  │    Exit                     │
  └─────────────────────────────┘

Sensor items:
  - Always listed (discovered from PtolemySettings)
  - Green dot + enabled  → active stream incoming
  - Grey dot + greyed    → no stream / stub
  - Clicking a sensor item opens Sensor Settings in SettingsWindow
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QAction, QMenu, QApplication
from PyQt5.QtGui     import QIcon, QColor
from PyQt5.QtCore    import Qt

from Pharos.ptolemy_settings import PtolemySettings


class SystemTrayIcon(QSystemTrayIcon):

    def __init__(self, icon, parent=None):
        super().__init__(icon, parent)
        self.Ptolemy = parent
        self._settings_engine = PtolemySettings()
        self._settings_engine.scan()
        self._settings_window = None

        self._build_menu()
        self.activated.connect(self._on_activated)

    # ── Menu build ────────────────────────────────────────────────────────────

    def _build_menu(self):
        menu = QMenu()

        # Settings
        settings_action = QAction("⚙  Settings", menu)
        settings_action.triggered.connect(self._open_settings)
        menu.addAction(settings_action)

        menu.addSeparator()

        # Sensor router section
        sensor_header = QAction("SENSORS", menu)
        sensor_header.setEnabled(False)
        menu.addAction(sensor_header)

        self._sensor_actions = {}
        for sid, info in self._settings_engine.sensor_inputs.items():
            active = info.get("active", False)
            label  = info.get("label", sid)
            dot    = "●  " if active else "○  "
            act    = QAction(dot + label, menu)
            act.setEnabled(active)   # greyed out unless stream active
            act.triggered.connect(lambda checked, s=sid: self._open_sensor_settings(s))
            menu.addAction(act)
            self._sensor_actions[sid] = act

        menu.addSeparator()

        # Hide / Show
        hide_action = QAction("Hide", menu)
        hide_action.triggered.connect(self.Ptolemy.hideShow)
        menu.addAction(hide_action)

        # Exit
        exit_action = QAction("Exit", menu)
        exit_action.triggered.connect(QApplication.quit)
        menu.addAction(exit_action)

        self.setContextMenu(menu)

    # ── Actions ───────────────────────────────────────────────────────────────

    def _open_settings(self):
        from Pharos.settings_window import PtolemySettingsWindow
        if self._settings_window is None:
            self._settings_window = PtolemySettingsWindow()
        self._settings_window.show()
        self._settings_window.raise_()

    def _open_sensor_settings(self, sensor_id: str):
        from Pharos.settings_window import PtolemySettingsWindow
        if self._settings_window is None:
            self._settings_window = PtolemySettingsWindow()
        # Switch sidebar to Inputs section
        self._settings_window._input_list.setCurrentRow(
            list(self._settings_engine.sensor_inputs.keys()).index(sensor_id)
        )
        self._settings_window.show()
        self._settings_window.raise_()

    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # left click
            if self.Ptolemy:
                self.Ptolemy.hideShow()

    # ── Stream notification API (called by Tesla SensorStream) ───────────────

    def notify_sensor_active(self, sensor_id: str, active: bool):
        """
        Called by Tesla face when a sensor stream starts or stops.
        Updates the tray menu dot and enable state in-place.
        """
        self._settings_engine.mark_sensor_active(sensor_id, active)
        if sensor_id in self._sensor_actions:
            info  = self._settings_engine.sensor_inputs.get(sensor_id, {})
            label = info.get("label", sensor_id)
            dot   = "●  " if active else "○  "
            act   = self._sensor_actions[sensor_id]
            act.setText(dot + label)
            act.setEnabled(active)
