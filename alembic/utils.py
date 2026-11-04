import re
import unicodedata


def strip_non_utf8(value: str) -> str:
    """Remove characters that aren't valid, printable UTF-8 text."""
    # Drop anything that can't be encoded as UTF-8 (e.g. lone surrogates)
    value = value.encode("utf-8", errors="ignore").decode("utf-8")
    # Drop the replacement char left by earlier bad decodes, and control chars
    return "".join(
        ch for ch in value
        if ch != "\ufffd" and (ch.isspace() or unicodedata.category(ch)[0] != "C")
    )


def normalise_label(value: str | None) -> str | None:
    """Clean a free-text label: valid UTF-8 only, single-spaced, trimmed, blanks as None."""
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", strip_non_utf8(value)).strip()
    return cleaned or None