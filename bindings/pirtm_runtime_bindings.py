"""
Phase 4: PIRTM Runtime Library Interface (ctypes bindings)

Provides Python bindings to the C runtime library (libpirtm_runtime.so)
via ctypes. Handles state management, iteration, and witness validation.

Status: Phase 4 Implementation
Related: ADR-009-llvm-compilation.md, pirtm_runtime.h (C interface)
"""

import ctypes
from ctypes import POINTER, c_double, c_int, c_float, c_char_p, CDLL
import numpy as np
from typing import Optional
import os


# ============================================================================
# ctypes Declarations
# ============================================================================

def _load_libpirtm(lib_path: Optional[str] = None) -> CDLL:
    """
    Load the PIRTM runtime library.
    
    Args:
        lib_path: Path to libpirtm_runtime.so (default: search standard paths)
    
    Returns:
        CDLL instance
    
    Raises:
        OSError: If library not found
    """
    if lib_path:
        return CDLL(lib_path)
    
    # Try standard library search paths
    candidates = [
        "libpirtm_runtime.so",
        "libpirtm_runtime.dylib",  # macOS
        "pirtm_runtime.dll",        # Windows
        "/usr/local/lib/libpirtm_runtime.so",
        "/usr/lib/libpirtm_runtime.so",
        os.path.expanduser("~/.local/lib/libpirtm_runtime.so"),
    ]
    
    for candidate in candidates:
        try:
            return CDLL(candidate)
        except OSError:
            continue
    
    raise OSError(
        "libpirtm_runtime not found. "
        "Install via 'pip install pirtm[llvm]' or provide lib_path parameter."
    )


# ============================================================================
# PirtmState: Python Wrapper
# ============================================================================

