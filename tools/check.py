"""check.py: the one-command check (tests + text lint). The pre-commit hook runs this; exit code gates the commit."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

rc = subprocess.call([sys.executable, "-X", "utf8", "-m", "pytest", "-q", str(ROOT / "tests")], cwd=ROOT)
rc |= subprocess.call([sys.executable, "-X", "utf8", str(ROOT / "tools/lint.py")], cwd=ROOT)
sys.exit(rc)
