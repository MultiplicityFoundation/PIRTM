from __future__ import annotations

from collections.abc import Callable

from .handlers.computation import transpile_computation
from .handlers.data_asset import transpile_data_asset
from .handlers.workflow import transpile_workflow

HandlerFn = Callable[..., object]


_REGISTRY: dict[str, HandlerFn] = {
    "data_asset": transpile_data_asset,
    "computation": transpile_computation,
    "workflow": transpile_workflow,
}


def get_handler(input_type: str) -> HandlerFn:
    try:
        return _REGISTRY[input_type]
    except KeyError as exc:
        raise ValueError(f"unsupported input_type: {input_type}") from exc
