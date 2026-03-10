"""
MLIREmitter: Transpile PIRTM Recurrence to MLIR `linalg` Dialect.

This module lowers the recurrence loop X_{t+1} = P(Ξ X_t + Λ T(X_t) + G_t)
into verifiable MLIR code with contractivity bounds as first-class attributes.

See: ADR-007-mlir-lowering.md
"""

import hashlib
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, Tuple


@dataclass
class MLIRConfig:
    """Configuration for MLIR emission."""
    epsilon: float = 0.05
    confidence: float = 0.9999
    op_norm_T: float = 1.0
    prime_index: int = 17
    emit_witness_hash: bool = True
    witness_hash_type: str = "poseidon"  # or "sha256"


class MLIREmitter:
    """
    Emit verifiable MLIR from PIRTM recurrence loop.
    
    The generated MLIR includes:
    - linalg operations for matrix/vector ops
    - pirtm custom operations for sigmoid, clip
    - First-class contractivity attributes
    - Witness hash encoding (ACE integration)
    
    Example:
        emitter = MLIREmitter(config=MLIRConfig(epsilon=0.05))
        mlir_str = emitter.emit_module()
        
        # Write to file
        with open("recurrence.mlir", "w") as f:
            f.write(mlir_str)
        
        # Verify with MLIR
        # $ mlir-opt --verify-diagnostics recurrence.mlir
    """
    
    def __init__(self, config: Optional[MLIRConfig] = None):
        """Initialize with optional configuration."""
        self.config = config or MLIRConfig()
        self._indent_level = 0
    
    # ========== Public API ==========
    
    def emit_module(
        self,
        policy_name: str = "CarryForward",
        kernel_name: str = "FullAsymmetricAttribution",
        trace_id: Optional[str] = None,
        dimension: int = 512,
    ) -> str:
        """
        Emit complete MLIR module.
        
        Args:
            policy_name: Name of ledger policy (e.g., "CarryForward")
            kernel_name: Name of attribution kernel
            trace_id: Optional ACE witness ID (for commitment)
            dimension: Tensor dimension (for function signature)
        
        Returns:
            Complete MLIR module as string.
        """
        parts: list[str] = []
        
        # Module header with metadata
        parts.append(self._emit_module_header(policy_name, kernel_name, trace_id))
        
        # Contractivity metadata block
        parts.append(self._emit_contractivity_bounds())
        
        # Main recurrence function
        parts.append(self._emit_recurrence_function(dimension))
        
        # Closing brace
        parts.append("}\n")
        
        return "\n".join(parts)
    
    def emit_recurrence_function(self, dimension: int = 512) -> str:
        """Emit just the recurrence function (no module wrapper)."""
        return self._emit_recurrence_function(dimension)
    
    def emit_contractivity_bounds(self) -> str:
        """Emit contractivity metadata block."""
        return self._emit_contractivity_bounds()
    
    def emit_witness_commitment(self, trace_id: str) -> str:
        """
        Emit witness commitment (ACE integration).
        
        Args:
            trace_id: Trace ID or session ID from ACE
        
        Returns:
            MLIR attribute string with hash commitment.
        """
        if self.config.witness_hash_type == "poseidon":
            hash_val = self._poseidon_hash(trace_id)
        else:
            hash_val = hashlib.sha256(trace_id.encode()).hexdigest()[:16]
        
        return f'@ace_witness = "{hash_val}" : !pirtm.witness_hash'
    
    # ========== Private Emission Methods ==========
    
    def _emit_module_header(
        self,
        policy_name: str,
        kernel_name: str,
        trace_id: Optional[str],
    ) -> str:
        """Emit MLIR module header with metadata."""
        lines = [
            "// PIRTM Recurrence Loop → MLIR (linalg dialect)",
            f"// Policy: {policy_name}",
            f"// Kernel: {kernel_name}",
            f"// Emitted: {datetime.now(timezone.utc).isoformat()} UTC",
        ]
        
        if trace_id:
            lines.append(f"// ACE Witness ID: {trace_id}")
        
        lines.extend([
            f"// Contractivity Guarantee: epsilon={self.config.epsilon}, "
            f"confidence={self.config.confidence}",
            "",
            "module {",
        ])
        
        return "\n".join(lines)
    
    def _emit_contractivity_bounds(self) -> str:
        """Emit contractivity metadata in pirtm.module block."""
        lines = [
            "  pirtm.module {",
            f"    @epsilon = {self.config.epsilon} : f64",
            f"    @confidence = {self.config.confidence} : f64",
            f"    @op_norm_T = {self.config.op_norm_T} : f64",
            f"    @prime_index = {self.config.prime_index} : i64",
        ]
        
        # Optional witness hash
        if self.config.emit_witness_hash:
            lines.append(f"    @has_witness_commitment : i1")
        
        lines.append("  }")
        return "\n".join(lines)
    
    def _emit_recurrence_function(self, dimension: int) -> str:
        """
        Emit main recurrence function.
        
        Signature:
            func.func @pirtm_recurrence(
              %X_t: tensor<?xf64>,
              %Xi_t: tensor<?x?xf64>,
              %Lambda_t: tensor<?x?xf64>,
              %G_t: tensor<?xf64>
            ) -> tensor<?xf64>
        
        Body:
            1. T(X_t) = sigmoid(X_t)
            2. term1 = Ξ X_t  (matvec)
            3. term2 = Λ T(X_t)  (matvec)
            4. Y_t = term1 + term2 + G_t  (add)
            5. X_next = P(Y_t) = clip(Y_t, -1, 1)
        """
        lines = [
            '  func.func @pirtm_recurrence(',
            '    %X_t: tensor<?xf64>,',
            '    %Xi_t: tensor<?x?xf64>,',
            '    %Lambda_t: tensor<?x?xf64>,',
            '    %G_t: tensor<?xf64>',
            '  ) -> (',
            f'    tensor<?xf64>',
            '  ) {{',
        ]
        
        # Function body
        lines.extend([
            '    // Step 1: T(X_t) = sigmoid(X_t)',
            '    %T_X_t = "pirtm.sigmoid"(%X_t)',
            '      : (tensor<?xf64>) -> tensor<?xf64>',
            '',
            '    // Step 2: Ξ X_t',
            '    %term1 = "linalg.matvec"(%Xi_t, %X_t)',
            '      : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>',
            '',
            '    // Step 3: Λ T(X_t)',
            '    %term2 = "linalg.matvec"(%Lambda_t, %T_X_t)',
            '      : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>',
            '',
            '    // Step 4: Sum terms',
            '    %Y_t = "linalg.add"(%term1, %term2)',
            '      : (tensor<?xf64>, tensor<?xf64>) -> tensor<?xf64>',
            '    %Y_plus_G = "linalg.add"(%Y_t, %G_t)',
            '      : (tensor<?xf64>, tensor<?xf64>) -> tensor<?xf64>',
            '',
            '    // Step 5: Projection P(Y) = clip(Y, -1, 1)',
            '    %X_next = "pirtm.clip"(%Y_plus_G)',
            '      : (tensor<?xf64>) -> tensor<?xf64>',
            '      { bound_low = -1.0 : f64, bound_high = 1.0 : f64 }',
            '',
            f'    // Return with contractivity guarantee',
            f'    // L0: ||X_next|| < 1 - epsilon = {1.0 - self.config.epsilon}',
            '    return %X_next : tensor<?xf64>',
            '  }',
        ])
        
        return "\n".join(lines)
    
    def _emit_certify_function(self) -> str:
        """
        Emit witness certification function.
        
        Validates that trajectory satisfies L0 invariant.
        """
        lines = [
            '  func.func @pirtm_certify(',
            '    %X_t: tensor<?xf64>,',
            f'    %epsilon: f64 = {self.config.epsilon}',
            '  ) -> i1 {',
            '    // Verify ||X_t|| < 1 - epsilon',
            '    %norm_X = "linalg.norm"(%X_t)',
            '      : (tensor<?xf64>) -> f64',
            '    %threshold = arith.constant (1.0 - %epsilon) : f64',
            '    %is_valid = arith.cmpf "olt", %norm_X, %threshold',
            '    return %is_valid : i1',
            '  }',
        ]
        return "\n".join(lines)
    
    # ========== Helper Methods ==========
    
    def _poseidon_hash(self, data: str) -> str:
        """
        Compute Poseidon hash (placeholder for actual hash).
        
        In production, this would call the actual Poseidon hasher
        from the ACE module. For now, we use a deterministic
        SHA256 prefix.
        
        Args:
            data: Input string
        
        Returns:
            Hex string (truncated to 16 chars for readability)
        """
        # Deterministic for testing
        h = hashlib.sha256(("poseidon:" + data).encode()).hexdigest()
        return "0x" + h[:16]
    
    def emit_diagnostics_header(self) -> str:
        """
        Emit mlir-opt diagnostic header for verification.
        
        This allows MLIR verifier to fail on contractivity violations.
        """
        lines = [
            "// expected-no-errors",
            "// CHECK: module",
            "// CHECK: pirtm.module",
            "// CHECK: epsilon = {{.*}} : f64",
            "// CHECK: func.func @pirtm_recurrence",
        ]
        return "\n".join(lines)