class PirtmState:
    """
    Python wrapper for PIRTM runtime state.
    
    Encapsulates a C pirtm_state structure, providing methods for
    iteration, state access, and witness validation.
    """
    
    _libpirtm = None  # Lazy-loaded library
    
    def __init__(self, state_dim: int, epsilon: float,
                 gain_matrix: Optional[np.ndarray] = None,
                 lib_path: Optional[str] = None):
        """
        Initialize PIRTM runtime state.
        
        Args:
            state_dim: Dimension of state vector
            epsilon: Contractivity margin (0.0 to 1.0)
            gain_matrix: Optional (state_dim × state_dim) gain matrix
            lib_path: Path to libpirtm_runtime library
        
        Raises:
            ValueError: If epsilon out of range or gain_matrix wrong shape
            OSError: If library not found
        """
        if not (0.0 <= epsilon < 1.0):
            raise ValueError(f"epsilon must be in [0, 1), got {epsilon}")
        
        if state_dim <= 0:
            raise ValueError(f"state_dim must be > 0, got {state_dim}")
        
        # Load library if not already loaded
        if PirtmState._libpirtm is None:
            PirtmState._libpirtm = _load_libpirtm(lib_path)
            assert PirtmState._libpirtm is not None
            self._setup_ctypes()
        
        self._state_dim = state_dim
        self._epsilon = epsilon
        self._state_ptr = None
        
        # Convert gain matrix to C format
        if gain_matrix is not None:
            if gain_matrix.shape != (state_dim, state_dim):
                raise ValueError(
                    f"gain_matrix must be ({state_dim}, {state_dim}), "
                    f"got {gain_matrix.shape}"
                )
            gain_ptr = gain_matrix.ctypes.data_as(POINTER(c_double))
            gain_rows = state_dim
            gain_cols = state_dim
        else:
            gain_ptr = None
            gain_rows = 0
            gain_cols = 0
        
        # Call pirtm_state_new
        state_ptr = ctypes.c_void_p()
        ret = PirtmState._libpirtm.pirtm_state_new(
            state_dim,
            c_float(epsilon),
            gain_ptr,
            gain_rows,
            gain_cols,
            ctypes.byref(state_ptr)
        )
        
        if ret != 0:
            raise RuntimeError(
                f"pirtm_state_new failed with code {ret}"
            )
        
        self._state_ptr = state_ptr
    
    @classmethod
    def _setup_ctypes(cls):
        """Setup ctypes function signatures."""
        lib = cls._libpirtm
        assert lib is not None  # Type guard for Pylance
        
        # pirtm_state_new
        lib.pirtm_state_new.argtypes = [
            c_int,                      # state_dim
            c_float,                    # epsilon
            POINTER(c_double),          # gain_matrix_ptr
            c_int, c_int,               # gain_rows, gain_cols
            POINTER(ctypes.c_void_p)    # out_state
        ]
        lib.pirtm_state_new.restype = c_int
        
        # pirtm_step
        lib.pirtm_step.argtypes = [ctypes.c_void_p]  # state
        lib.pirtm_step.restype = c_double              # returns norm
        
        # pirtm_run
        lib.pirtm_run.argtypes = [ctypes.c_void_p, c_int]  # state, num_steps
        lib.pirtm_run.restype = c_int                       # returns status
        
        # pirtm_get_state
        lib.pirtm_get_state.argtypes = [
            ctypes.c_void_p,           # state
            POINTER(c_double),         # out_buffer
            ctypes.c_size_t            # buffer_size
        ]
        lib.pirtm_get_state.restype = None
        
        # pirtm_set_state
        lib.pirtm_set_state.argtypes = [
            ctypes.c_void_p,           # state
            POINTER(c_double),         # buffer
            ctypes.c_size_t            # buffer_size
        ]
        lib.pirtm_set_state.restype = None
        
        # pirtm_get_dimension
        lib.pirtm_get_dimension.argtypes = [ctypes.c_void_p]
        lib.pirtm_get_dimension.restype = c_int
        
        # pirtm_verify_witness (optional)
        if hasattr(lib, 'pirtm_verify_witness'):
            lib.pirtm_verify_witness.argtypes = [
                ctypes.c_void_p,       # state
                c_char_p                # expected_hash
            ]
            lib.pirtm_verify_witness.restype = c_int
        
        # pirtm_state_free
        lib.pirtm_state_free.argtypes = [ctypes.c_void_p]
        lib.pirtm_state_free.restype = None
    
    def step(self) -> float:
        """
        Execute one iteration: X_{t+1} = T(Λ, X_t)
        
        Returns:
            Norm of state vector (||X_{t+1}||)
        """
        if self._state_ptr is None:
            raise RuntimeError("State has been freed")
        
        norm = PirtmState._libpirtm.pirtm_step(self._state_ptr)
        return float(norm)
    
    def run(self, num_steps: int) -> int:
        """
        Execute N iterations.
        
        Args:
            num_steps: Number of iterations to run
        
        Returns:
            0 if success, non-zero error code otherwise
        """
        if self._state_ptr is None:
            raise RuntimeError("State has been freed")
        
        if num_steps <= 0:
            raise ValueError(f"num_steps must be > 0, got {num_steps}")
        
        ret = PirtmState._libpirtm.pirtm_run(self._state_ptr, num_steps)
        return ret
    
    @property
    def state_vector(self) -> np.ndarray:
        """
        Get current state vector.
        
        Returns:
            Copy of state as (n,) numpy array of float64
        """
        if self._state_ptr is None:
            raise RuntimeError("State has been freed")
        
        buf = np.zeros(self._state_dim, dtype=np.float64)
        PirtmState._libpirtm.pirtm_get_state(
            self._state_ptr,
            buf.ctypes.data_as(POINTER(c_double)),
            buf.nbytes
        )
        return buf
    
    @state_vector.setter
    def state_vector(self, vec: np.ndarray):
        """
        Set state vector.
        
        Args:
            vec: (n,) array of float64
        """
        if self._state_ptr is None:
            raise RuntimeError("State has been freed")
        
        if vec.shape != (self._state_dim,):
            raise ValueError(
                f"vec must have shape ({self._state_dim},), got {vec.shape}"
            )
        
        vec = np.ascontiguousarray(vec, dtype=np.float64)
        PirtmState._libpirtm.pirtm_set_state(
            self._state_ptr,
            vec.ctypes.data_as(POINTER(c_double)),
            vec.nbytes
        )
    
    @property
    def dimension(self) -> int:
        """Get state dimension."""
        if self._state_ptr is None:
            raise RuntimeError("State has been freed")
        
        return PirtmState._libpirtm.pirtm_get_dimension(self._state_ptr)
    
    @property
    def epsilon(self) -> float:
        """Get contractivity margin."""
        return self._epsilon
    
    @property
    def norm(self) -> float:
        """Get Euclidean norm of state vector."""
        return float(np.linalg.norm(self.state_vector))
    
    def cleanup(self):
        """Explicitly cleanup state (also called by __del__)."""
        if self._state_ptr is not None and PirtmState._libpirtm is not None:
            try:
                PirtmState._libpirtm.pirtm_state_free(self._state_ptr)
            except Exception:
                pass  # Ignore errors during cleanup
            self._state_ptr = None
    
    def verify_witness(self, expected_hash: str) -> bool:
        """
        Verify ACE witness commitment.
        
        Args:
            expected_hash: Hex-encoded SHA256 hash
        
        Returns:
            True if witness is valid, False otherwise
        """
        if self._state_ptr is None:
            raise RuntimeError("State has been freed")
        
        if not hasattr(PirtmState._libpirtm, 'pirtm_verify_witness'):
            raise NotImplementedError(
                "Witness verification not available in this build"
            )
        
        ret = PirtmState._libpirtm.pirtm_verify_witness(
            self._state_ptr,
            expected_hash.encode('utf-8')
        )
        return ret == 1
    
    def __del__(self):
        """Cleanup: free state if not already freed."""
        if self._state_ptr is not None and PirtmState._libpirtm is not None:
            try:
                PirtmState._libpirtm.pirtm_state_free(self._state_ptr)
            except:
                pass  # Ignore errors during cleanup
            self._state_ptr = None
    
    def __repr__(self) -> str:
        return (
            f"PirtmState(dim={self._state_dim}, epsilon={self._epsilon:.4f}, "
            f"state_ptr={self._state_ptr})"
        )


# ============================================================================
# Utility Functions
# ============================================================================

def check_runtime_available(lib_path: Optional[str] = None) -> bool:
    """
    Check if PIRTM runtime library is available.
    
    Returns:
        True if library can be loaded, False otherwise
    """
    try:
        _load_libpirtm(lib_path)
        return True
    except OSError:
        return False
