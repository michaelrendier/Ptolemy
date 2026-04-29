#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

"""
Ptolemy3.py — Integration Kernel v3.0
======================================
Architecture:
    Ptolemy   — QMainWindow shell, singletons, scene substrate
    PtolBus   — Face registry, thread lifecycle, suspend/resume
    PGui      — PWindow chrome, QGraphicsProxyWidget management (Pharos/PGui.py)
    PtolVispy — VisPy GL canvas helper (defined below)

    All networking and device interfacing lives in Tesla:
        Tesla.HolePunch  — UDP NAT traversal, rendezvous relay, GPS data channel
        Tesla.KVM        — Fake KVM: mouse/kb structs over punched UDP socket
        Tesla.Sockets    — Base UDP/TCP layer
        Tesla.KVMServer  — Remote receiver (python-xlib / uinput application)

Render strategy:
    QGraphicsScene   — primary desktop, all PWindows live here (~10^3 items)
    VisPy/OpenGL     — injected as QGraphicsProxyWidget for data-dense faces
                       (Alexandria, Archimedes spectrograph, Noether plots)
                       GPU-side VBO rendering: 10^6+ primitives at 60fps
                       QGraphicsScene handles chrome only; VisPy handles pixels

Threading contract:
    Each Face launched through PtolBus gets:
        face._ptol_thread  — QThread driving the face's work loop
        face._ptol_timers  — list of QTimers owned by the face
    PtolBus.suspend(id)  → thread.quit() + timer.stop() for each
    PtolBus.resume(id)   → thread.start() + timer.start() for each
    PtolBus.terminate(id)→ suspend + thread.wait() + del
    Faces not visible are NOT processing. No exceptions.
"""

# ── Standard library ──────────────────────────────────────────────────────────
import sys
import os
import time
import inspect
import importlib
import struct
from subprocess import Popen, PIPE

# ── PyQt5 ─────────────────────────────────────────────────────────────────────
from PyQt5.QtCore    import Qt, QTimer, QThread, pyqtSignal, QObject, QRect
from PyQt5.QtGui     import QBrush, QColor, QPen, QFont, QIcon, QPixmap
from PyQt5.QtSvg     import QSvgWidget
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QGraphicsScene,
                              QGraphicsView, QGraphicsProxyWidget, QFrame,
                              QDesktopWidget, QGridLayout)

# ── Ptolemy core modules ───────────────────────────────────────────────────────
from Callimachus.Database      import Database
from Pharos.Dialogs            import Dialogs
from Pharos.SystemTrayIcon     import SystemTrayIcon
from Pharos.UtilityFunctions   import cmdline
from Pharos.Menu               import Menu
from Pharos.Interface          import User
from urllib.request            import build_opener

# ── Tesla — all interfacing ────────────────────────────────────────────────────
from Tesla.HolePunch           import HolePunch
from Tesla.KVM                 import KVMClient


# ══════════════════════════════════════════════════════════════════════════════
#  PtolBus — Face lifecycle manager
# ══════════════════════════════════════════════════════════════════════════════

