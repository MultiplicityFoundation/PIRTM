from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .types import AceCertificate


@dataclass(frozen=True)
class AceWitness:
    """ACE witness envelope used for cross-system verification payloads."""

    certificate: AceCertificate
    prime_index: int

    def export(self) -> dict:
        payload = asdict(self.certificate)
        payload["level"] = self.certificate.level.value
        return {
            "primeIndex": int(self.prime_index),
            "certificate": payload,
        }

    @classmethod
    def from_certificate(cls, certificate: AceCertificate, prime_index: int) -> AceWitness:
        return cls(certificate=certificate, prime_index=prime_index)
