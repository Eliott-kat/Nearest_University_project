import threading
import webview
import time
import requests
from main import app

def start_flask():
    app.run()

def wait_for_flask(url, timeout=15):
    """Attend que le serveur Flask soit prêt avant d'ouvrir la fenêtre."""
    start = time.time()
    while True:
        try:
            requests.get(url)
            return
        except Exception:
            if time.time() - start > timeout:
                raise RuntimeError("Flask n'a pas démarré après 15 secondes.")
            time.sleep(0.5)

if __name__ == '__main__':
    flask_thread = threading.Thread(target=start_flask, daemon=True)
    flask_thread.start()
    wait_for_flask("http://127.0.0.1:5000")
    webview.create_window("NEU-AcadCheck", "http://127.0.0.1:5000")
    webview.start(gui='edgechromium')