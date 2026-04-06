"""Allow running strainer as ``python -m strainer``."""

import sys

from strainer.cli import main

sys.exit(main(sys.argv))