class PtolBus(QObject):
    """
    Central integration bus. Owns the face registry and enforces the
    threading contract: faces not on screen are not processing.

    Usage:
        window = self.bus.launch(TreasureHunt)        # inline, threaded
        self.bus.suspend(window.face_id)              # minimize → pause
        self.bus.resume(window.face_id)               # restore → unpause
        self.bus.terminate(window.face_id)            # close → destroy
    """

    face_launched   = pyqtSignal(str)     # face_id
    face_suspended  = pyqtSignal(str)
    face_resumed    = pyqtSignal(str)
    face_terminated = pyqtSignal(str)

    def __init__(self, ptolemy):
        super().__init__(ptolemy)
        self.Ptolemy  = ptolemy
        self._registry = {}               # face_id → FaceRecord
        self._counter  = 0

    # ── Launch ────────────────────────────────────────────────────────────────

    def launch(self, face_cls, *args, use_vispy=False, **kwargs):
        """
        Instantiate a Face and wrap it in a PWindow on the scene.
        Returns the PWindow item.
        face_cls must accept parent=Ptolemy as first kwarg.
        If use_vispy=True, expects face_cls to return a VisPy canvas;
        wraps it as QGraphicsProxyWidget(canvas.native) instead.
        """
        from Pharos.PGui import PWindow           # lazy — PGui not written yet

        face_id = f"{face_cls.__name__}_{self._counter}"
        self._counter += 1

        # Instantiate the face
        face = face_cls(*args, parent=self.Ptolemy, **kwargs)

        # Collect timers declared by the face (convention: face._ptol_timers)
        timers = getattr(face, '_ptol_timers', [])

        # Collect thread declared by the face (convention: face._ptol_thread)
        thread = getattr(face, '_ptol_thread', None)

        # Wrap in PWindow chrome on the scene
        if use_vispy:
            native = face.native          # VisPy canvas native Qt widget
            pwin = PWindow(native, title=face_cls.__name__,
                           face_id=face_id, bus=self,
                           ptolemy=self.Ptolemy)
        else:
            pwin = PWindow(face, title=face_cls.__name__,
                           face_id=face_id, bus=self,
                           ptolemy=self.Ptolemy)

        self.Ptolemy.scene.addItem(pwin)

        self._registry[face_id] = {
            'face':    face,
            'pwin':    pwin,
            'thread':  thread,
            'timers':  timers,
            'state':   'running',
            'cls':     face_cls.__name__,
        }

        self.face_launched.emit(face_id)
        return pwin

    # ── Launch subprocess (legacy / standalone mode) ──────────────────────────

    def launch_subprocess(self, script_path, *args):
        """
        For faces not yet integrated inline (legacy subprocess path).
        Returns Popen handle. No suspend/resume — process-level only.
        """
        cmd = ['python3', script_path] + list(args)
        proc = Popen(cmd, stdout=PIPE, stderr=PIPE)
        face_id = f"subprocess_{os.path.basename(script_path)}_{self._counter}"
        self._counter += 1
        self._registry[face_id] = {
            'face':   None,
            'pwin':   None,
            'thread': None,
            'timers': [],
            'state':  'subprocess',
            'proc':   proc,
            'cls':    script_path,
        }
        return proc

    # ── Import helper — dynamic face loading ──────────────────────────────────

    def import_face(self, module_path, class_name):
        """
        Dynamically import a Face class by dotted module path.
        Example: bus.import_face('Phaleron.TreasureHunt.TreasureHunt', 'TreasureHunt')
        Returns the class. Caches the import.
        """
        mod = importlib.import_module(module_path)
        return getattr(mod, class_name)

    # ── Suspend / Resume / Terminate ─────────────────────────────────────────

    def suspend(self, face_id):
        """Pause all processing for a face (minimize). Thread-safe."""
        rec = self._registry.get(face_id)
        if not rec or rec['state'] != 'running':
            return
        if rec['thread']:
            rec['thread'].quit()
        for timer in rec['timers']:
            timer.stop()
        rec['state'] = 'suspended'
        self.face_suspended.emit(face_id)

    def resume(self, face_id):
        """Resume processing for a face (restore from minimize)."""
        rec = self._registry.get(face_id)
        if not rec or rec['state'] != 'suspended':
            return
        if rec['thread']:
            rec['thread'].start()
        for timer in rec['timers']:
            timer.start()
        rec['state'] = 'running'
        self.face_resumed.emit(face_id)

    def terminate(self, face_id):
        """Fully destroy a face and remove its PWindow from the scene."""
        rec = self._registry.get(face_id)
        if not rec:
            return

        # Subprocess path
        if rec['state'] == 'subprocess':
            proc = rec.get('proc')
            if proc:
                proc.terminate()
            del self._registry[face_id]
            return

        # Inline path
        self.suspend(face_id)
        if rec['thread']:
            rec['thread'].wait(2000)        # 2s grace period

        pwin = rec.get('pwin')
        if pwin and pwin.scene():
            self.Ptolemy.scene.removeItem(pwin)

        face = rec.get('face')
        if face:
            try:
                face.deleteLater()
            except Exception:
                pass

        del self._registry[face_id]
        self.face_terminated.emit(face_id)

    # ── Status ────────────────────────────────────────────────────────────────

    def status(self):
        return {fid: {'cls': r['cls'], 'state': r['state']}
                for fid, r in self._registry.items()}



# ══════════════════════════════════════════════════════════════════════════════
#  PtolVispy — VisPy GL canvas integration helper
# ══════════════════════════════════════════════════════════════════════════════

