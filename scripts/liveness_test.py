#!/usr/bin/env python3
"""Compatibility entry point for the instrumented fixed-token cache diagnostic.

The old free-generation/hook comparison was retired: generated histories can
 diverge and unchanged logits do not establish a no-op. See --help and
 docs/VALIDATION.md. Hooks are an optional, separately validated intervention.
"""
from test_kv_scoring_path import main

if __name__ == '__main__':
    main()
