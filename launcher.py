"""
ScrapeGraphAI All-in-One Launcher.

Checks system requirements, auto-installs missing deps,
creates persistent Chrome profile, and starts the stack.

Usage:
    python launcher.py
    python launcher.py --poe
    python launcher.py --backend-only
    python launcher.py --skip-checks
"""

import argparse
import json
import os
import shutil
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
WEBAPP_DIR = HERE / "webapp"
BACKEND_DIR = WEBAPP_DIR / "backend"
FRONTEND_DIR = WEBAPP_DIR / "frontend"


NOT_FOUND_MSG = "No free port found in range {}-{}"


def find_free_port(start: int = 8000, max_attempts: int = 50) -> int:
    for port in range(start, start + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    raise RuntimeError(NOT_FOUND_MSG.format(start, start + max_attempts))


def _find_cmd(name: str) -> str:
    found = shutil.which(name)
    if found:
        return found
    raise FileNotFoundError(f"'{name}' not found on PATH")


def poe_available() -> bool:
    try:
        subprocess.run(
            [_find_cmd("poe"), "--version"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
        return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def ensure_poe() -> None:
    if not poe_available():
        print("poethepoet not found. Installing...", flush=True)
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "poethepoet"],
            check=True,
        )


def start_backend_native(port: int, frontend_port: int) -> subprocess.Popen:
    env = os.environ.copy()
    env["SCRAPEGRAPHAI_TELEMETRY_ENABLED"] = "false"
    env["FRONTEND_PORT"] = str(frontend_port)
    print(f"[backend] Starting on port {port}...", flush=True)
    return subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "app.main:app",
         "--host", "127.0.0.1", "--port", str(port), "--reload"],
        cwd=str(BACKEND_DIR),
        env=env,
    )


def start_backend_poe(port: int, frontend_port: int) -> subprocess.Popen:
    poe = _find_cmd("poe")
    env = os.environ.copy()
    env["SCRAPEGRAPHAI_TELEMETRY_ENABLED"] = "false"
    env["FRONTEND_PORT"] = str(frontend_port)
    print(f"[backend] Starting on port {port} via poe...", flush=True)
    return subprocess.Popen(
        [poe, "web-backend"],
        cwd=str(BACKEND_DIR),
        env=env,
    )


def _find_npx() -> str:
    npx = shutil.which("npx")
    if npx:
        return npx
    raise FileNotFoundError("npx not found. Install Node.js (npm ships with npx)")


def start_frontend_native(port: int, backend_port: int) -> subprocess.Popen:
    npx = _find_npx()
    env = os.environ.copy()
    env["VITE_BACKEND_URL"] = f"http://127.0.0.1:{backend_port}"
    print(f"[frontend] Starting on port {port}, backend -> {backend_port}...", flush=True)
    return subprocess.Popen(
        [npx, "vite", "--port", str(port), "--host", "127.0.0.1"],
        cwd=str(FRONTEND_DIR),
        env=env,
    )


def start_frontend_poe(port: int, backend_port: int) -> subprocess.Popen:
    poe = _find_cmd("poe")
    env = os.environ.copy()
    env["VITE_BACKEND_URL"] = f"http://127.0.0.1:{backend_port}"
    print(f"[frontend] Starting on port {port}, backend -> {backend_port} via poe...", flush=True)
    return subprocess.Popen(
        [poe, "web-frontend"],
        cwd=str(FRONTEND_DIR),
        env=env,
    )


HEALTH_OK = 200


def wait_for_backend(port: int, timeout: int = 30) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = urllib.request.urlopen(
                f"http://127.0.0.1:{port}/api/health",
                timeout=2,
            )
            if resp.status == HEALTH_OK:
                return True
        except Exception:
            pass
        time.sleep(1)
    return False


HEALTHY_HEADER = "─" * 56


def print_healthy(backend_port: int, frontend_port: int) -> None:
    print(HEALTHY_HEADER, flush=True)
    print(f"  Backend  -> http://127.0.0.1:{backend_port}/docs", flush=True)
    print(f"  Frontend -> http://127.0.0.1:{frontend_port}", flush=True)
    print("  Press Ctrl+C to stop all services", flush=True)
    print(HEALTHY_HEADER, flush=True)


def cleanup_procs(procs: list[subprocess.Popen]) -> None:
    for p in procs:
        if p.poll() is None:
            p.terminate()
            try:
                p.wait(timeout=5)
            except subprocess.TimeoutExpired:
                p.kill()


def start_backend(args: argparse.Namespace, backend_port: int, frontend_port: int) -> subprocess.Popen | None:
    if args.frontend_only:
        return None
    if args.poe:
        return start_backend_poe(backend_port, frontend_port)
    return start_backend_native(backend_port, frontend_port)