class PtolVispy:
    """
    Mixin/helper for faces that use VisPy for GPU-accelerated rendering.

    Why VisPy for data-dense faces:
        QGraphicsScene handles ~10^3 items before frame rate degrades.
        VisPy renders directly to OpenGL via VBO — 10^6+ primitives at 60fps.
        Working proof: working/vispy-test-2.py renders 320,000 vertices
        (16×20 signals × 1000 samples) in real time with GLSL clipping.

    Architecture:
        VisPy canvas → renders data/geometry to OpenGL surface
        canvas.native → the underlying Qt widget
        QGraphicsProxyWidget(canvas.native) → sits on QGraphicsScene
        PWindow wraps the proxy → chrome, suspend, close

    Faces that benefit: Alexandria (Earth/Core), Archimedes (spectrograph,
    Noether current plots), Mouseion (GLViewer), any future graph-dense UI.

    Usage in a Face:
        class AlexandriaGl(QWidget, PtolVispy):
            def __init__(self, parent):
                super().__init__(parent)
                self.canvas = self.make_vispy_canvas(size=(800, 600))
                layout = QVBoxLayout(self)
                layout.addWidget(self.canvas.native)
                # Implement on_draw, on_resize on self.canvas

    Or full-GL face launched via bus:
        pwin = ptolemy.bus.launch(AlexandriaGl, use_vispy=True)
        # bus.launch with use_vispy=True proxies canvas.native directly
    """

    @staticmethod
    def make_vispy_canvas(size=(800, 600), title='', keys='interactive'):
        """Return a VisPy canvas configured for Qt5 backend embedding."""
        try:
            import vispy
            vispy.use('PyQt5')
            from vispy import app
            canvas = app.Canvas(size=size, title=title, keys=keys, show=False)
            return canvas
        except ImportError:
            raise RuntimeError(
                'VisPy not installed. '
                'pip install vispy --break-system-packages')

    @staticmethod
    def add_vispy_to_scene(scene, canvas, x=0, y=0):
        """
        Embed a VisPy canvas.native into a QGraphicsScene as a proxy widget.
        Returns the QGraphicsProxyWidget.
        """
        proxy = scene.addWidget(canvas.native)
        proxy.setPos(x, y)
        return proxy


# ══════════════════════════════════════════════════════════════════════════════
#  Ptolemy — Main window shell (v3.0)
# ══════════════════════════════════════════════════════════════════════════════

