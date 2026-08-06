#!/usr/bin/env python3
"""Compatibility entry point for the authoritative fail-closed proton-decay gate."""
from proton_decay_falsification_gate_v20 import *  # noqa: F401,F403
from proton_decay_falsification_gate_v20 import main

if __name__ == "__main__":
    raise SystemExit(main())
