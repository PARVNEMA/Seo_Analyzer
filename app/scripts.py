"""Project scripts.

These scripts are registered in ``pyproject.toml`` under ``[project.scripts]``
and can be executed directly via ``uv run <script_name>``.
"""

import subprocess
import sys

def dev() -> None:
    """Run the FastAPI development server with hot-reloading."""
    try:
        subprocess.run(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--reload",
                "--port",
                "8000",
            ],
            check=True,
        )
    except KeyboardInterrupt:
        print("\nServer stopped.")
