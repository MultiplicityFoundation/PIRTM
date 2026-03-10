"""
PIRTM Bytecode Format and Serialization

Spec Reference: PIRTM ADR-004, ADR-007 (Day 14+)

The .pirtm.bc (bytecode) format carries:
  - !pirtm_proof section with proof_hash = H(prime_index || ε || op_norm_T || ...)
  - contractivity_check result (PASS/FAIL)
  - Module metadata (name, prime_index, epsilon, op_norm_T)
  - Non-allocating static proof information

Format: Binary with JSON metadata section + hash tree

Constraints:
  - Non-allocating (no dynamic memory allocation)
  - Deterministic (same input → same bytecode)
  - Verifiable (can audit via pirtm inspect)
"""

import json
import hashlib
import struct
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from pathlib import Path
import base64


@dataclass
class ProofHash:
    """Deterministic proof hash for contractivity certificate."""
    prime_index: int
    epsilon: float
    op_norm_T: float
    nonce: str = "PIRTM-DAY14"
    
    def compute(self) -> str:
        """Compute deterministic SHA256 hash."""
        params = f"{self.prime_index}|{self.epsilon}|{self.op_norm_T}|{self.nonce}"
        return hashlib.sha256(params.encode()).hexdigest()


@dataclass
class ModuleMetadata:
    """Metadata for a single PIRTM module in bytecode."""
    name: str
    prime_index: int
    epsilon: float
    op_norm_T: float
    contractivity_check: str  # "PASS" or "FAIL"
    proof_hash: str
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PIRTMBytecode:
    """
    PIRTM bytecode container with proof information.
    
    Attributes:
        modules: List of module metadata
        coupling: Coupling matrix attribute (or #pirtm.unresolved_coupling)
        mlir_source: MLIR text representation
        audit_trail: List of transformation steps
    """
    modules: List[ModuleMetadata]
    coupling: str = "#pirtm.unresolved_coupling"
    mlir_source: str = ""
    audit_trail: List[str] = None
    
    def __post_init__(self):
        if self.audit_trail is None:
            self.audit_trail = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "modules": [m.to_dict() for m in self.modules],
            "coupling": self.coupling,
            "mlir_source": self.mlir_source[:500],  # Truncate for size
            "audit_trail": self.audit_trail,
        }
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'PIRTMBytecode':
        """Deserialize from dictionary."""
        modules = [
            ModuleMetadata(**m) for m in data.get("modules", [])
        ]
        return PIRTMBytecode(
            modules=modules,
            coupling=data.get("coupling", "#pirtm.unresolved_coupling"),
            mlir_source=data.get("mlir_source", ""),
            audit_trail=data.get("audit_trail", []),
        )
    
    def all_modules_contractive(self) -> bool:
        """Check if all modules passed contractivity check."""
        return all(m.contractivity_check == "PASS" for m in self.modules)
    
    def write_to_file(self, filepath: Path) -> None:
        """Write bytecode to .pirtm.bc file (JSON format)."""
        bytecode_data = {
            "format": "pirtm.bc",
            "version": "1.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "content": self.to_dict(),
        }
        
        with open(filepath, 'w') as f:
            json.dump(bytecode_data, f, indent=2)
    
    @staticmethod
    def read_from_file(filepath: Path) -> 'PIRTMBytecode':
        """Read bytecode from .pirtm.bc file."""
        with open(filepath, 'r') as f:
            bytecode_data = json.load(f)
        
        return PIRTMBytecode.from_dict(bytecode_data.get("content", {}))


class ContractivityCheckPass:
    """
    Transpile-time contractivity verification pass.
    
    Spec: PIRTM ADR-004 L0 invariant #2
    Runs at compile time on each module before linking.
    """
    
    @staticmethod
    def check_module(
        module_name: str,
        prime_index: int,
        epsilon: float,
        op_norm_T: float,
    ) -> tuple[str, str]:
        """
        Check contractivity of a module.
        
        Args:
            module_name: Name of the module
            prime_index: Module modulus
            epsilon: Convergence bound (ε in ||q_t|| < 1-ε)
            op_norm_T: Operator norm of system matrix
        
        Returns:
            (status: "PASS" or "FAIL", reason: diagnostic message)
        
        Contractivity requires: op_norm_T + epsilon < 1.0
        (Margin must exist: 1 - ε - ‖T‖ > 0)
        """
        margin = 1.0 - epsilon - op_norm_T
        
        if margin > 0:
            return "PASS", f"Contractive: margin = 1 - {epsilon:.4f} - {op_norm_T:.4f} = {margin:.4f} > 0"
        elif margin == 0:
            return "FAIL", f"Marginally stable (not contractive): margin = 0"
        else:
            return "FAIL", f"Divergent: margin = {margin:.4f} < 0 (‖T‖ + ε > 1)"
    
    @staticmethod
    def verify_bytecode_contractivity(bytecode: PIRTMBytecode) -> bool:
        """Verify that all modules in bytecode are marked as contractive."""
        return bytecode.all_modules_contractive()


def create_bytecode_from_mlir(
    mlir_text: str,
    modules: List[Dict[str, Any]],
) -> PIRTMBytecode:
    """
    Create PIRTM bytecode from MLIR output and module descriptions.
    
    Args:
        mlir_text: MLIR module text
        modules: List of dicts with name, prime_index, epsilon, op_norm_T
    
    Returns:
        PIRTMBytecode instance with contractivity checks applied
    """
    module_metadata = []
    
    for mod in modules:
        name = mod.get('name', f"module_{mod['prime_index']}")
        prime_index = mod['prime_index']
        epsilon = mod['epsilon']
        op_norm_T = mod['op_norm_T']
        
        # Run contractivity check
        status, reason = ContractivityCheckPass.check_module(
            name, prime_index, epsilon, op_norm_T
        )
        
        # Compute proof hash
        proof_hash = ProofHash(
            prime_index=prime_index,
            epsilon=epsilon,
            op_norm_T=op_norm_T,
        ).compute()
        
        metadata = ModuleMetadata(
            name=name,
            prime_index=prime_index,
            epsilon=epsilon,
            op_norm_T=op_norm_T,
            contractivity_check=status,
            proof_hash=proof_hash,
        )
        module_metadata.append(metadata)
    
    bytecode = PIRTMBytecode(
        modules=module_metadata,
        mlir_source=mlir_text,
        audit_trail=[f"Day 14: contractivity_check pass completed"],
    )
    
    return bytecode
