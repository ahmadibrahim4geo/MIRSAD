"""Independent MIRSAD desktop application."""
__version__ = "0.4.0.dev8"


def runtime_channel():
    import sys
    from pathlib import Path
    root=Path(sys.executable).parent
    return "stable" if getattr(sys,"frozen",False) and (root.name == "stable" or (root/"release.json").is_file()) else "development"
