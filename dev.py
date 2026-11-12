import sys
import time
import subprocess
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROOT = Path(__file__).resolve().parent

IGNORE_DIRS = {
    ".venv",
    "__pycache__",
    ".git",
    "output",
}

class ReloadHandler(FileSystemEventHandler):
    def __init__(self, process):
        self.process = process

    def on_modified(self, event):
        if event.is_directory:
            return

        path = Path(event.src_path)

        if path.suffix != ".py":
            return

        if any(part in IGNORE_DIRS for part in path.parts):
            return

        print(f"\nPerubahan terdeteksi: {path.name}")
        self.process()

def run_app():
    return subprocess.Popen([
        sys.executable,
        "-m",
        "app.main"
    ])

process = run_app()

def restart_app():
    global process

    if process.poll() is None:
        process.terminate()
        process.wait()

    time.sleep(0.5)
    process = run_app()

handler = ReloadHandler(restart_app)
observer = Observer()
observer.schedule(handler, str(ROOT / "app"), recursive=True)
observer.start()

print("Worksheet Generator Auto Reload aktif.")
print("Simpan file Python untuk memuat ulang aplikasi.")
print("Tekan CTRL+C untuk berhenti.")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    observer.stop()
    if process.poll() is None:
        process.terminate()

observer.join()