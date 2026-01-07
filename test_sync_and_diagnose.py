#!/usr/bin/env python3
"""
Run sync and then diagnostics to verify the fix.
"""

import sys
sys.path.insert(0, '.')

from roadmap import sync_all_to_graph
from app import diagnose_graph_contents

if __name__ == "__main__":
    print("=" * 60)
    print("STEP 1: Running sync_all_to_graph()")
    print("=" * 60)
    print()

    graph = sync_all_to_graph()

    print("\n" * 2)
    print("=" * 60)
    print("STEP 2: Running diagnostics")
    print("=" * 60)
    print()

    diagnose_graph_contents()
