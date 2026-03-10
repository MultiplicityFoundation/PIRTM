"""
NumPy Backend Implementation for PIRTM

Reference implementation of the TensorBackend protocol using NumPy.
This is the default backend and remains compatible with all existing code.

Reference: ADR-006 (Backend Abstraction), ADR-004 (Contractivity Semantics)
"""

from typing import Tuple
import numpy as np
from . import Array, Scalar, TensorBackend


class NumPyBackend(TensorBackend):
    """
    NumPy-based implementation of TensorBackend protocol.
    
    This is the reference implementation and default backend.
    All PIRTM core functions work with NumPy arrays via this backend.
    
    Performance note: NumPy operations are limited by:
    - GIL (Global Interpreter Lock): No true parallelism
    - Dynamic dispatch: ~10-20% overhead vs compiled alternatives
    
    LLVM and MLIR backends will provide 5-10× speedup for recurrence loops.
    """
    
    def __init__(self):
        """Initialize NumPy backend."""
        self._name = "numpy"
    
    def name(self) -> str:
        """Return backend identifier."""
        return self._name
    
    # =========================================================================
    # Linear Algebra Operations
    # =========================================================================
    
    def matmul(self, A: Array, x: Array) -> Array:
        """Matrix-vector multiplication using NumPy."""
        return np.matmul(A, x)
    
    def gemm(self, A: Array, B: Array, alpha: Scalar = 1.0, beta: Scalar = 0.0) -> Array:
        """Matrix-matrix multiplication with scaling."""
        result = alpha * np.matmul(A, B)
        if beta != 0.0:
            result = result + beta
        return result
    
    def add(self, x: Array, y: Array) -> Array:
        """Element-wise addition."""
        return np.add(x, y)
    
    def multiply(self, x: Array, y: Array) -> Array:
        """Element-wise multiplication."""
        return np.multiply(x, y)
    
    def dot(self, x: Array, y: Array) -> Scalar:
        """Inner product."""
        return float(np.dot(x, y))
    
    def norm(self, x: Array, order: int = 2) -> Scalar:
        """Vector norm."""
        return float(np.linalg.norm(x, ord=order))
    
    # =========================================================================
    # Element-wise Operations
    # =========================================================================
    
    def clip(self, x: Array, min_val: Scalar, max_val: Scalar) -> Array:
        """Element-wise clipping."""
        return np.clip(x, min_val, max_val)
    
    def sigmoid(self, x: Array) -> Array:
        """Sigmoid activation function."""
        return 1.0 / (1.0 + np.exp(-x))
    
    def exp(self, x: Array) -> Array:
        """Element-wise exponential."""
        return np.exp(x)
    
    def log(self, x: Array) -> Array:
        """Element-wise natural logarithm."""
        return np.log(x)
    
    def sqrt(self, x: Array) -> Array:
        """Element-wise square root."""
        return np.sqrt(x)
    
    def tanh(self, x: Array) -> Array:
        """Hyperbolic tangent."""
        return np.tanh(x)
    
    # =========================================================================
    # Matrix Creation
    # =========================================================================
    
    def eye(self, n: int) -> Array:
        """Identity matrix."""
        return np.eye(n)
    
    def zeros(self, shape: Tuple[int, ...]) -> Array:
        """Array of zeros."""
        return np.zeros(shape)
    
    def ones(self, shape: Tuple[int, ...]) -> Array:
        """Array of ones."""
        return np.ones(shape)
    
    def diag(self, x: Array) -> Array:
        """Create diagonal matrix from 1D array."""
        return np.diag(x)
    
    def eye_like(self, x: Array) -> Array:
        """Identity matrix with same shape as x."""
        return np.eye(x.shape[0])
    
    # =========================================================================
    # Array Manipulation
    # =========================================================================
    
    def reshape(self, x: Array, newshape: Tuple[int, ...]) -> Array:
        """Reshape array."""
        return np.reshape(x, newshape)
    
    def transpose(self, x: Array) -> Array:
        """Transpose 2D array."""
        return np.transpose(x)
    
    def concatenate(self, arrays: list[Array], axis: int = 0) -> Array:
        """Concatenate arrays."""
        return np.concatenate(arrays, axis=axis)
    
    # =========================================================================
    # Backend Info
    # =========================================================================
    
    def device(self) -> str:
        """Return device location (NumPy always CPU)."""
        return "cpu"
    
    def dtype(self, x: Array) -> str:
        """Return data type of array."""
        if isinstance(x, np.ndarray):
            return str(x.dtype)  # type: ignore
        return "unknown"


# Register NumPy backend as default
_numpy_backend_instance = NumPyBackend()