class Ptolemy(QMainWindow):
    """
    Integration kernel. Owns the scene, singletons, and the bus.
    Does not own faces — the bus does.
    Does not drive face logic — faces drive themselves.

    Faces launch via:
        self.bus.launch(FaceClass)             # inline, integrated
        self.bus.launch_subprocess(path)       # legacy subprocess
        self.bus.import_face(module, cls)      # dynamic import then launch
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        # ── Paths ─────────────────────────────────────────────────────────────
        self.homeDir   = '/home/rendier/Ptolemy/'
        self.mediaDir  = self.homeDir + 'media/'
        self.imgDir    = self.homeDir + 'images/'
        self.pharosImg = self.imgDir  + 'Pharos/'
        self.screen    = QDesktopWidget().screenGeometry()

        # ── Scene / View ──────────────────────────────────────────────────────
        self._setup_scene()

        # ── Identity ──────────────────────────────────────────────────────────
        self.name     = 'Πτολεμαῖος Φιλάδελφος'
        self.user     = Popen('whoami',  stdout=PIPE, shell=True).communicate()[0][:-1]
        self.platform = Popen('uname -o',stdout=PIPE, shell=True).communicate()[0][:-1]
        self.nodename = Popen('uname -n',stdout=PIPE, shell=True).communicate()[0][:-1]

        # ── Stylesheet ────────────────────────────────────────────────────────
        self.stylesheet = self._build_stylesheet()

        # ── Core singletons ───────────────────────────────────────────────────
        self.db       = Database(parent=self)
        self.dialogs  = Dialogs(parent=self)
        self.opener   = build_opener()
        self.opener.addheaders = [
            ('User-agent',           'Mozilla/5.0 (X11; Linux x86_64)'),
            ('Accept',               'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),
            ('Accept-Language',      'en-US,en;q=0.9'),
            ('Upgrade-Insecure-Requests', '1'),
        ]

        # ── Integration bus ───────────────────────────────────────────────────
        self.bus = PtolBus(self)

        # ── Network layer ─────────────────────────────────────────────────────
        self.hole_punch = HolePunch(self)
        self.kvm        = KVMClient(self)

        # ── System tray ───────────────────────────────────────────────────────
        self.sysTrayIcon = SystemTrayIcon(
            QIcon(self.imgDir + 'Pharos/indicator-ball.gif'), parent=self)
        self.sysTrayIcon.show()

        # ── Command history ───────────────────────────────────────────────────
        self.cmdhistory = []

        # ── UI ────────────────────────────────────────────────────────────────
        self._init_ui()

    # ── Scene setup ───────────────────────────────────────────────────────────

    def _setup_scene(self):
        w, h = self.screen.width(), self.screen.height()

        self._form = QWidget(self)
        self._form.setContentsMargins(0, 0, 0, 0)
        layout = QGridLayout(self._form)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        self.scene = QGraphicsScene(0, 0, w, h)
        self.view  = QGraphicsView(self._form)
        self.view.setScene(self.scene)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setFrameShape(QFrame.NoFrame)
        self.view.setBackgroundBrush(QBrush(QColor('black')))
        self.view.setInteractive(True)
        self.view.setContentsMargins(0, 0, 0, 0)
        self.view.setGeometry(self.screen)

        self._form.setGeometry(self.screen)
        self.setCentralWidget(self._form)
        self.setGeometry(self.screen)
        self.setWindowTitle('Πτολεμαῖος Φιλάδελφος')
        self.setWindowIcon(QIcon(self.imgDir + 'ptol.svg'))

    # ── UI init ───────────────────────────────────────────────────────────────

    def _init_ui(self):
        self.setStyleSheet(self.stylesheet)

        # Philadelphos must exist before Interface tries to bind setOutput
        self._launch_philadelphos()

        # Pharos nav interface (always present)
        self.Interface = User(self)
        self.scene.addWidget(self.Interface)

        # Menu (always present)
        self.Menu = Menu(parent=self)
        self.scene.addWidget(self.Menu)

    def _launch_philadelphos(self):
        """
        Philadelphos is the AI/command layer. Launch inline if available,
        subprocess fallback otherwise.
        """
        try:
            from Philadelphos.Phila import Phila
            self.Philadelphos = Phila(self)
            self.scene.addWidget(self.Philadelphos)
        except ImportError:
            try:
                from Pharos.Philadelphos.CommandInput import Command
                self.Philadelphos = Command(self)
                self.scene.addWidget(self.Philadelphos)
            except ImportError:
                self.Philadelphos = None

    # ── Face launchers (bus delegates) ────────────────────────────────────────

    def open_face(self, module_path, class_name, *args, **kwargs):
        """
        Universal face launcher. Dynamically imports and launches any face.
        Example: self.open_face('Phaleron.TreasureHunt.TreasureHunt', 'TreasureHunt')
        """
        face_cls = self.bus.import_face(module_path, class_name)
        return self.bus.launch(face_cls, *args, **kwargs)

    def openSearch(self, event=None):
        return self.open_face(
            'Phaleron.TreasureHunt.TreasureHunt', 'TreasureHunt')

    def openNavigation(self, event=None):
        return self.open_face('Anaximander.Navigation', 'Navigation')

    def openCore(self, event=None):
        from Mouseion.GLViewer import Viewer
        from Alexandria.Core   import Core
        return self.bus.launch(Viewer, Core, self)

    def openEarth(self, event=None):
        from Mouseion.GLViewer import Viewer
        from Alexandria.Earth  import Earth
        return self.bus.launch(Viewer, Earth, rotate=True)

    def openWikiGroup(self, event=None):
        return self.open_face('Mouseion.WikiGroup', 'WikiGroup')

    def openLibrary(self, event=None):
        return self.open_face('Mouseion.Library', 'Library')

    def openNotepad(self, event=None):
        return self.open_face('Phaleron.Notepad', 'Notepad')

    def openDbCPanel(self, event=None):
        return self.open_face('Callimachus.DBControlPanel', 'DBControlPanel')

    def openGraphPlot(self, event=None):
        from Archimedes.Maths.GraphPlot import GraphPlot
        return self.bus.launch(GraphPlot)

    # ── Network launchers ─────────────────────────────────────────────────────

    def punch_to(self, peer_id, relay_host=None, relay_port=None):
        """Initiate hole punch. Connect kvm on success."""
        self.hole_punch.punch_ready.connect(self._on_punch_ready)
        self.hole_punch.punch_failed.connect(self._on_punch_failed)
        self.hole_punch.punch(peer_id, relay_host, relay_port)

    def _on_punch_ready(self, ip, port):
        self.kvm.connect(ip, port, sock=self.hole_punch.sock)
        # TreasureHunt VNC fallback URL (configure per deployment)
        self.kvm.vnc_url = None   # e.g. 'http://host:6080/vnc.html'

    def _on_punch_failed(self, reason):
        print(f'[Tesla/KVM] Hole punch failed: {reason}')
        vnc_url = self.kvm.open_vnc_fallback()
        if vnc_url:
            self._open_vnc_in_browser(vnc_url)

    def _open_vnc_in_browser(self, url):
        """Route VNC fallback URL to TreasureHunt tab via bus."""
        for rec in self.bus._registry.values():
            if rec['cls'] == 'TreasureHunt' and rec['state'] == 'running':
                face = rec.get('face')
                if face and hasattr(face, 'add_new_tab'):
                    face.add_new_tab(url, 'VNC Fallback')
                    return

    # ── Qt primitives ─────────────────────────────────────────────────────────

    def pen(self, color, width=1):
        p = QPen(QColor(color))
        p.setWidth(width)
        p.setCapStyle(Qt.FlatCap)
        return p

    def brush(self, color):
        return QBrush(QColor(color))

    def font(self, size=10):
        return QFont('Ubuntu Mono', size)

    def cwd(self):
        return os.getcwd()

    def sysTime(self):
        t = time.localtime()
        return f'{t[3]:02d}:{t[4]:02d}:{t[5]:02d}'

    def sysDate(self):
        t = time.localtime()
        return f'{t[2]:02d}.{t[1]:02d}.{str(t[0])[2:]}'

    def timeStamp(self):
        return [self.sysDate(), self.sysTime()]

    def cronJob(self, interval_ms, job):
        cron = QTimer(self)
        cron.setInterval(interval_ms)
        try:
            cron.timeout.connect(job)
        except TypeError:
            pass
        cron.start()
        return cron

    # ── Stylesheet ────────────────────────────────────────────────────────────

    def _build_stylesheet(self):
        return (
            "QMainWindow { background-color: black; color: white } "
            "QWidget { background-color: black; color: white } "
            "QMenuBar { border: 1px solid white; background-color: black; color: white } "
            "QMenuBar::item { background-color: black; color: white } "
            "QToolBar { border: 1px solid white; background-color: black; color: white } "
            "QStatusBar { border: 1px solid white; background-color: black; color: white } "
            "QTabWidget { border: 1px solid white; background-color: black; color: white } "
            "QTabBar::tab { border: 1px solid white; background-color: black; color: white } "
            "QComboBox { border: 1px solid white; background-color: #333; color: white } "
            "QPushButton { border: 1px solid #00ffff; background-color: black; color: #00ffff } "
            "QPushButton:hover { border: 1px solid #0055ff; color: #0055ff } "
            "QLineEdit { border: 1px solid white; background-color: #111; color: white } "
            "QDockWidget { border: 1px solid white; background-color: black; color: white } "
            "QTableWidget { background-color: black; color: white } "
            "QTableWidget::item:focus { border: 1px solid white; background-color: #003 } "
            "QHeaderView::section { background-color: #001a33; color: white } "
            "QTextBrowser { border: 1px solid black; background-color: white; color: black } "
            "QListWidget { background-color: #111; color: white } "
            "QLabel { border: 0px } "
        )

    # ── Events ────────────────────────────────────────────────────────────────

    def closeEvent(self, event):
        # Terminate all faces cleanly
        for fid in list(self.bus._registry.keys()):
            self.bus.terminate(fid)
        self.kvm.disconnect()
        self.hole_punch.close()
        event.accept()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            pass

    def mousePressEvent(self, event):
        item = self.view.itemAt(event.x(), event.y())
        if self.Philadelphos and hasattr(self.Philadelphos, 'setOutput'):
            self.Philadelphos.setOutput(str(item), speak=False)
        self._aniclick(event)

    def _aniclick(self, event):
        pen = self.pen('white', 2)
        brush = self.brush('black')
        x, y = event.x(), event.y()
        c1 = self.scene.addEllipse(x-10, y-10, 20,  20,  pen, brush)
        c2 = self.scene.addEllipse(x-20, y-20, 40,  40,  pen, brush)
        c3 = self.scene.addEllipse(x-30, y-30, 60,  60,  pen, brush)
        self.scene.removeItem(c1)
        self.scene.removeItem(c2)
        QTimer.singleShot(150, lambda: self._safe_remove(c3))

    def _safe_remove(self, item):
        if item.scene():
            self.scene.removeItem(item)

    def hideShow(self):
        if self.isVisible():
            self.hide()
        else:
            self.show()


# ══════════════════════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════════════════════

def main():
    app = QApplication(sys.argv)
    app.setApplicationName('Ptolemy III')

    ptol = Ptolemy()
    ptol.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
