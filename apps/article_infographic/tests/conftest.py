import sys
from pathlib import Path

TESTS = Path(__file__).resolve().parent
SRC = TESTS.parents[0] / "src"
for path in (SRC, TESTS):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))
