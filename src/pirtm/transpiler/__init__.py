from __future__ import annotations

from .models import TranspileResult
from .registry import get_handler
from .spec import TranspileSpec


def transpile(spec: TranspileSpec) -> TranspileResult:
    spec.validate()
    handler = get_handler(spec.input_type)
    result = handler(spec)
    if not isinstance(result, TranspileResult):
        raise TypeError("handler returned invalid transpile result")
    return result


__all__ = ["TranspileSpec", "TranspileResult", "transpile"]
