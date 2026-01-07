#!/usr/bin/env python3
"""
Run graph diagnostics to see what's in the unified graph.
"""

import sys
sys.path.insert(0, '.')

from app import diagnose_graph_contents

if __name__ == "__main__":
    print("Running unified graph diagnostics...\n")
    diagnose_graph_contents()
