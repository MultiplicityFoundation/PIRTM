"""
Backward compatibility shim for prime → mod nomenclature transition (Day 0–14).

During migration (Day 0–14):
  - Old code uses: channel.prime, module.prime_index
  - Shim maps to: channel.mod, module.prime_index (stored as property)
  - Verifier sees: mod= in the MLIR dialect

After Day 14:
  - All code uses: mod, prime_index (unchanged field names)
  - This shim layer is removed

Spec Reference:
  - PIRTM ADR-004: Type system
  - PIRTM ADR-007: Migration strategy
  - L0 invariant #1: pirtm.module carries exactly one prime_index, epsilon, op_norm_T
"""


class PrimeChannelShim:
    """Wraps a channel to provide both .prime and .mod for compatibility.
    
    During migration, this allows old code (using .prime) and new code (using .mod)
    to coexist. Both properties return the same internal _mod value. After Day 14,
    this shim is removed and all code uses .mod directly.
    
    Properties:
      - .prime (deprecated): Read-only access to modulus value
      - .mod (canonical): Read-only access to modulus value
      - .as_mlir(): Returns MLIR-formatted string
    """
    
    def __init__(self, mod_value: int):
        """Initialize with a modulus value.
        
        Args:
            mod_value: Prime or squarefree composite modulus
        """
        if not isinstance(mod_value, int):
            raise TypeError(f"mod_value must be int, got {type(mod_value)}")
        if mod_value < 2:
            raise ValueError(f"mod_value must be >= 2, got {mod_value}")
        
        self._mod = mod_value
    
    @property
    def prime(self) -> int:
        """Deprecated: Use .mod instead. Returns the modulus value."""
        return self._mod
    
    @property
    def mod(self) -> int:
        """Canonical MLIR-friendly modulus value."""
        return self._mod
    
    def as_mlir(self) -> str:
        """Return MLIR attribute representation."""
        return f"mod={self._mod}"
    
    def __repr__(self) -> str:
        return f"PrimeChannelShim(mod={self._mod})"
    
    def __str__(self) -> str:
        return self.as_mlir()
    
    def __eq__(self, other) -> bool:
        if isinstance(other, PrimeChannelShim):
            return self._mod == other._mod
        if isinstance(other, int):
            return self._mod == other
        return False
    
    def __hash__(self) -> int:
        return hash(self._mod)


class SessionGraphShim:
    """Wraps SessionGraph to map old prime_index field to modern .mod context.
    
    L0 invariant #1: pirtm.module carries exactly one prime_index, one epsilon,
    one op_norm_T. This shim enforces that invariant during migration.
    
    Properties:
      - .prime_index (canonical): The modulus prime or squarefree composite
      - .mod (alias): Read-only alias for prime_index (used in MLIR emission)
      - .epsilon: Convergence bound (read-only)
      - .op_norm_T: Operator norm bound (read-only)
      - .coupling: Link-time coupling matrix (set once via set_coupling())
    """
    
    def __init__(self, prime_index: int, epsilon: float, op_norm_T: float):
        """Initialize with the three required fields (L0 invariant #1).
        
        Args:
            prime_index: Modulus (prime or squarefree composite)
            epsilon: Convergence bound (ε in PIRTM spec)
            op_norm_T: Operator norm bound (‖T‖ in PIRTM spec)
        """
        if not isinstance(prime_index, int):
            raise TypeError(f"prime_index must be int, got {type(prime_index)}")
        if prime_index < 2:
            raise ValueError(f"prime_index must be >= 2, got {prime_index}")
        
        if not isinstance(epsilon, (int, float)):
            raise TypeError(f"epsilon must be numeric, got {type(epsilon)}")
        if epsilon <= 0:
            raise ValueError(f"epsilon must be > 0, got {epsilon}")
        
        if not isinstance(op_norm_T, (int, float)):
            raise TypeError(f"op_norm_T must be numeric, got {type(op_norm_T)}")
        if op_norm_T < 0:
            raise ValueError(f"op_norm_T must be >= 0, got {op_norm_T}")
        
        self.prime_index = prime_index  # Canonical name (L0 invariant #1)
        self.epsilon = epsilon
        self.op_norm_T = op_norm_T
        self._coupling = None
    
    @property
    def mod(self) -> int:
        """Alias for prime_index (used in MLIR emission context).
        
        After Day 14, this alias is removed and code uses prime_index directly.
        """
        return self.prime_index
    
    def set_coupling(self, coupling_matrix):
        """Assign link-time coupling matrix (L0 invariant #4).
        
        This method enforces that coupling is set exactly once. After Day 14,
        coupling assignment is handled by the linker module directly.
        
        Args:
            coupling_matrix: 2D array or list of coupling values
            
        Raises:
            RuntimeError: If coupling is already set
        """
        if self._coupling is not None:
            raise RuntimeError(
                f"Coupling already resolved for prime_index={self.prime_index}; "
                "cannot set twice (L0 invariant #4)"
            )
        self._coupling = coupling_matrix
    
    @property
    def coupling(self):
        """Get the resolved coupling matrix (set by linker)."""
        return self._coupling
    
    def __repr__(self) -> str:
        coupling_str = (
            f", coupling={self._coupling}" if self._coupling is not None else ""
        )
        return (
            f"SessionGraphShim(prime_index={self.prime_index}, "
            f"ε={self.epsilon}, ‖T‖={self.op_norm_T}{coupling_str})"
        )
    
    def __str__(self) -> str:
        return self.__repr__()


# Type aliases for easier migration
Channel = PrimeChannelShim
SessionGraph = SessionGraphShim