def start_frontend(args: argparse.Namespace, frontend_port: int, backend_port: int) -> subprocess.Popen | None:
    if args.backend_only:
        return None
    if args.poe:
        return start_frontend_poe(frontend_port, backend_port)
    return start_frontend_native(frontend_port, backend_port)


def wait_for_health_or_warn(backend_port: int) -> None:
    print("[launcher] Waiting for backend to be ready...", flush=True)
    if wait_for_backend(backend_port):
        print(f"[launcher] Backend ready at http://127.0.0.1:{backend_port}", flush=True)
    else:
        print("[launcher] Backend did not become ready in time", flush=True)


# ── System checks ──────────────────────────────────────────────────────
SCRAPEGRAPH_DIR = Path.home() / ".scrapegraph"
CHROME_PROFILE_DIR = SCRAPEGRAPH_DIR / "chrome-profile"
STORAGE_STATE_DIR = SCRAPEGRAPH_DIR / "chrome-data"
STORAGE_STATE_FILE = STORAGE_STATE_DIR / "storage_state.json"


def check_chrome() -> bool:
    """Check if Chrome/Chromium is available on the system."""
    candidates = [
        "chrome", "chromium", "google-chrome", "google-chrome-stable",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    ]
    for cmd in candidates:
        try:
            shutil.which(cmd)
            return True
        except Exception:
            pass
        if os.path.isfile(cmd):
            return True
    return False


def check_playwright_browsers() -> bool:
    """Check if Playwright has Chromium installed."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "playwright", "install", "--dry-run"],
            capture_output=True, text=True, timeout=15,
        )
        return "chromium" not in result.stdout and "already" in result.stdout
    except Exception:
        return False


def ensure_scrapegraph_dirs():
    """Create ~/.scrapegraph/ directory structure."""
    CHROME_PROFILE_DIR.mkdir(parents=True, exist_ok=True)
    STORAGE_STATE_DIR.mkdir(parents=True, exist_ok=True)
    print(f"[setup] Chrome profile: {CHROME_PROFILE_DIR}")
    print(f"[setup] Cookie cache:   {STORAGE_STATE_FILE}")


def ensure_playwright_browsers():
    """Install Playwright browsers if missing."""
    if check_playwright_browsers():
        print("[setup] Playwright browsers already installed.")
        return
    print("[setup] Installing Playwright browsers (chromium)...")
    subprocess.run(
        [sys.executable, "-m", "playwright", "install", "chromium"],
        check=True, timeout=120,
    )


def ensure_deps():
    """Check and install missing Python dependencies."""
    required = [
        "undetected-playwright",
    ]
    for pkg in required:
        try:
            __import__(pkg.replace("-", "_"))
            print(f"[setup] {pkg} OK")
        except ImportError:
            print(f"[setup] Installing {pkg}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", pkg],
                check=True, timeout=60,
            )


def system_check(args) -> bool:
    """Run all system checks, return False if critical issues found."""
    print("─" * 56)
    print("  ScrapeGraphAI System Check")
    print("─" * 56)

    chrome_ok = check_chrome()
    if chrome_ok:
        print("[✓] Chrome/Chromium found")
    else:
        print("[✗] Chrome/Chromium not found")
        print("    Install Chrome from https://www.google.com/chrome/")
        print("    Some features may not work without Chrome.")

    ensure_scrapegraph_dirs()
    ensure_deps()
    ensure_playwright_browsers()

    print("─" * 56)
    return True


def main() -> None:
    parser = argparse.ArgumentParser(description="ScrapeGraphAI All-in-One Launcher")
    parser.add_argument("--poe", action="store_true", help="Use poethepoet task runner")
    parser.add_argument("--backend-only", action="store_true")
    parser.add_argument("--frontend-only", action="store_true")
    parser.add_argument("--backend-port", type=int, default=None)
    parser.add_argument("--frontend-port", type=int, default=5173)
    parser.add_argument("--skip-checks", action="store_true")
    args = parser.parse_args()

    if not args.skip_checks:
        system_check(args)

    if args.poe:
        ensure_poe()

    backend_port = args.backend_port or find_free_port(8000)
    frontend_port = args.frontend_port

    procs: list[subprocess.Popen] = []

    try:
        p = start_backend(args, backend_port, frontend_port)
        if p is not None:
            procs.append(p)
            wait_for_health_or_warn(backend_port)

        p = start_frontend(args, frontend_port, backend_port)
        if p is not None:
            procs.append(p)

        print_healthy(backend_port, frontend_port)

        if not procs:
            print("[launcher] No services started. Use --backend-only, --frontend-only, or neither.", flush=True)
            return

        while all(p.poll() is None for p in procs):
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n[launcher] Shutting down...", flush=True)
    finally:
        cleanup_procs(procs)
        print("[launcher] All services stopped.", flush=True)


if __name__ == "__main__":
    main()
