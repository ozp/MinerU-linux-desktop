"""
MinerU Desktop Client - Version Information

This module contains version information for the application.
Update the VERSION variable when releasing new versions.

Versioning follows Semantic Versioning (semver.org):
- MAJOR version: Incompatible API changes
- MINOR version: New functionality in a backward compatible manner
- PATCH version: Backward compatible bug fixes
"""

# Application version
VERSION = "1.0.0"

# Version components
VERSION_MAJOR, VERSION_MINOR, VERSION_PATCH = VERSION.split(".")

# Full version string for display
VERSION_STRING = f"MinerU Desktop Client v{VERSION}"

# Short version for file names
VERSION_SHORT = VERSION


def get_version():
    """Return the current version string."""
    return VERSION


def get_version_string():
    """Return the full version string for display."""
    return VERSION_STRING


def get_version_info():
    """Return version information as a dictionary."""
    return {
        "version": VERSION,
        "major": VERSION_MAJOR,
        "minor": VERSION_MINOR,
        "patch": VERSION_PATCH,
        "string": VERSION_STRING
    }
