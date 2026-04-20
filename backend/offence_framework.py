# DO NOT UNDO — offence_framework module (now a back-compat shim after
# the P2 refactor on 2026-02-14). Real content lives in /app/backend/frameworks/.
# All existing `from offence_framework import X` statements continue to work
# unchanged.
"""
Back-compat re-export shim. Prefer importing from `frameworks` directly in
new code. This file exists only to avoid breaking existing import paths.
"""
from frameworks import *  # noqa: F401, F403
from frameworks import __all__  # noqa: F401
