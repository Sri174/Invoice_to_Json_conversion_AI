"""
Invoice Processor API
Run script for development and production.
"""
import os
import sys
import subprocess

def install_requirements():
    """Install Python dependencies."""
    print("Installing dependencies...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

def check_tesseract():
    """Check if Tesseract OCR is installed."""
    try:
        result = subprocess.run(
            ['tesseract', '--version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            print(f"Tesseract found: {result.stdout.split()[1]}")
            return True
    except FileNotFoundError:
        pass

    # Windows common paths
    if os.name == 'nt':
        paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        ]
        for path in paths:
            if os.path.exists(path):
                print(f"Tesseract found at: {path}")
                os.environ['TESSERACT_PATH'] = path
                return True

    print("WARNING: Tesseract OCR not found in PATH")
    print("Install from: https://github.com/UB-Mannheim/tesseract/wiki")
    print("For Arabic support, install Arabic language data")
    return False

def main():
    mode = input("Select mode:\n1. Development (reload enabled)\n2. Production\n3. Install dependencies only\nChoice [1-3]: ").strip()

    if mode == "3":
        install_requirements()
        return

    if mode != "2":
        # Install dependencies first
        try:
            import fastapi
            print("Dependencies already installed")
        except ImportError:
            install_requirements()

    check_tesseract()

    import uvicorn
    from app.config import API_HOST, API_PORT

    if mode == "2":
        print(f"Starting production server on {API_HOST}:{API_PORT}")
        uvicorn.run("app.main:app", host=API_HOST, port=API_PORT)
    else:
        print(f"Starting development server on {API_HOST}:{API_PORT}")
        print("API docs available at: http://localhost:8000/docs")
        uvicorn.run("app.main:app", host=API_HOST, port=API_PORT, reload=True)

if __name__ == "__main__":
    main()
