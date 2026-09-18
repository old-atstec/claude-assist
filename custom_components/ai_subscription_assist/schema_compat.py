"""Schema -> OpenAPI/JSON-schema conversion across Home Assistant versions.

Home Assistant 2026.9 replaced voluptuous with probatio and no longer ships
``voluptuous_openapi``. Inside HA the ``voluptuous`` module name is aliased to
probatio's shim, so probatio's ``to_openapi`` handles the schemas we build.
Older HA releases (< 2026.9) still ship ``voluptuous_openapi``, so fall back
to it there.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

try:
    from probatio import UNSUPPORTED
    from probatio import to_openapi as _to_openapi
except ImportError:  # Home Assistant < 2026.9
    from voluptuous_openapi import UNSUPPORTED
    from voluptuous_openapi import convert as _to_openapi


def convert(
    schema: Any, *, custom_serializer: Callable[[Any], Any] | None = None
) -> dict[str, Any]:
    """Convert a voluptuous/probatio schema to an OpenAPI/JSON schema dict."""
    return _to_openapi(schema, custom_serializer=custom_serializer)


__all__ = ["UNSUPPORTED", "convert"]
