#!/usr/bin/env python3
import os
import shutil
import subprocess
import sys
from pathlib import Path

def print_step(msg):
    print(f"\n{'-'*60}")
    print(f"👉 {msg}")
    print(f"{'-'*60}\n")

def check_requirements():
    try:
        import PyInstaller
    except ImportError:
        print_step("Installing PyInstaller...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

def clean_build_dirs():
    print_step("Cleaning old build directories")
    dirs_to_clean = ['build', 'dist']
    for d in dirs_to_clean:
        if os.path.exists(d):
            print(f"Removing {d}/...")
            shutil.rmtree(d)

def run_pyinstaller():
    print_step("Running PyInstaller build")
    try:
        subprocess.check_call(["pyinstaller", "contextgrid.spec", "--clean", "-y"])
        print_step("Build completed successfully!")
        print("Executables can be found in the 'dist' folder:")
        print("  - dist/contextgrid-api/contextgrid-api.exe")
        print("  - dist/contextgrid-web/contextgrid-web.exe")
        print("  - dist/cg/cg.exe")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Build failed with error code {e.returncode}")
        sys.exit(1)

if __name__ == "__main__":
    check_requirements()
    clean_build_dirs()
    run_pyinstaller()
