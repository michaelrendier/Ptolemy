#!/usr/bin/env python3
"""
PtolC/tools/ingest_system.py — full filesystem ingest for ptolemy (Python3)

Recursively visits every readable file from ROOT, extracts text,
feeds it to ptolemy -l - in batches.  State saved to JSON every
BATCH_DIRS directories — safe to kill and resume at any time.
Run as root — no sudo required anywhere in this script.

SETUP (run once):
    cd PtolC
    make
    bash tools/install_ingest_deps.sh
    ./tools/checkpoint_expand monad_wordnet.bin 255400
    ./ptolemy -s

RUN:
    python3 tools/ingest_system.py --root / --first /SystemTree.txt
    # overnight:
    nohup python3 tools/ingest_system.py --root / --first /SystemTree.txt \\
        2>&1 | tee ingest_py.log &

RESUME (after kill):
    python3 tools/ingest_system.py --root / --first /SystemTree.txt
    # Already-completed directories are skipped automatically.

ANDROID FACTORY IMAGES / PARTITION DUMPS:
    Walk-the-Hallway mount is implemented below (commented out).
    Provide --fstab from the image when available — it drives partition
    selection and gives correct type hints for erofs/f2fs/squashfs.
    Enable by uncommenting the walk_hallway block in main() and passing:
        python3 tools/ingest_system.py --images /path/to/image.bin ...
    ADB shell (rooted phone, no mount needed):
        adb shell find / -readable -type f 2>/dev/null \\
            | while read f; do adb shell cat "$f" 2>/dev/null; done \\
            | ./ptolemy -l -

GOOGLE DRIVE (GNOME GVFS):
    Detected automatically at /run/user/<uid>/gvfs/
    Mount it in Nautilus (Files) before running — it appears as
    google-drive:host=gmail.com,user=... subdirectory.

EXTERNAL DRIVES:
    All subdirectories of /media/ are detected automatically (any user's mount).
"""

import argparse
import json
import logging
import math
import os
import subprocess
import sys
import time

# ── Optional library imports ───────────────────────────────────────────────────
try:
    import magic as libmagic
    _HAVE_MAGIC = True
except ImportError:
    _HAVE_MAGIC = False

try:
    import chardet
    _HAVE_CHARDET = True
except ImportError:
    _HAVE_CHARDET = False

try:
    from pdfminer.high_level import extract_text as pdf_extract
    _HAVE_PDFMINER = True
except ImportError:
    _HAVE_PDFMINER = False

try:
    import docx as python_docx
    _HAVE_DOCX = True
except ImportError:
    _HAVE_DOCX = False

try:
    import ebooklib
    from ebooklib import epub as epub_lib
    import re as _re
    _HAVE_EPUB = True
except ImportError:
    _HAVE_EPUB = False

try:
    from odf import teletype
    from odf.opendocument import load as odf_load
    _HAVE_ODF = True
except ImportError:
    _HAVE_ODF = False

try:
    from striprtf.striprtf import rtf_to_text
    _HAVE_RTF = True
except ImportError:
    _HAVE_RTF = False

try:
    from bs4 import BeautifulSoup
    _HAVE_BS4 = True
except ImportError:
    _HAVE_BS4 = False

try:
    import pytesseract
    from PIL import Image
    _HAVE_OCR = True
except ImportError:
    _HAVE_OCR = False

# ── Constants ──────────────────────────────────────────────────────────────────
CHUNK_LINES   = 50_000
DEFAULT_BATCH = 10
STATE_FILE    = "ingest_state.json"
PTOLEMY       = "./ptolemy"

PRUNE_DIRS = frozenset([
    "/proc", "/sys", "/dev", "/run/lock",
    "/snap", "/var/run", "/tmp",
])

LOG = logging.getLogger("ingest")

# ── Mime detection ─────────────────────────────────────────────────────────────

def mime_type(path: str) -> str:
    if _HAVE_MAGIC:
        try:
            return libmagic.from_file(path, mime=True) or ""
        except Exception:
            pass
    result = subprocess.run(
        ["file", "-b", "--mime-type", path],
        capture_output=True, text=True, timeout=5
    )
    return result.stdout.strip() if result.returncode == 0 else ""

