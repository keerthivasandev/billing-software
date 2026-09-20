# Packaging (Windows .exe)

## Build

```powershell
conda activate billing-software
pip install -r requirements.txt
pip install pyinstaller
pyinstaller sri_lakshmi_erp.spec
```

Output: `dist/SriLakshmiERP.exe` (one-file, windowed, no console).

## Notes

- Uses **PySide6** only — no Electron/WebView.
- No hard-coded developer paths; entry is `main.py`.
- Sample data is in-package; no external DB required for the UI demo.
- On first run after packaging, Windows Defender may scan the new exe (normal for PyInstaller).
