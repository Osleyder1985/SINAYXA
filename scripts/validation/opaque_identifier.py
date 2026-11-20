"""Generate non-semantic UUIDv4 identifiers using the operating system CSPRNG."""
from __future__ import annotations

import secrets
import uuid


def generate_opaque_id() -> str:
    """Return a canonical lowercase UUIDv4 using secrets.token_bytes.

    This helper creates new identifiers only. Historical migration must never
    call it to replace an existing subject, audit, retention or copy reference.
    """
    random_bytes = bytearray(secrets.token_bytes(16))
    if len(random_bytes) != 16:
        raise RuntimeError("the secure random source did not return exactly 16 bytes")
    random_bytes[6] = (random_bytes[6] & 0x0F) | 0x40
    random_bytes[8] = (random_bytes[8] & 0x3F) | 0x80
    return str(uuid.UUID(bytes=bytes(random_bytes)))


def is_canonical_opaque_id(value: object) -> bool:
    """Check canonical lowercase UUIDv4 syntax; this does not prove provenance."""
    if not isinstance(value, str):
        return False
    try:
        parsed = uuid.UUID(value)
    except (ValueError, AttributeError, TypeError):
        return False
    return parsed.version == 4 and str(parsed) == value
