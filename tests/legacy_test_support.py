# -*- coding: utf-8 -*-
"""Owned scratch for Python 2/3 legacy tests; no Desktop runtime dependency."""
from __future__ import unicode_literals
import os
import tempfile

def temporary_workspace():
    folder=os.path.join(os.path.dirname(os.path.abspath(__file__)),'.output')
    try:os.makedirs(folder)
    except OSError:
        if not os.path.isdir(folder):raise
    return tempfile.mkdtemp(prefix='legacy-',dir=folder)
