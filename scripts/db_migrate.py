#!/usr/bin/env python3
"""
Database Migration Utility

Run database migrations using Alembic.
Usage:
    python scripts/db_migrate.py upgrade    # Run all pending migrations
    python scripts/db_migrate.py downgrade   # Rollback last migration
    python scripts/db_migrate.py status      # Show migration status
    python scripts/db_migrate.py generate "description"  # Generate new migration
"""

import os
import sys
import subprocess
from pathlib import Path


def main():
    """Run database migration commands."""
    project_root = Path(__file__).parent.parent
    backend_dir = project_root / "backend"

    if not (backend_dir / "alembic.ini").exists():
        print("Error: alembic.ini not found in backend/")
        sys.exit(1)

    args = sys.argv[1:]
    if not args:
        print("Usage: python scripts/db_migrate.py <command>")
        print("Commands: upgrade, downgrade, status, generate <description>, revision <description>")
        sys.exit(1)

    command = args[0]

    if command == "upgrade":
        print("Running migrations...")
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"],
            cwd=str(backend_dir),
            check=True,
        )
        print("✓ Migrations complete")

    elif command == "downgrade":
        print("Rolling back migration...")
        subprocess.run(
            [sys.executable, "-m", "alembic", "downgrade", "-1"],
            cwd=str(backend_dir),
            check=True,
        )
        print("✓ Rollback complete")

    elif command == "status":
        subprocess.run(
            [sys.executable, "-m", "alembic", "current", "-v"],
            cwd=str(backend_dir),
        )
        print("---")
        subprocess.run(
            [sys.executable, "-m", "alembic", "heads", "-v"],
            cwd=str(backend_dir),
        )

    elif command == "generate":
        if len(args) < 2:
            print("Usage: python scripts/db_migrate.py generate <description>")
            sys.exit(1)
        description = args[1]
        subprocess.run(
            [sys.executable, "-m", "alembic", "revision", "--autogenerate", "-m", description],
            cwd=str(backend_dir),
            check=True,
        )
        print(f"✓ Migration '{description}' generated")

    elif command == "revision":
        if len(args) < 2:
            print("Usage: python scripts/db_migrate.py revision <description>")
            sys.exit(1)
        description = args[1]
        subprocess.run(
            [sys.executable, "-m", "alembic", "revision", "-m", description],
            cwd=str(backend_dir),
            check=True,
        )
        print(f"✓ Revision '{description}' created")

    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
