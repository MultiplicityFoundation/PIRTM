from __future__ import annotations

import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pirtm.audit import AuditChain

    from .spec import TranspileSpec


def bind_identity(audit: AuditChain, spec: TranspileSpec) -> None:
    audit.append_payload(
        {
            "type": "identity_binding",
            "prime_index": int(spec.prime_index),
            "identity_commitment": str(spec.identity_commitment),
            "timestamp": time.time(),
        }
    )
