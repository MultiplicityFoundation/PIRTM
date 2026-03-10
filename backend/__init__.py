"""
PIRTM Backend Abstraction Protocol (Phase 1 Liberation)

Decouples PIRTM core logic from NumPy via a protocol-based abstraction.
Enables multiple tensor backends (NumPy, MLIR, LLVM, GPU) without touching
core algorithms.

Reference: ADR-006 (Backend Abstraction), ADR-004 (Contractivity Semantics)

See:
  - backend.py: TensorBackend protocol definition
  - numpy_backend.py: Reference NumPy implementation
  - registry.py: Backend registration and discovery
"""

from typing import Protocol, Any, Tuple, Union, Optional
import threading

# Type aliases
Array = Any  # Opaque tensor type; each backend defines this
Scalar = Union[float, int]


class TensorBackend(Protocol):
    """
    Specification for tensor computation backends.
    
    Any backend implementing this protocol can replace NumPy as PIRTM's
    underlying computation substrate. This enables:
    
    1. **Backend Lock-in Resolution**: Core logic doesn't depend on NumPy
    2. **MLIR/LLVM Compilation**: Compiled backends can provide 5-10× speedup
    3. **Verification Independence**: Contractivity validation can move to compile-time
    
    All methods in this protocol have deterministic semantics and preserve
    PIRTM's L0 contraction invariant (q_t < 1 - ε).
    
    See ADR-006 for full protocol rationale and ADR-004 for contractivity semantics.
    """
    
    def name(self) -> str:
        """Unique identifier for this backend (e.g., 'numpy', 'mlir', 'llvm')."""
        ...
    
    # =========================================================================
    # Core Linear Algebra Operations
    # =========================================================================
    
    def matmul(self, A: Array, x: Array) -> Array:
        """
        Matrix-vector multiplication: A @ x.
        
        Args:
            A: 2D array of shape (m, n)
            x: 1D array of shape (n,)
        
        Returns:
            1D array of shape (m,), result of A @ x
        
        Raises:
            ValueError: If shapes are incompatible
        """
        ...
    
    def gemm(self, A: Array, B: Array, alpha: Scalar = 1.0, beta: Scalar = 0.0) -> Array:
        """
        Matrix-matrix multiplication with scaling: alpha * A @ B + beta * result.
        
        Used for batch operations in spectral governance.
        """
        ...
    
    def add(self, x: Array, y: Array) -> Array:
        """Element-wise addition: x + y."""
        ...
    
    def multiply(self, x: Array, y: Array) -> Array:
        """Element-wise multiplication: x * y."""
        ...
    
    def dot(self, x: Array, y: Array) -> Scalar:
        """Inner product: x · y (result is scalar)."""
        ...
    
    def norm(self, x: Array, order: int = 2) -> Scalar:
        """
        Vector norm: ||x||_order.
        
        Args:
            x: 1D array
            order: Norm order (default 2 = Euclidean)
        
        Returns:
            Scalar norm value
            
        Note: For contractivity verification, order=2 (L2 norm) is canonical.
        """
        ...
    
    # =========================================================================
    # Element-wise Operations
    # =========================================================================
    
    def clip(self, x: Array, min_val: Scalar, max_val: Scalar) -> Array:
        """Element-wise clipping: clip(x, min_val, max_val)."""
        ...
    
    def sigmoid(self, x: Array) -> Array:
        """Sigmoid activation: 1 / (1 + exp(-x))."""
        ...
    
    def exp(self, x: Array) -> Array:
        """Element-wise exponential: e^x."""
        ...
    
    def log(self, x: Array) -> Array:
        """Element-wise natural logarithm: ln(x)."""
        ...
    
    def sqrt(self, x: Array) -> Array:
        """Element-wise square root: sqrt(x)."""
        ...
    
    def tanh(self, x: Array) -> Array:
        """Hyperbolic tangent: tanh(x)."""
        ...
    
    # =========================================================================
    # Matrix Creation
    # =========================================================================
    
    def eye(self, n: int) -> Array:
        """Identity matrix of shape (n, n)."""
        ...
    
    def zeros(self, shape: Tuple[int, ...]) -> Array:
        """Array of zeros with given shape."""
        ...
    
    def ones(self, shape: Tuple[int, ...]) -> Array:
        """Array of ones with given shape."""
        ...
    
    def diag(self, x: Array) -> Array:
        """Create diagonal matrix from 1D array."""
        ...
    
    def eye_like(self, x: Array) -> Array:
        """Identity matrix with same shape as x."""
        ...
    
    # =========================================================================
    # Array Manipulation
    # =========================================================================
    
    def reshape(self, x: Array, newshape: Tuple[int, ...]) -> Array:
        """Reshape array without copying data."""
        ...
    
    def transpose(self, x: Array) -> Array:
        """Transpose 2D array."""
        ...
    
    def concatenate(self, arrays: list[Array], axis: int = 0) -> Array:
        """Concatenate arrays along axis."""
        ...
    
    # =========================================================================
    # Backend Info
    # =========================================================================
    
    def device(self) -> str:
        """Device location (e.g., 'cpu', 'gpu:0', 'tpu')."""
        ...
    
    def dtype(self, x: Array) -> str:
        """Data type of array (e.g., 'float64', 'float32')."""
        ...


# Global backend registry and default
_backend_registry: dict[str, TensorBackend] = {}
_default_backend: Optional[TensorBackend] = None
_lock = threading.Lock()


def register_backend(name: str, backend: TensorBackend) -> None:
    """Register a backend implementation."""
    with _lock:
        _backend_registry[name] = backend


def get_backend(name: str = "numpy") -> TensorBackend:
    """
    Get a backend by name. If not registered, imports and returns it.
    
    Args:
        name: Backend name ('numpy', 'mlir', 'llvm', etc.)
    
    Returns:
        Backend instance implementing TensorBackend protocol
    
    Raises:
        ValueError: If backend not found or failed to initialize
    """
    with _lock:
        if name in _backend_registry:
            return _backend_registry[name]
        
        # Lazy import and initialize
        if name == "numpy":
            from . import numpy_backend
            backend = numpy_backend.NumPyBackend()
            _backend_registry[name] = backend
            return backend
        else:
            raise ValueError(f"Unknown backend: {name}")


def set_default_backend(name: str) -> None:
    """Set the default backend for PIRTM core operations."""
    global _default_backend
    with _lock:
        _default_backend = get_backend(name)


def current_backend() -> TensorBackend:
    """Get the currently active default backend."""
    global _default_backend
    if _default_backend is None:
        _default_backend = get_backend("numpy")
    return _default_backend


__all__ = [
    "Array",
    "Scalar",
    "TensorBackend",
    "register_backend",
    "get_backend",
    "set_default_backend",
    "current_backend",
]