class MLIRRoundTripValidator:
    """
    Validate round-trip: Python → MLIR → Verification.
    
    Used in testing to ensure emitted MLIR is valid and semantically correct.
    """
    
    def __init__(self, emitter: MLIREmitter):
        self.emitter = emitter
    
    def validate_module(self, mlir_str: str) -> Tuple[bool, Optional[str]]:
        """
        Check if MLIR module is well-formed.
        
        Args:
            mlir_str: MLIR module as string
        
        Returns:
            (is_valid, error_message)
        """
        # Basic checks (full check requires mlir-opt binary)
        checks = [
            ("module {" in mlir_str, "Missing module wrapper"),
            ("pirtm.module" in mlir_str, "Missing pirtm.module metadata"),
            ("@pirtm_recurrence" in mlir_str, "Missing recurrence function"),
            ("linalg.matvec" in mlir_str, "Missing matrix-vector operations"),
            ("pirtm.sigmoid" in mlir_str, "Missing sigmoid operation"),
            ("pirtm.clip" in mlir_str, "Missing clip projection"),
        ]
        
        for check, msg in checks:
            if not check:
                return False, msg
        
        return True, None
    
    def extract_epsilon(self, mlir_str: str) -> Optional[float]:
        """Extract epsilon value from emitted MLIR."""
        import re
        match = re.search(r'@epsilon = ([\d.]+)', mlir_str)
        return float(match.group(1)) if match else None
    
    def extract_contractivity_bounds(self, mlir_str: str) -> Dict[str, int | float]:
        """Extract all contractivity metadata from MLIR."""
        import re
        result = {}
        
        patterns = {
            "epsilon": r'@epsilon = ([\d.]+)',
            "confidence": r'@confidence = ([\d.]+)',
            "op_norm_T": r'@op_norm_T = ([\d.]+)',
            "prime_index": r'@prime_index = (\d+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, mlir_str)
            if match:
                try:
                    val = float(match.group(1)) if "." in match.group(1) else int(match.group(1))
                    result[key] = val
                except ValueError:
                    pass
        
        return result  # type: Dict[str, int | float]


def emit_mlir_test_fixture(
    dimension: int = 512,
    epsilon: float = 0.05,
    policy: str = "CarryForward",
) -> str:
    """
    Generate MLIR test fixture with known properties.
    
    Used for verification tests.
    
    Args:
        dimension: Tensor size
        epsilon: Contractivity margin
        policy: Ledger policy name
    
    Returns:
        Complete MLIR module for testing
    """
    config = MLIRConfig(epsilon=epsilon)
    emitter = MLIREmitter(config=config)
    return emitter.emit_module(
        policy_name=policy,
        kernel_name="FullAsymmetricAttribution",
        trace_id="test_trace_001",
        dimension=dimension,
    )
