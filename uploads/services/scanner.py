from django.conf import settings
import shutil
import subprocess
import os
import glob
import platform

def _scan_network(path):
    try:
        import pyclamd
        cd = pyclamd.ClamdNetworkSocket(host=settings.CLAMAV_HOST, port=settings.CLAMAV_PORT)
        cd.ping()
        result = cd.scan_file(path)
        if result is None:
            return ("CLEAN", "")
        return ("INFECTED", str(result))
    except Exception as e:
        return ("ERROR", f"network: {e}")

def _scan_cli(path):
    exe = shutil.which("clamscan")
    if not exe:
        return ("ERROR", "cli: clamscan not found")
    try:
        proc = subprocess.run([exe, "--no-summary", path], capture_output=True, text=True)
        if proc.returncode == 0:
            return ("CLEAN", "")
        if proc.returncode == 1:
            return ("INFECTED", proc.stdout or "cli: infected")
        return ("ERROR", proc.stderr or "cli: scan error")
    except Exception as e:
        return ("ERROR", f"cli: {e}")

def _find_defender_exe():
    exe = shutil.which("MpCmdRun.exe")
    if exe and os.path.isfile(exe):
        return exe
    candidates = []
    pf = os.environ.get("ProgramFiles")
    if pf:
        candidates.append(os.path.join(pf, "Windows Defender", "MpCmdRun.exe"))
        candidates.append(os.path.join(pf, "Microsoft Defender", "MpCmdRun.exe"))
    candidates.extend(glob.glob(r"C:\ProgramData\Microsoft\Windows Defender\Platform\*\MpCmdRun.exe"))
    for c in candidates:
        if os.path.isfile(c):
            return c
    return None

def _scan_defender(path):
    if platform.system() != "Windows":
        return ("ERROR", "defender: not windows")
    exe = _find_defender_exe()
    if not exe:
        return ("ERROR", "defender: MpCmdRun.exe not found")
    try:
        proc = subprocess.run([exe, "-Scan", "-ScanType", "3", "-File", path], capture_output=True, text=True)
        out = (proc.stdout or "") + (proc.stderr or "")
        if "No threats" in out or proc.returncode == 0:
            return ("CLEAN", "")
        if "Found" in out or "Threat" in out or proc.returncode == 2:
            return ("INFECTED", out.strip() or "defender: infected")
        return ("ERROR", out.strip() or f"defender: exit {proc.returncode}")
    except Exception as e:
        return ("ERROR", f"defender: {e}")

def scan_file(path):
    status, msg = _scan_network(path)
    if status == "ERROR":
        status, msg2 = _scan_cli(path)
        if status == "ERROR":
            status, msg3 = _scan_defender(path)
            if status == "ERROR":
                return ("ERROR", f"{msg}; {msg2}; {msg3}")
            return (status, msg3)
        return (status, msg2)
    return (status, msg)
