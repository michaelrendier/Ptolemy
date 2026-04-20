#!/usr/bin/python3
# -*- coding: utf-8 -*-
__author__ = 'rendier'

"""
Ptolemy3.py — Integration Kernel v3.0
======================================
Architecture:
    Ptolemy          — QMainWindow shell, singletons, scene substrate
    PtolBus          — Face registry, thread lifecycle, suspend/resume
    PGui (external)  — PWindow chrome, QGraphicsProxyWidget management
    PtolKVM          — Fake KVM: UDP mouse/kb stream to remote host (stub)
    PtolHolePunch    — UDP NAT traversal rendezvous (stub, Tesla-integrated)

Render strategy:
    QGraphicsScene   — primary desktop, all PWindows live here
    VisPy canvas     — injected as QGraphicsProxyWidget for GL-accelerated
                       faces (Alexandria, Archimedes spectrograph, etc.)
                       Bypasses Qt item overhead: 10^6+ objects GPU-side
                       while QGraphicsScene handles window chrome/WM only

Threading contract:
    Each Face launched through PtolBus gets:
        face._ptol_thread  — QThread driving the face's work loop
        face._ptol_timers  — list of QTimers owned by the face
    PtolBus.suspend(id)  → thread.quit() + timer.stop() for each
    PtolBus.resume(id)   → thread.start() + timer.start() for each
    PtolBus.terminate(id)→ suspend + thread.wait() + del
    Faces that are not visible are NOT processing. No exceptions.

Network topology:
    Tesla.Sockets    — base UDP/TCP layer (existing)
    PtolHolePunch    — rendezvous server model, punches through NAT
                       Registers (public_ip, public_port) with relay,
                       peers exchange endpoints, then direct UDP
    PtolKVM          — sends (dx, dy, button, key) structs over punched
                       UDP channel. Server side applies via python-xlib
                       or uinput. No VNC overhead.
    Fallback         — TreasureHunt tab loads VNC web client if KVM down
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
#  PtolHolePunch — NAT traversal (stub, Tesla-integrated)
# ══════════════════════════════════════════════════════════════════════════════

class PtolHolePunch(QObject):
    """
    UDP hole punch via shared rendezvous relay.

    Protocol (3-way):
        1. Both peers send REGISTER packets to relay with (peer_id, secret)
        2. Relay replies with each peer's (public_ip, public_port)
        3. Peers simultaneously send to each other's public endpoint
           → NAT tables open in both directions → direct UDP channel

    Relay can be a minimal Python socket server (50 lines) on any VPS.
    No STUN/TURN infrastructure needed.

    Ports:
        23232  — Ptolemy primary (from existing Tesla code)
        32323  — House/relay
        5555   — Local LAN

    KVM channel uses this punched socket.
    VNC fallback runs over same channel or separate TCP tunnel.
    """

    punch_ready    = pyqtSignal(str, int)     # (peer_ip, peer_port)
    punch_failed   = pyqtSignal(str)

    # Known endpoints (from existing Tesla config — update as IPs change)
    RELAY_HOST  = '80.255.11.139'
    RELAY_PORT  = 23232
    HOUSE_HOST  = '72.211.113.6'
    HOUSE_PORT  = 32323
    LOCAL_PORT  = 5555

    def __init__(self, ptolemy, peer_id='ptolemy'):
        super().__init__(ptolemy)
        self.Ptolemy  = ptolemy
        self.peer_id  = peer_id
        self.sock     = None
        self._thread  = None
        self.peer_endpoint = None       # (ip, port) once punched

    def punch(self, peer_id_remote, relay_host=None, relay_port=None):
        """
        Begin hole punch to peer_id_remote via relay.
        Emits punch_ready(ip, port) on success.
        Non-blocking — runs in PtolHolePunchThread.
        STUB: wire to Tesla.GpsHolePunch when network config is live.
        """
        relay_host = relay_host or self.RELAY_HOST
        relay_port = relay_port or self.RELAY_PORT
        self._thread = PtolHolePunchThread(
            self, peer_id_remote, relay_host, relay_port)
        self._thread.punch_ready.connect(self._on_punch_ready)
        self._thread.punch_failed.connect(self.punch_failed)
        self._thread.start()

    def _on_punch_ready(self, ip, port):
        self.peer_endpoint = (ip, port)
        self.punch_ready.emit(ip, port)

    def close(self):
        if self._thread:
            self._thread.quit()
            self._thread.wait(1000)
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass


class PtolHolePunchThread(QThread):
    punch_ready  = pyqtSignal(str, int)
    punch_failed = pyqtSignal(str)

    def __init__(self, punch, peer_id_remote, relay_host, relay_port):
        super().__init__()
        self.punch           = punch
        self.peer_id_remote  = peer_id_remote
        self.relay_host      = relay_host
        self.relay_port      = relay_port

    def run(self):
        """
        STUB implementation — replace body with real punch logic.
        Real implementation:
            1. sock.sendto(REGISTER:<peer_id>:<secret>, relay)
            2. recv relay reply → parse (remote_ip, remote_port)
            3. simultaneous punch packets to remote_ip:remote_port
            4. recv first packet back → channel open
        """
        import socket, time
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.settimeout(10.0)
            self.punch.sock = sock

            # Step 1: Register with relay
            register_msg = f"REGISTER:{self.punch.peer_id}:{self.peer_id_remote}".encode()
            sock.sendto(register_msg, (self.relay_host, self.relay_port))

            # Step 2: Wait for relay to return remote peer endpoint
            data, _ = sock.recvfrom(256)
            parts = data.decode().split(':')
            if parts[0] == 'PEER' and len(parts) == 3:
                remote_ip   = parts[1]
                remote_port = int(parts[2])
                # Step 3: Simultaneous punch
                for _ in range(5):
                    sock.sendto(b'PUNCH', (remote_ip, remote_port))
                    time.sleep(0.1)
                # Step 4: Confirm
                sock.settimeout(5.0)
                sock.recvfrom(64)
                self.punch_ready.emit(remote_ip, remote_port)
            else:
                self.punch_failed.emit('Relay response malformed')

        except socket.timeout:
            self.punch_failed.emit('Hole punch timed out')
        except Exception as e:
            self.punch_failed.emit(str(e))


# ══════════════════════════════════════════════════════════════════════════════
#  PtolKVM — Fake KVM over punched UDP channel (stub)
# ══════════════════════════════════════════════════════════════════════════════

class PtolKVM(QObject):
    """
    Transmits local mouse movements and keypresses to a remote Ptolemy node
    over the punched UDP channel. No VNC overhead — raw input events only.

    Packet format (12 bytes, struct):
        type   : uint8  (0=mouse_move, 1=mouse_btn, 2=key, 3=ping)
        flags  : uint8  (button mask, key modifiers)
        x      : int16  (dx for move, absolute x for btn)
        y      : int16  (dy for move, absolute y for btn)
        key    : uint16 (Qt key code)
        seq    : uint32 (sequence number, for ordering)

    Server side (remote Ptolemy):
        Receives packets, applies via python-xlib or uinput.
        Drops out-of-order packets (seq comparison).
        Heartbeat ping every 5s to keep NAT hole open.

    VNC fallback:
        If KVM channel fails or remote is unreachable,
        Ptolemy opens a TreasureHunt tab to the VNC web client URL.
        Can be pre-configured: self.vnc_url = 'http://host:6080/vnc.html'
    """

    KVM_PACKET = struct.Struct('!BBhhHI')    # network byte order, 12 bytes
    HEARTBEAT_INTERVAL_MS = 5000

    connected    = pyqtSignal()
    disconnected = pyqtSignal()

    def __init__(self, ptolemy):
        super().__init__(ptolemy)
        self.Ptolemy      = ptolemy
        self.sock         = None
        self.remote       = None        # (ip, port)
        self.seq          = 0
        self.enabled      = False
        self.vnc_url      = None        # set to fallback VNC web URL

        self._heartbeat   = QTimer(self)
        self._heartbeat.setInterval(self.HEARTBEAT_INTERVAL_MS)
        self._heartbeat.timeout.connect(self._ping)

    def connect(self, remote_ip, remote_port, sock=None):
        """
        Activate KVM stream to remote_ip:remote_port.
        sock is the already-punched UDP socket from PtolHolePunch.
        """
        import socket as _socket
        self.remote  = (remote_ip, remote_port)
        self.sock    = sock or _socket.socket(_socket.AF_INET, _socket.SOCK_DGRAM)
        self.enabled = True
        self._heartbeat.start()
        self.connected.emit()

    def disconnect(self):
        self.enabled = False
        self._heartbeat.stop()
        self.remote = None
        self.disconnected.emit()

    def send_mouse_move(self, dx, dy):
        if not self.enabled: return
        self._send(0, 0, dx, dy, 0)

    def send_mouse_button(self, x, y, button, pressed):
        if not self.enabled: return
        flags = (button & 0x0F) | (0x80 if pressed else 0)
        self._send(1, flags, x, y, 0)

    def send_key(self, qt_key, modifiers, pressed):
        if not self.enabled: return
        flags = int(modifiers) & 0xFF
        self._send(2, flags | (0x80 if pressed else 0), 0, 0, qt_key & 0xFFFF)

    def _ping(self):
        self._send(3, 0, 0, 0, 0)

    def _send(self, ptype, flags, x, y, key):
        self.seq = (self.seq + 1) & 0xFFFFFFFF
        try:
            pkt = self.KVM_PACKET.pack(ptype, flags, x, y, key, self.seq)
            self.sock.sendto(pkt, self.remote)
        except Exception:
            pass

    def open_vnc_fallback(self):
        """Open VNC web client in a TreasureHunt browser tab."""
        if not self.vnc_url:
            return
        # Emit to whatever face is registered as the browser
        # PtolBus will route this to TreasureHunt if open
        th_record = next(
            (r for r in self.Ptolemy.bus._registry.values()
             if r['cls'] == 'TreasureHunt' and r['state'] == 'running'),
            None
        )
        if th_record and th_record['face']:
            face = th_record['face']
            if hasattr(face, 'add_new_tab'):
                face.add_new_tab(self.vnc_url, 'VNC Fallback')


# ══════════════════════════════════════════════════════════════════════════════
#  VisPy integration helper
# ══════════════════════════════════════════════════════════════════════════════

class PtolVispy:
    """
    Mixin/helper for faces that use VisPy for rendering.
    VisPy canvas renders via OpenGL — bypasses Qt item overhead entirely.
    QGraphicsScene handles the chrome (PWindow); VisPy handles the pixels.

    3 orders of magnitude object improvement:
        QGraphicsScene: ~10^3 items before frame rate degrades
        VisPy/GPU:      10^6+ primitives at 60fps (VBO-driven)
                        The vispy-test-2.py in working/ shows 16x20=320
                        signals × 1000 samples = 320,000 vertices realtime.

    Usage in a Face:
        class Alexandria(QWidget, PtolVispy):
            def __init__(self, parent):
                super().__init__(parent)
                self.canvas = self.make_vispy_canvas(size=(800,600))
                # canvas.native is the Qt widget — embed in layout
                layout = QVBoxLayout(self)
                layout.addWidget(self.canvas.native)

    Or for full-window GL face:
        pwin = self.bus.launch(AlexandriaGl, use_vispy=True)
        # PtolBus.launch with use_vispy=True proxies canvas.native directly
    """

    @staticmethod
    def make_vispy_canvas(size=(800, 600), title='', keys='interactive'):
        """
        Return a VisPy canvas configured for Qt5 backend embedding.
        Import is lazy — only faces that need GL pay the import cost.
        """
        try:
            import vispy
            vispy.use('PyQt5')
            from vispy import app, gloo
            canvas = app.Canvas(
                size=size,
                title=title,
                keys=keys,
                show=False
            )
            return canvas
        except ImportError:
            raise RuntimeError(
                "VisPy not installed. pip install vispy --break-system-packages")

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
        self.hole_punch = PtolHolePunch(self)
        self.kvm        = PtolKVM(self)

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

        # Pharos nav interface (always present)
        self.Interface = User(self)
        self.scene.addWidget(self.Interface)

        # Menu (always present)
        self.Menu = Menu(parent=self)
        self.scene.addWidget(self.Menu)

        # Philadelphos command input — lazy import, subprocess/inline toggle
        self._launch_philadelphos()

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

    def _on_punch_failed(self, reason):
        print(f'[PtolKVM] Hole punch failed: {reason}')
        self.kvm.open_vnc_fallback()

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
