import os
import subprocess
import sys
import platform

venv_dir = "venv"

# 1. Create the virtual environment
subprocess.check_call([sys.executable, "-m", "venv", venv_dir])

# 2. Determine the path to pip inside the venv
if platform.system() == "Windows":
    pip_path = os.path.join(venv_dir, "Scripts", "pip.exe")
else:
    pip_path = os.path.join(venv_dir, "bin", "pip")

# 3. Install requirements.txt if it exists
requirements_file = "requirements.txt"
if os.path.isfile(requirements_file):
    subprocess.check_call([pip_path, "install", "-r", requirements_file])
    print("✅ Installed dependencies from requirements.txt")
else:
    print("⚠️ No requirements.txt found, skipping install.")

# 4. Show user how to activate
print("\n✅ Virtual environment created!")
if platform.system() == "Windows":
    print("To activate it:")
    print(rf"  Command Prompt: {venv_dir}\Scripts\activate.bat")
    print(rf"  PowerShell:     {venv_dir}\Scripts\Activate.ps1")
else:
    print(f"To activate it:\n  source {venv_dir}/bin/activate")
