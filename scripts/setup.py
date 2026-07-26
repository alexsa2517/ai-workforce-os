#!/usr/bin/env python3
"""
Setup script for AI Workforce OS

This script helps with initial project setup including:
- Creating .env file from template
- Initializing database
- Installing dependencies
- Setting up pre-commit hooks
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path


def main():
    """Run the setup process."""
    print("=" * 60)
    print("AI Workforce OS - Setup")
    print("=" * 60)

    project_root = Path(__file__).parent.parent

    # Step 1: Create .env file
    print("\n[1/4] Setting up environment variables...")
    env_example = project_root / ".env.example"
    env_file = project_root / ".env"
    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("  ✓ Created .env from .env.example")
    elif env_file.exists():
        print("  ✓ .env already exists, skipping")
    else:
        print("  ✗ .env.example not found")

    # Step 2: Install dependencies
    print("\n[2/4] Installing dependencies...")
    backend_req = project_root / "backend" / "requirements.txt"
    if backend_req.exists():
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", str(backend_req)],
            check=False,
        )
        print("  ✓ Backend dependencies installed")
    else:
        print("  ✗ requirements.txt not found")

    # Step 3: Initialize database
    print("\n[3/4] Initializing database...")
    db_path = project_root / "backend" / "ai_workforce.db"
    if not db_path.exists():
        try:
            subprocess.run(
                [sys.executable, "-c", "from database.session import init_db; init_db()"],
                cwd=str(project_root / "backend"),
                check=False,
            )
            print("  ✓ Database initialized")
        except Exception as e:
            print(f"  ⚠ Database initialization skipped: {e}")
    else:
        print("  ✓ Database already exists")

    # Step 4: Install pre-commit hooks
    print("\n[4/4] Setting up pre-commit hooks...")
    try:
        result = subprocess.run(
            ["pre-commit", "install"],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode == 0:
            print("  ✓ Pre-commit hooks installed")
        else:
            print("  ⚠ Pre-commit not installed (pip install pre-commit)")
    except FileNotFoundError:
        print("  ⚠ pre-commit not found, skipping")

    print("\n" + "=" * 60)
    print("Setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Edit .env file with your API keys")
    print("  2. Run: make dev")
    print("  3. Open: http://localhost:8000/docs")
    print("")


if __name__ == "__main__":
    main()