# ── Text extraction ────────────────────────────────────────────────────────────

def decode_bytes(raw: bytes) -> str:
    if _HAVE_CHARDET:
        det = chardet.detect(raw[:8192])
        enc = det.get("encoding") or "utf-8"
    else:
        enc = "utf-8"
    return raw.decode(enc, errors="replace")


def extract_text(path: str, mime: str) -> str:
    """Return extracted text from path (empty string on failure or binary)."""
    try:
        if mime.startswith("text/"):
            with open(path, "rb") as f:
                return decode_bytes(f.read())

        if mime == "application/pdf":
            if _HAVE_PDFMINER:
                try:
                    return pdf_extract(path) or ""
                except Exception:
                    pass
            result = subprocess.run(
                ["pdftotext", "-q", "-nopgbrk", "-enc", "UTF-8", path, "-"],
                capture_output=True, timeout=60
            )
            if result.returncode == 0:
                return result.stdout.decode("utf-8", errors="replace")
            if _HAVE_OCR:
                try:
                    import pdf2image
                    imgs = pdf2image.convert_from_path(path, dpi=150)
                    return "\n".join(pytesseract.image_to_string(img) for img in imgs)
                except Exception:
                    pass
            return ""

        if mime in ("application/gzip", "application/x-gzip"):
            result = subprocess.run(["zcat", path], capture_output=True, timeout=30)
            if result.returncode != 0:
                return ""
            inner = subprocess.run(
                ["file", "-b", "--mime-type", "-"],
                input=result.stdout[:512], capture_output=True, timeout=5
            ).stdout.strip().decode()
            if inner.startswith("text/"):
                col = subprocess.run(
                    ["col", "-b"], input=result.stdout, capture_output=True, timeout=30
                )
                return col.stdout.decode("utf-8", errors="replace")
            return ""

        if mime == "application/x-bzip2":
            result = subprocess.run(["bzcat", path], capture_output=True, timeout=30)
            return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""

        if mime == "application/x-xz":
            result = subprocess.run(["xzcat", path], capture_output=True, timeout=30)
            return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""

        if mime in ("text/html", "application/xhtml+xml"):
            with open(path, "rb") as f:
                raw = f.read()
            if _HAVE_BS4:
                soup = BeautifulSoup(raw, "lxml")
                return soup.get_text(separator="\n")
            result = subprocess.run(["html2text", path], capture_output=True, timeout=30)
            return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""

        if mime == "application/msword":
            result = subprocess.run(["catdoc", path], capture_output=True, timeout=30)
            return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""

        if mime in ("application/rtf", "text/rtf"):
            if _HAVE_RTF:
                with open(path, "rb") as f:
                    return rtf_to_text(f.read().decode("utf-8", errors="replace"))
            result = subprocess.run(["unrtf", "--text", path], capture_output=True, timeout=30)
            return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""

        if mime == "application/epub+zip":
            if _HAVE_EPUB:
                try:
                    book = epub_lib.read_epub(path, options={"ignore_ncx": True})
                    parts = []
                    for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT):
                        if _HAVE_BS4:
                            soup = BeautifulSoup(item.get_content(), "lxml")
                            parts.append(soup.get_text(separator="\n"))
                        else:
                            parts.append(_re.sub(r"<[^>]+>", "",
                                item.get_content().decode("utf-8", errors="replace")))
                    return "\n".join(parts)
                except Exception:
                    pass
            import zipfile, re
            try:
                with zipfile.ZipFile(path) as z:
                    parts = []
                    for n in z.namelist():
                        if n.endswith((".xhtml", ".html", ".htm")):
                            raw = z.read(n).decode("utf-8", errors="replace")
                            parts.append(re.sub(r"<[^>]+>", "", raw))
                    return "\n".join(parts)
            except Exception:
                return ""

        if mime == "application/vnd.oasis.opendocument.text":
            if _HAVE_ODF:
                try:
                    doc = odf_load(path)
                    return teletype.extractText(doc.text)
                except Exception:
                    pass
            result = subprocess.run(["odt2txt", "--stdout", path], capture_output=True, timeout=30)
            return result.stdout.decode("utf-8", errors="replace") if result.returncode == 0 else ""

        if mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            if _HAVE_DOCX:
                try:
                    doc = python_docx.Document(path)
                    return "\n".join(p.text for p in doc.paragraphs)
                except Exception:
                    pass
            return ""

        if mime in ("application/vnd.ms-excel",
                    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"):
            try:
                import openpyxl
                wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
                rows = []
                for ws in wb.worksheets:
                    for row in ws.iter_rows(values_only=True):
                        rows.append("\t".join(str(c) for c in row if c is not None))
                return "\n".join(rows)
            except Exception:
                return ""

        if mime.startswith("image/") and _HAVE_OCR:
            try:
                img = Image.open(path)
                return pytesseract.image_to_string(img)
            except Exception:
                pass

        # gettext .po/.pot — all Unicode locale strings (every language on the system)
        if path.endswith((".po", ".pot")):
            try:
                with open(path, "rb") as f:
                    raw = f.read()
                text = decode_bytes(raw)
                lines = [ln[7:].strip().strip('"') for ln in text.splitlines()
                         if ln.startswith("msgstr") or ln.startswith("msgid")]
                return "\n".join(ln for ln in lines if ln)
            except Exception:
                return ""

    except (PermissionError, FileNotFoundError, IsADirectoryError, OSError):
        pass
    except subprocess.TimeoutExpired:
        LOG.warning("timeout: %s", path)
    except Exception as e:
        LOG.debug("extract error %s: %s", path, e)

    return ""

# ── Ptolemy pipe ───────────────────────────────────────────────────────────────

def learn_text(text: str, ptolemy: str) -> bool:
    """Feed text to ptolemy -l -, return True on success."""
    if not text.strip():
        return True
    try:
        result = subprocess.run(
            [ptolemy, "-l", "-"],
            input=text.encode("utf-8", errors="replace"),
            capture_output=True, timeout=300
        )
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        LOG.warning("ptolemy timeout during learn")
        return False
    except Exception as e:
        LOG.error("ptolemy error: %s", e)
        return False


def learn_chunked(text: str, ptolemy: str, chunk_lines: int = CHUNK_LINES) -> int:
    """Learn text in chunk_lines-line slices. Returns number of chunks sent."""
    lines = text.splitlines(keepends=True)
    if not lines:
        return 0
    n_chunks = math.ceil(len(lines) / chunk_lines)
    for i in range(n_chunks):
        chunk = "".join(lines[i * chunk_lines:(i + 1) * chunk_lines])
        if not learn_text(chunk, ptolemy):
            LOG.warning("learn failed on chunk %d/%d", i + 1, n_chunks)
    return n_chunks

# ── State management ───────────────────────────────────────────────────────────

def load_state(state_path: str) -> dict:
    if os.path.exists(state_path):
        try:
            with open(state_path) as f:
                return json.load(f)
        except Exception:
            pass
    return {"done_dirs": [], "files_total": 0, "dirs_total": 0,
            "errors": 0, "started": time.time()}


def save_state(state: dict, state_path: str):
    tmp = state_path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(state, f, indent=2)
    os.replace(tmp, state_path)

# ── Directory discovery ────────────────────────────────────────────────────────

def auto_extra_roots() -> list[str]:
    """
    Detect GVFS mounts and external drives without assuming a username.

    GVFS: /run/user/<uid>/gvfs/  — GNOME network mounts (Google Drive, SMB, …)
          Each subdirectory is a separate mount (google-drive:host=…, smb-share:…).
          Mount the drive in Nautilus first, then run ingest.

    External drives: /media/ — all user subdirs, all mounted volumes within them.
    Running as root means $USER is "root", so we scan /media/ for any username.
    """
    extras = []

    uid  = os.getuid()
    gvfs = f"/run/user/{uid}/gvfs"
    if os.path.isdir(gvfs):
        for entry in os.scandir(gvfs):
            if entry.is_dir():
                LOG.info("GVFS mount: %s", entry.path)
                extras.append(entry.path)

    if os.path.isdir("/media"):
        for user_entry in os.scandir("/media"):
            if not user_entry.is_dir():
                continue
            for vol_entry in os.scandir(user_entry.path):
                if vol_entry.is_dir():
                    LOG.info("External drive: %s", vol_entry.path)
                    extras.append(vol_entry.path)

    return extras


def should_prune(path: str) -> bool:
    return any(path == p or path.startswith(p + "/") for p in PRUNE_DIRS)

# ── Priority file ──────────────────────────────────────────────────────────────

def ingest_priority_file(path: str, ptolemy: str, chunk_lines: int):
    if not os.path.isfile(path):
        LOG.info("priority file not ready yet: %s  (will ingest when found)", path)
        return
    size = os.path.getsize(path)
    LOG.info("priority file: %s  (%.1f MB)", path, size / 1e6)
    try:
        with open(path, "rb") as f:
            raw = f.read()
        chunks = learn_chunked(decode_bytes(raw), ptolemy, chunk_lines)
        LOG.info("priority file done: %d chunks", chunks)
    except Exception as e:
        LOG.error("priority file error: %s", e)

# ── Main ingest loop ───────────────────────────────────────────────────────────

def ingest_tree(root: str, ptolemy: str, state: dict, state_path: str,
                batch_dirs: int, chunk_lines: int):
    done_set       = set(state["done_dirs"])
    dirs_since_save = 0
    accumulated    = []
    acc_lines      = 0

    def flush():
        nonlocal accumulated, acc_lines
        if accumulated:
            learn_chunked("\n".join(accumulated), ptolemy, chunk_lines)
            accumulated = []
            acc_lines   = 0

    for dirpath, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = [
            d for d in sorted(dirnames)
            if not should_prune(os.path.join(dirpath, d))
            and not os.path.islink(os.path.join(dirpath, d))
        ]

        if should_prune(dirpath) or dirpath in done_set:
            continue

        LOG.info("[%s] %s  (%d files)", time.strftime("%H:%M:%S"), dirpath, len(filenames))

        for fname in sorted(filenames):
            fpath = os.path.join(dirpath, fname)
            if os.path.islink(fpath):
                continue
            try:
                st = os.stat(fpath)
                if st.st_size == 0 or st.st_size > 512 * 1024 * 1024:
                    continue
            except OSError:
                continue

            try:
                mime = mime_type(fpath)
            except Exception:
                mime = ""

            text = extract_text(fpath, mime)
            if text.strip():
                lines = text.splitlines()
                accumulated.extend(lines)
                acc_lines += len(lines)
                state["files_total"] += 1
                if acc_lines >= chunk_lines:
                    flush()

        state["done_dirs"].append(dirpath)
        done_set.add(dirpath)
        state["dirs_total"] += 1
        dirs_since_save += 1

        if dirs_since_save >= batch_dirs:
            flush()
            save_state(state, state_path)
            elapsed = time.time() - state["started"]
            LOG.info("checkpoint: %d dirs  %d files  %.0fs",
                     state["dirs_total"], state["files_total"], elapsed)
            dirs_since_save = 0

    flush()
    save_state(state, state_path)


# ════════════════════════════════════════════════════════════════════════════════
# WALK-THE-HALLWAY — binary image mount / ingest
# Commented out pending fstab from each Android image.
# When you have the fstab, pass it via --fstab so partition types are confirmed.
#
# HOW IT WORKS:
#   Phase 1 — The Hallway (probe):
#     losetup --partscan --find --show image.bin  → /dev/loopN
#     lsblk + blkid reads the sysfs partition table (/sys/block/loopN/loopNpM/)
#     Collects every filesystem type present.
#     losetup -d (exit hallway, zero mount time).
#
#   Phase 2 — Open the Doors (mount):
#     losetup --partscan again.
#     For each partition:
#       - Skip EFI/efivars (raw UEFI NVRAM — secure boot keys, boot order, firmware)
#       - mount --mkdir -o ro -t type1,type2 /dev/loopNpM /mnt/hallway/img/pM
#         ^ --mkdir: mount creates the mountpoint dir if it doesn't exist
#         ^ -t comma list: mount(8) tries each type in order, no spaces
#           man 8 mount: "Multiple types can be specified in a comma-separated list"
#           Useful for Android where system may be ext4 (old) or erofs/squashfs (new)
#       - ingest_tree() over the mountpoint
#     umount -l all, losetup -d.
#
# TO ENABLE:
#   1. Uncomment walk_hallway_images() and _SKIP_FSTYPES/_SKIP_LABELS/_losetup_* below
#   2. Uncomment the --images / --mount-base args in main()
#   3. Uncomment the walk_hallway_images() call in main()
#   4. Provide --fstab /path/to/fstab for each image (drives type selection)
# ════════════════════════════════════════════════════════════════════════════════

# # Partition types to never mount
# _SKIP_FSTYPES = frozenset([
#     "vfat",        # EFI System Partition — efivars, UEFI NVRAM, secure boot keys
#     "swap",        # raw swap — no text
#     "BitLocker",   # encrypted
#     "crypto_LUKS", # encrypted
# ])
#
# # EFI System Partition GUID (GPT)
# _EFI_GUID = "C12A7328-F81F-11D2-BA4B-00A0C93EC93B"
#
# # Partition labels that are always EFI/firmware — skip regardless of detected type
# _SKIP_LABELS = frozenset(["EFI", "EFI System", "ESP", "efivars",
#                            "BIOS Boot", "BIOS_GRUB"])
#
#
# def _losetup_attach(image_path: str) -> str:
#     """Attach image to next free loop device with partition scanning. Returns /dev/loopN."""
#     r = subprocess.run(
#         ["losetup", "--partscan", "--find", "--show", image_path],
#         capture_output=True, text=True, timeout=30
#     )
#     if r.returncode != 0:
#         raise RuntimeError(f"losetup failed: {r.stderr.strip()}")
#     return r.stdout.strip()
#
#
# def _losetup_detach(loop_dev: str):
#     subprocess.run(["losetup", "-d", loop_dev], capture_output=True, timeout=10)
#
#
# def _probe_partitions(loop_dev: str) -> list[dict]:
#     """
#     Query lsblk for all child partitions of loop_dev.
#     Returns list of {dev, fstype, label, size, parttype}.
#     lsblk reads /sys/block/loopN/ (sysfs) — this IS the sysfs walk.
#     """
#     r = subprocess.run(
#         ["lsblk", "--json", "--output", "NAME,FSTYPE,LABEL,SIZE,PARTTYPE", loop_dev],
#         capture_output=True, text=True, timeout=15
#     )
#     if r.returncode != 0:
#         return []
#     try:
#         tree = json.loads(r.stdout)
#         result = []
#         for dev in tree.get("blockdevices", []):
#             for child in dev.get("children", []):
#                 result.append({
#                     "dev":      f"/dev/{child.get('name', '')}",
#                     "fstype":   child.get("fstype") or "",
#                     "label":    child.get("label")  or "",
#                     "size":     child.get("size")   or "",
#                     "parttype": child.get("parttype") or "",
#                 })
#         return result
#     except Exception:
#         return []
#
#
# def _is_efi_partition(p: dict) -> bool:
#     """
#     True for EFI System Partition or efivars — always skip.
#     efivars contains raw UEFI NVRAM: secure boot keys, boot order, firmware
#     settings.  There is too much sensitive information in this partition
#     to ingest safely.
#     """
#     fstype   = (p.get("fstype")   or "").lower()
#     label    = (p.get("label")    or "").upper()
#     parttype = (p.get("parttype") or "").upper()
#     if fstype in {f.lower() for f in _SKIP_FSTYPES}:
#         return True
#     if any(skip.upper() in label for skip in _SKIP_LABELS):
#         return True
#     if _EFI_GUID.upper() in parttype:
#         return True
#     return False
#
#
# def walk_hallway_images(image_paths: list[str], mount_base: str,
#                         ptolemy: str, state: dict, state_path: str,
#                         batch_dirs: int, chunk_lines: int):
#     """
#     Walk-the-Hallway mount for binary disk images (.bin, .img, partition dumps).
#
#     mount --mkdir: util-linux 2.36+ — creates the mountpoint directory
#     automatically if it does not exist. No manual mkdir needed.
#
#     -t comma syntax: mount(8) "Multiple types can be specified in a
#     comma-separated list" (no spaces). Mount tries each in order, stops at
#     first success. Example: -t ext4,f2fs,erofs,squashfs
#     This is the walk-the-hallway output: one combined -t string built from
#     everything blkid detected in the probe pass.
#
#     EFI/efivars: always skipped. Contains raw UEFI NVRAM — secure boot keys,
#     boot order, firmware variables. Flag it, log it, never mount it.
#
#     Android notes (pending fstab per image):
#       system.img  — ext4 (older) or erofs/squashfs (Android 10+)
#       vendor.img  — same
#       userdata    — ext4 or f2fs; may be encrypted (skip if crypto_LUKS)
#       boot.img    — Android sparse format, not a standard partition image
#       Provide fstab to confirm types before enabling.
#     """
#     for image_path in image_paths:
#         if not os.path.isfile(image_path):
#             LOG.warning("image not found: %s", image_path)
#             continue
#
#         LOG.info("walk-the-hallway: %s", image_path)
#         loop_dev = None
#         mounted  = []
#
#         try:
#             # ── Phase 1: the hallway (probe via sysfs) ────────────────────────
#             loop_dev = _losetup_attach(image_path)
#             LOG.info("  loop: %s  (partition scan active)", loop_dev)
#             time.sleep(1)   # let kernel expose partitions in sysfs
#
#             partitions = _probe_partitions(loop_dev)
#             if not partitions:
#                 LOG.warning("  no partitions in %s", image_path)
#                 _losetup_detach(loop_dev); loop_dev = None
#                 continue
#
#             # Build the combined -t string from all non-EFI detected types
#             all_types    = [p["fstype"] for p in partitions
#                             if p["fstype"] and not _is_efi_partition(p)]
#             unique_types = list(dict.fromkeys(all_types))   # dedup, preserve order
#             combined_t   = ",".join(unique_types) if unique_types else "auto"
#             LOG.info("  partitions: %d  combined -t: %s", len(partitions), combined_t)
#
#             for p in partitions:
#                 status = "SKIP efivars" if _is_efi_partition(p) else "ok"
#                 LOG.info("  [%s] %s  fstype=%s  size=%s  label=%s",
#                          status, p["dev"], p["fstype"], p["size"], p["label"])
#
#             _losetup_detach(loop_dev); loop_dev = None
#             LOG.info("  probe done — exiting hallway")
#
#             # ── Phase 2: open the doors (mount each partition) ─────────────────
#             loop_dev = _losetup_attach(image_path)
#             time.sleep(1)
#             img_stem = os.path.splitext(os.path.basename(image_path))[0]
#
#             for i, p in enumerate(partitions):
#                 if _is_efi_partition(p):
#                     LOG.info("  skip efivars: %s (%s)", p["dev"], p["fstype"])
#                     continue
#
#                 # mount --mkdir creates /mnt/hallway/<img>/<pN> automatically
#                 mountpoint = os.path.join(mount_base, img_stem, f"p{i+1}")
#                 fstype_arg = p["fstype"] if p["fstype"] else combined_t
#
#                 LOG.info("  mount %s → %s  -t %s", p["dev"], mountpoint, fstype_arg)
#                 r = subprocess.run(
#                     ["mount", "--mkdir", "-o", "ro", "-t", fstype_arg,
#                      p["dev"], mountpoint],
#                     capture_output=True, text=True, timeout=30
#                 )
#                 if r.returncode != 0:
#                     LOG.warning("  mount failed: %s  (%s)", p["dev"], r.stderr.strip())
#                     continue
#
#                 mounted.append(mountpoint)
#                 ingest_tree(mountpoint, ptolemy, state, state_path,
#                             batch_dirs, chunk_lines)
#
#         except Exception as e:
#             LOG.error("walk-the-hallway error %s: %s", image_path, e)
#
#         finally:
#             for mp in reversed(mounted):
#                 subprocess.run(["umount", "-l", mp], capture_output=True, timeout=30)
#                 LOG.info("  umounted %s", mp)
#             if loop_dev:
#                 _losetup_detach(loop_dev)
#                 LOG.info("  detached %s", loop_dev)

# ════════════════════════════════════════════════════════════════════════════════

# ── Entry point ────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="ptolemy full-system ingest (Python3, resumable, run as root)"
    )
    ap.add_argument("--root",        default="/",         help="root directory to traverse")
    ap.add_argument("--first",       default="",          help="priority file (e.g. /SystemTree.txt)")
    ap.add_argument("--ptolemy",     default=PTOLEMY,     help="path to ptolemy binary")
    ap.add_argument("--state",       default=STATE_FILE,  help="JSON state file")
    ap.add_argument("--batch-dirs",  type=int, default=DEFAULT_BATCH, help="checkpoint every N dirs")
    ap.add_argument("--chunk-lines", type=int, default=CHUNK_LINES,   help="max lines per learn call")
    ap.add_argument("--extra",       action="append", default=[],     help="extra root dir (repeatable)")
    ap.add_argument("--no-auto-extra", action="store_true",           help="skip GVFS/media detection")
    # Uncomment when walk-the-hallway is enabled:
    # ap.add_argument("--images",    action="append", default=[],  help="binary image to mount+ingest")
    # ap.add_argument("--mount-base",default="/mnt/hallway",       help="base dir for hallway mounts")
    # ap.add_argument("--fstab",     default="",                   help="fstab from image (type hints)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s  %(levelname)-5s  %(message)s",
        datefmt="%H:%M:%S",
    )

    if not os.path.isfile(args.ptolemy) or not os.access(args.ptolemy, os.X_OK):
        LOG.error("ptolemy not found: %s  (build with: cd PtolC && make)", args.ptolemy)
        sys.exit(1)

    r = subprocess.run([args.ptolemy, "-s"], capture_output=True, timeout=10)
    if r.returncode == 0:
        LOG.info("ptolemy status:\n%s", r.stdout.decode("utf-8", errors="replace").strip())
    else:
        LOG.warning("ptolemy -s non-zero — continuing anyway")

    state = load_state(args.state)
    if state["dirs_total"] > 0:
        LOG.info("RESUMING: %d dirs  %d files already done",
                 state["dirs_total"], state["files_total"])

    # ── Priority file first ───────────────────────────────────────────────────
    if args.first and args.first not in state.get("done_dirs", []):
        LOG.info("=== Priority file ===")
        ingest_priority_file(args.first, args.ptolemy, args.chunk_lines)
        state["done_dirs"].append(args.first)
        save_state(state, args.state)

    # ── Auto-detect GVFS / external drives ───────────────────────────────────
    extra_list = list(args.extra)
    if not args.no_auto_extra:
        extra_list += auto_extra_roots()

    # ── Walk-the-Hallway for binary images (commented out — see block above) ─
    # if args.images:
    #     walk_hallway_images(args.images, args.mount_base,
    #                         args.ptolemy, state, args.state,
    #                         args.batch_dirs, args.chunk_lines)

    # ── Main filesystem traversal ─────────────────────────────────────────────
    for root in [args.root] + extra_list:
        if not os.path.isdir(root):
            LOG.warning("root not accessible: %s", root)
            continue
        LOG.info("=== Traversing: %s ===", root)
        ingest_tree(root, args.ptolemy, state, args.state,
                    args.batch_dirs, args.chunk_lines)

    # ── Final report ──────────────────────────────────────────────────────────
    elapsed = time.time() - state["started"]
    LOG.info("════════════════════════════════════════")
    LOG.info("INGEST COMPLETE")
    LOG.info("  dirs  visited : %d", state["dirs_total"])
    LOG.info("  files learned : %d", state["files_total"])
    LOG.info("  elapsed       : %.0f s  (%.1f h)", elapsed, elapsed / 3600)
    LOG.info("════════════════════════════════════════")

    r = subprocess.run([args.ptolemy, "-s"], capture_output=True, timeout=10)
    if r.returncode == 0:
        print(r.stdout.decode("utf-8", errors="replace"))


if __name__ == "__main__":
    main()
