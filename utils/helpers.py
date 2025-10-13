# utils/helpers.py
"""
Helper utilities used across services
"""

import re
import unicodedata
from datetime import datetime
from typing import Any, Dict


def sanitize_filename(name: str, max_length: int = 200) -> str:
    """
    Sanitize a string to be safe for use as a filename across platforms.

    - Removes or replaces invalid filesystem characters
    - Normalizes unicode characters to ASCII where possible
    - Trims spaces and dots at ends
    - Enforces a maximum length
    """
    if not isinstance(name, str):
        name = str(name)

    # Normalize unicode → ASCII
    name = unicodedata.normalize("NFKD", name)
    name = name.encode("ascii", "ignore").decode("ascii")

    # Replace invalid characters
    name = re.sub(r'[<>:"/\\|?*]', "_", name)

    # Collapse whitespace
    name = re.sub(r"\s+", " ", name).strip()

    # Remove leading/trailing dots and spaces
    name = name.strip(" .")

    # Enforce max length
    if len(name) > max_length:
        name = name[:max_length]

    # Fallback if empty after cleaning
    if not name:
        name = "unnamed"

    return name


def timestamp_str(fmt: str = "%Y%m%d_%H%M%S") -> str:
    """
    Return current timestamp as string, safe for filenames.
    """
    return datetime.now().strftime(fmt)


def dict_safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """
    Safely get a key from a dictionary, returning default if missing or None.
    """
    try:
        value = data.get(key, default)
        return value if value is not None else default
    except Exception:
        return default
