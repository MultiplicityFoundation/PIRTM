"""
PIRTM MLIR Emitter: Transpile PIRTM types to MLIR with mod= canonical form.

This module emits MLIR with proper PIRTM dialect type annotations using the
canonical mod= nomenclature per PIRTM ADR-004.

Spec Reference:
  - PIRTM ADR-004: mod= canonical form for all types
  - PIRTM ADR-007: Migration strategy (Day 3–7)

Changes from mlir_lowering.py:
  - All types use mod= (not .prime)
  - CertType, EpsilonType, OpNormTType expressed in MLIR
  - SessionGraph carries prime_index field (canonical per ADR-004 L0 #1)
"""

from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
import hashlib

from pirtm.channels.shim import PrimeChannelShim, SessionGraphShim
from pirtm.dialect.pirtm_types import CertType, EpsilonType, OpNormTType


@dataclass
class MLIREmitterConfig:
    """Configuration for MLIR emission with mod= canonical form."""
    
    prime_index: int = 7919  # Modulus for this module
    epsilon: float = 0.05   # Convergence bound ε
    op_norm_T: float = 1.0  # Operator norm ‖T‖


class PIRTMMLIREmitter:
    """
    Emit MLIR with proper PIRTM dialect types using mod= canonical form.
    
    Every type in the emitted MLIR uses mod= instead of property access.
    Example:
      !pirtm.cert(mod=7919)
      !pirtm.epsilon(mod=7919, value=0.05)
      !pirtm.op_norm_t(mod=7919, norm=1.0)
      !pirtm.session_graph(mod=62595733, coupling=#pirtm.unresolved_coupling)
    """
    
    def __init__(self, config: Optional[MLIREmitterConfig] = None):
        """Initialize emitter with optional config."""
        self.config = config or MLIREmitterConfig()
        self._indent = "  "
        self._indent_level = 0
    
    def emit_module(
        self,
        module_name: str = "pirtm_module",
        components: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Emit complete MLIR module with PIRTM dialect types.
        
        Args:
            module_name: Name for the MLIR module
            components: Optional list of component dicts with prime_index, epsilon, op_norm_T
        
        Returns:
            Complete MLIR module string with mod= canonical form
        """
        lines: List[str] = []
        
        # Module header
        lines.append(f'module @{module_name} {{')
        lines.append('')
        
        # Module-level attributes (PIRTM metadata)
        lines.append('  // PIRTM Module Metadata (ADR-006)')
        lines.append(f'  #pirtm.module_attr = {{')
        lines.append(f'    prime_index = {self.config.prime_index} : i64,')
        lines.append(f'    epsilon = {self.config.epsilon} : f32,')
        lines.append(f'    op_norm_T = {self.config.op_norm_T} : f32')
        lines.append(f'  }}')
        lines.append('')
        
        # Type definitions (using canonical mod= form)
        lines.append('  // Type Definitions (canonical mod= form)')
        cert_type = f'!pirtm.cert(mod={self.config.prime_index})'
        epsilon_type = f'!pirtm.epsilon(mod={self.config.prime_index}, value={self.config.epsilon})'
        op_norm_type = f'!pirtm.op_norm_t(mod={self.config.prime_index}, norm={self.config.op_norm_T})'
        
        lines.append(f'  // Cert type: {cert_type}')
        lines.append(f'  // Epsilon type: {epsilon_type}')
        lines.append(f'  // OpNormT type: {op_norm_type}')
        lines.append('')
        
        # SessionGraph (composite, might have coupling)
        lines.append('  // Session Graph (L0 invariant #1: exactly one prime_index)')
        lines.append(f'  #pirtm.session_graph_attr = {{')
        lines.append(f'    prime_index = {self.config.prime_index} : i64,')
        lines.append(f'    coupling = #pirtm.unresolved_coupling')
        lines.append(f'  }}')
        lines.append('')
        
        # Placeholder recurrence function with types
        lines.append('  func.func @recurrence(%x : tensor<?xf32>) -> tensor<?xf32> {')
        lines.append('    // Contractivity check placeholder')
        lines.append('    // Spec Reference: PIRTM ADR-004 L0 invariant #2')
        lines.append('    //   contractivity-check runs at transpile-time')
        lines.append('    //   spectral-small-gain runs at link-time')
        lines.append('    %result = %x : tensor<?xf32>')
        lines.append('    return %result : tensor<?xf32>')
        lines.append('  }')
        lines.append('')
        
        # Closing brace
        lines.append('}')
        
        return '\n'.join(lines)
    
    def emit_cert_type(self, mod: int) -> str:
        """Emit PIRTM cert type with canonical mod= form."""
        return f"!pirtm.cert(mod={mod})"
    
    def emit_epsilon_type(self, mod: int, value: float) -> str:
        """Emit PIRTM epsilon type with canonical mod= form."""
        return f"!pirtm.epsilon(mod={mod}, value={value})"
    
    def emit_op_norm_t_type(self, mod: int, norm: float) -> str:
        """Emit PIRTM op_norm_t type with canonical mod= form."""
        return f"!pirtm.op_norm_t(mod={mod}, norm={norm})"
    
    def emit_session_graph_type(self, prime_index: int, coupling_attr: str = "#pirtm.unresolved_coupling") -> str:
        """
        Emit PIRTM session_graph type with canonical form.
        
        Args:
            prime_index: Module modulus (prime or squarefree composite)
            coupling_attr: Coupling matrix attribute (default: unresolved)
        
        Returns:
            MLIR type string using mod= form
        """
        return f"!pirtm.session_graph(mod={prime_index}, coupling={coupling_attr})"
    
    def emit_unresolved_coupling(self) -> str:
        """Emit placeholder for unresolved coupling (L0 invariant #4)."""
        return "#pirtm.unresolved_coupling"
    
    def emit_proof_hash_block(self, prime_index: int, epsilon: float, op_norm_T: float) -> str:
        """
        Emit !pirtm_proof section with parameters (Day 14 gate requirement).
        
        This section carries proof_hash = H(prime_index ∥ ε ∥ op_norm_T ∥ ...)
        and is used in the VIN composition (four-level hash tree, ADR-009).
        """
        # Compute deterministic proof hash
        params_str = f"{prime_index}|{epsilon}|{op_norm_T}"
        proof_hash = hashlib.sha256(params_str.encode()).hexdigest()[:16]
        
        return (
            f'!pirtm_proof {{\n'
            f'  prime_index = {prime_index} : i64,\n'
            f'  epsilon = {epsilon} : f32,\n'
            f'  op_norm_T = {op_norm_T} : f32,\n'
            f'  proof_hash = "0x{proof_hash}"\n'
            f'}}'
        )


class RoundTripValidator:
    """Validate round-trip of examples via MLIR emission."""
    
    @staticmethod
    def can_emit(component: Dict[str, Any]) -> bool:
        """Check if component has required fields for emission."""
        required = {'prime_index', 'epsilon', 'op_norm_T'}
        return all(k in component for k in required)
    
    @staticmethod
    def emit_component(component: Dict[str, Any]) -> str:
        """Emit MLIR for a single component."""
        emitter = PIRTMMLIREmitter(
            config=MLIREmitterConfig(
                prime_index=component['prime_index'],
                epsilon=component['epsilon'],
                op_norm_T=component['op_norm_T'],
            )
        )
        return emitter.emit_module(module_name=f"component_{component['prime_index']}")
    
    @staticmethod
    def validate_no_prime_refs(mlir_text: str) -> bool:
        """Check that MLIR uses only mod= (no .prime property access)."""
        # Should not contain property access syntax
        if ".prime" in mlir_text:
            return False
        return True


if __name__ == "__main__":
    # Example: emit a simple module
    emitter = PIRTMMLIREmitter(
        MLIREmitterConfig(prime_index=7919, epsilon=0.12, op_norm_T=4.35)
    )
    mlir = emitter.emit_module("example_module")
    print(mlir)
    
    # Validate no .prime in output
    has_prime = ".prime" in mlir
    has_mod = "mod=" in mlir
    print(f"\n✅ No .prime property access: {not has_prime}")
    print(f"✅ Uses mod= canonical form: {has_mod}")
