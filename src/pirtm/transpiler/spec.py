from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

from pirtm.gate import EmissionPolicy
from pirtm.petc import _is_prime


@dataclass(slots=True)
class TranspileSpec:
    input_type: Literal["data_asset", "computation", "workflow"]
    input_ref: str
    prime_index: int
    identity_commitment: str
    norm_id: str = "l2"
    domain_id: str = "ball_l2_R1"
    epsilon: float = 0.05
    max_steps: int = 1000
    emission_policy: str = "suppress"
    metadata: dict[str, Any] = field(default_factory=dict)
    dim: int = 8
    op_norm_T: float = 0.5

    def validate(self) -> None:
        if self.input_type not in {"data_asset", "computation", "workflow"}:
            raise ValueError(f"unsupported input_type: {self.input_type}")
        if not self.input_ref:
            raise ValueError("input_ref must be non-empty")
        if not _is_prime(int(self.prime_index)):
            raise ValueError(f"prime_index must be prime: {self.prime_index}")
        if not self.identity_commitment:
            raise ValueError("identity_commitment must be non-empty")
        if not (0.0 < float(self.epsilon) < 1.0):
            raise ValueError("epsilon must be in (0, 1)")
        if int(self.max_steps) < 1:
            raise ValueError("max_steps must be >= 1")
        if int(self.dim) < 1:
            raise ValueError("dim must be >= 1")
        if float(self.op_norm_T) <= 0.0:
            raise ValueError("op_norm_T must be > 0")
        valid_policies = {policy.value for policy in EmissionPolicy}
        if self.emission_policy not in valid_policies:
            raise ValueError(
                f"emission_policy must be one of {sorted(valid_policies)}; got {self.emission_policy}"
            )
