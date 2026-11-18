"""String manipulation utilities."""

import re
import unicodedata


def normalize_whitespace(text: str) -> str:
    """Collapse consecutive whitespace into single spaces and strip ends.

    Uses ``str.split()``, which splits on all Unicode whitespace
    characters (including non-breaking space, NBSP U+00A0).

    Args:
        text: Input string to normalize.

    Returns:
        String with leading/trailing whitespace removed and internal runs
        of whitespace replaced by a single ASCII space.
    """
    return " ".join(text.split())


def slugify(text: str, separator: str = "-") -> str:
    """Convert text into a lowercase, ASCII-only URL-friendly slug.

    Args:
        text: Input string to convert.
        separator: Non-empty delimiter placed between alphanumeric tokens.

    Returns:
        Slugified string with leading/trailing separators stripped.

    Raises:
        ValueError: If ``separator`` is empty.
    """
    if not separator:
        raise ValueError("separator must be non-empty")
    ascii_text = (
        unicodedata.normalize("NFKD", text)
        .encode("ascii", "ignore")
        .decode("ascii")
        .lower()
    )
    tokens = re.findall(r"[a-z0-9]+", ascii_text)
    return separator.join(tokens)


def truncate(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to at most max_length characters, appending suffix.

    Args:
        text: Input string to truncate.
        max_length: Maximum allowed length of the returned string (>= 0).
        suffix: Ellipsis or marker appended when truncation occurs.

    Returns:
        Original text if within max_length, otherwise truncated text ending
        with suffix (or a prefix of suffix if max_length <= len(suffix)).

    Raises:
        ValueError: If ``max_length`` is negative.
    """
    if max_length < 0:
        raise ValueError("max_length must be non-negative")
    if len(text) <= max_length:
        return text
    if max_length <= len(suffix):
        return suffix[:max_length]
    cutoff = max_length - len(suffix)
    return f"{text[:cutoff].rstrip()}{suffix}"
