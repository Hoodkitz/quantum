import os
import shutil
import subprocess
import zipfile
import sys

GENERATED_DIR = "generated_output"

def ensure_generated_dir():
    if not os.path.exists(GENERATED_DIR):
        os.makedirs(GENERATED_DIR)

def save_code(code: str, filename: str = "main.py") -> str:
    ensure_generated_dir()
    filepath = os.path.join(GENERATED_DIR, filename)
    with open(filepath, "w") as f:
        f.write(code)
    return filepath

def create_requirements():
    ensure_generated_dir()
    # Ensure compatible versions are requested
    reqs = """tensorflow==2.16.2
tensorflow-quantum==0.7.5
cirq
sympy
numpy
matplotlib
"""
    filepath = os.path.join(GENERATED_DIR, "requirements.txt")
    with open(filepath, "w") as f:
        f.write(reqs)
    return filepath

def create_zip_package(base_filename: str = "quantum_app"):
    ensure_generated_dir()
    create_requirements()

    zip_path = os.path.join(GENERATED_DIR, f"{base_filename}.zip")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        # Add generated python file
        if os.path.exists(os.path.join(GENERATED_DIR, "main.py")):
            zipf.write(os.path.join(GENERATED_DIR, "main.py"), arcname="main.py")
        # Add requirements
        if os.path.exists(os.path.join(GENERATED_DIR, "requirements.txt")):
            zipf.write(os.path.join(GENERATED_DIR, "requirements.txt"), arcname="requirements.txt")

        # Add a readme
        readme_content = """
To run this application:
1. Install Python 3.10+
2. Run: pip install -r requirements.txt
3. Run: python main.py
"""
        zipf.writestr("README.txt", readme_content)

    return zip_path

def build_exe(script_path: str):
    """
    Runs PyInstaller to create an executable.
    Note: This builds for the CURRENT OS. To build Windows .exe, this script must run on Windows.
    """
    try:
        # Check if pyinstaller is available
        subprocess.check_call([sys.executable, "-m", "pyinstaller", "--version"])

        dist_path = os.path.join(GENERATED_DIR, "dist")
        work_path = os.path.join(GENERATED_DIR, "build")

        cmd = [
            sys.executable, "-m", "pyinstaller",
            "--onefile",
            "--distpath", dist_path,
            "--workpath", work_path,
            "--specpath", GENERATED_DIR,
            "--name", "QuantumApp",
            script_path
        ]

        process = subprocess.run(cmd, capture_output=True, text=True)

        if process.returncode != 0:
            return None, f"PyInstaller Failed:\n{process.stderr}"

        # Find the output file
        exe_name = "QuantumApp.exe" if os.name == 'nt' else "QuantumApp"
        exe_path = os.path.join(dist_path, exe_name)

        if os.path.exists(exe_path):
            return exe_path, "Success"
        else:
            return None, "Executable not found after build."

    except Exception as e:
        return None, str(e)
