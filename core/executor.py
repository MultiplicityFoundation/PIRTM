"""
Phase 4: Multi-Backend Executor

Unified interface for executing PIRTM recurrence loops on various backends:
- NumPy (Phase 1)
- LLVM compiled (Phase 4)
- Future: GPU, specialized hardware

Status: Phase 4 Implementation
Related: ADR-009-llvm-compilation.md
"""

from typing import Dict, Optional, List, Any, Union
import time
import numpy as np
from enum import Enum

from pirtm.bindings.pirtm_runtime_bindings import PirtmState, check_runtime_available


class Backend(Enum):
    """Available execution backends."""
    NUMPY = "numpy"
    LLVM = "llvm"
    AUTO = "auto"


class PirtmExecutor:
    """
    Unified executor for PIRTM recurrence loops.
    
    Supports multiple backends with automatic fallback:
    - LLVM: Native compiled code (fast, requires build)
    - NumPy: Pure Python (slower, always available)
    - Auto: Try LLVM first, fallback to NumPy
    """
    
    def __init__(self, backend: Union[Backend, str] = Backend.AUTO):
        """
        Initialize executor.
        
        Args:
            backend: Backend to use (NUMPY, LLVM, or AUTO)
        
        Raises:
            ValueError: If backend not recognized
        """
        if isinstance(backend, str):
            backend = Backend(backend)
        
        if backend == Backend.AUTO:
            # Try LLVM first, fallback to NumPy
            self._backend = self._select_best_backend()
        elif backend in (Backend.NUMPY, Backend.LLVM):
            self._backend = backend
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        self._backend_name = self._backend.value
    
    @staticmethod
    def _select_best_backend() -> Backend:
        """Select fastest available backend."""
        if check_runtime_available():
            return Backend.LLVM
        else:
            return Backend.NUMPY
    
    @property
    def backend_name(self) -> str:
        """Name of current backend."""
        return self._backend_name
    
    @property
    def supports_witness_validation(self) -> bool:
        """Whether backend can validate ACE witnesses."""
        return self._backend == Backend.LLVM
    
    def run(self,
            descriptor: Dict[str, Any],
            policy: Any,  # CarryForwardPolicy (not yet imported)
            kernel: Any,  # FullAsymmetricAttributionKernel (not yet imported)
            steps: int = 100,
            validate_witness: bool = False,
            initial_state: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Execute recurrence loop.
        
        Args:
            descriptor: Computation descriptor (contains epsilon, etc.)
            policy: Carry-forward policy
            kernel: Attribution kernel
            steps: Number of iterations
            validate_witness: Validate ACE witness if available (LLVM only)
            initial_state: Initial state vector (default: random)
        
        Returns:
            {
                'state': final_state_vector,
                'trajectory': List[np.ndarray] if return_trajectory=True,
                'final_norm': float,
                'backend': str,
                'witness_valid': bool or None,
                'execution_time': float,
                'steps_completed': int,
            }
        """
        
        start_time = time.time()
        
        try:
            if self._backend == Backend.NUMPY:
                result = self._run_numpy(
                    descriptor, policy, kernel, steps, initial_state
                )
            elif self._backend == Backend.LLVM:
                result = self._run_llvm(
                    descriptor, policy, kernel, steps, validate_witness,
                    initial_state
                )
            else:
                raise ValueError(f"Unknown backend: {self._backend}")
        
        except Exception as e:
            # Log error and fallback to NumPy if requested
            if self._backend == Backend.LLVM:
                import warnings
                warnings.warn(
                    f"LLVM backend failed ({e}), falling back to NumPy"
                )
                return self._run_numpy(
                    descriptor, policy, kernel, steps, initial_state
                )
            else:
                raise
        
        # Add execution metadata
        result['backend'] = self._backend_name
        result['execution_time'] = time.time() - start_time
        
        return result
    
    def _run_numpy(self,
                   descriptor: Dict[str, Any],
                   policy: Any,  # CarryForwardPolicy (not yet imported)
                   kernel: Any,  # FullAsymmetricAttributionKernel (not yet imported)
                   steps: int,
                   initial_state: Optional[np.ndarray]) -> Dict[str, Any]:
        """
        Execute via NumPy backend (Phase 1).
        
        Returns dict with execution results.
        """
        # Extract state dimension from descriptor or kernel
        state_dim = descriptor.get('state_dim') or kernel.n_features
        
        # Initialize state
        if initial_state is None:
            X_t = np.random.randn(state_dim) * 0.5  # Random in [-1, 1]
        else:
            X_t = np.array(initial_state, dtype=np.float64)
        
        # Get gain matrix from policy
        Lambda_t = policy.compute_gain_matrix(kernel)

        # Identity operator for Xi_t
        Xi_t = np.eye(state_dim)

        # Run recurrence using pirtm.core.recurrence.step
        from .recurrence import step as recurrence_step
        trajectory = [X_t.copy()]
        for _ in range(steps):
            X_t, _ = recurrence_step(X_t, Xi_t, Lambda_t)
            trajectory.append(X_t.copy())
        
        return {
            'state': X_t,
            'trajectory': trajectory,
            'final_norm': float(np.linalg.norm(X_t)),
            'steps_completed': steps,
            'witness_valid': None,
        }
    
    def _run_llvm(self,
                  descriptor: Dict[str, Any],
                  policy: Any,  # CarryForwardPolicy (not yet imported)
                  kernel: Any,  # FullAsymmetricAttributionKernel (not yet imported)
                  steps: int,
                  validate_witness: bool = False,
                  initial_state: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """
        Execute via LLVM compiled backend (Phase 4).
        
        Returns dict with execution results.
        """
        # Extract parameters
        state_dim = descriptor.get('state_dim') or kernel.n_features
        epsilon = descriptor.get('epsilon', 0.05)
        
        # Get gain matrix
        gain_matrix = policy.compute_gain_matrix(kernel)
        
        # Initialize state
        if initial_state is None:
            X_t = np.random.randn(state_dim) * 0.5
        else:
            X_t = np.array(initial_state, dtype=np.float64)
        
        # Create PIRTM runtime state
        pirtm_state = PirtmState(
            state_dim=state_dim,
            epsilon=epsilon,
            gain_matrix=gain_matrix
        )
        
        # Set initial state
        pirtm_state.state_vector = X_t
        
        # Run iterations
        ret = pirtm_state.run(steps)
        if ret != 0:
            raise RuntimeError(f"pirtm_run failed with code {ret}")
        
        # Get final state
        X_final = pirtm_state.state_vector
        final_norm = np.linalg.norm(X_final)
        
        # Validate witness if requested
        witness_valid = None
        if validate_witness:
            witness_hash = descriptor.get('witness_hash')
            if witness_hash:
                try:
                    witness_valid = pirtm_state.verify_witness(witness_hash)
                except NotImplementedError:
                    witness_valid = None
        
        return {
            'state': X_final,
            'trajectory': None,  # Not tracked in LLVM backend for performance
            'final_norm': float(final_norm),
            'steps_completed': steps,
            'witness_valid': witness_valid,
        }
    
    @staticmethod
    def available_backends() -> List[str]:
        """List of available backends on this system."""
        backends = ["numpy"]
        if check_runtime_available():
            backends.append("llvm")
        return backends
    
    @staticmethod
    def benchmark(descriptor: Dict[str, Any],
                  policy: Any,  # CarryForwardPolicy (not yet imported)
                  kernel: Any,  # FullAsymmetricAttributionKernel (not yet imported)
                  steps: int = 100) -> Dict[str, float]:
        """
        Benchmark all available backends.
        
        Returns:
            {backend_name: execution_time_seconds}
        """
        results: Dict[str, float] = {}
        
        # Benchmark NumPy
        executor = PirtmExecutor(Backend.NUMPY)
        start = time.time()
        executor.run(descriptor, policy, kernel, steps)
        results['numpy'] = time.time() - start
        
        # Benchmark LLVM (if available)
        if check_runtime_available():
            executor = PirtmExecutor(Backend.LLVM)
            start = time.time()
            executor.run(descriptor, policy, kernel, steps)
            results['llvm'] = time.time() - start
        
        return results


class ExecutionResult:
    """Represents a single execution result."""
    
    def __init__(self, result_dict: Dict[str, Any]):
        """
        Wrap execution result.
        
        Args:
            result_dict: Output from PirtmExecutor.run()
        """
        self._data = result_dict
    
    @property
    def state(self) -> np.ndarray:
        """Final state vector."""
        return self._data['state']
    
    @property
    def trajectory(self) -> Optional[List[np.ndarray]]:
        """Full trajectory (if tracked)."""
        return self._data.get('trajectory')
    
    @property
    def final_norm(self) -> float:
        """Norm of final state."""
        return self._data['final_norm']
    
    @property
    def backend(self) -> str:
        """Backend used."""
        return self._data['backend']
    
    @property
    def execution_time(self) -> float:
        """Execution time in seconds."""
        return self._data['execution_time']
    
    @property
    def steps_completed(self) -> int:
        """Number of steps executed."""
        return self._data['steps_completed']
    
    @property
    def witness_valid(self) -> Optional[bool]:
        """Witness validation result (if performed)."""
        return self._data.get('witness_valid')
    
    @property
    def throughput(self) -> float:
        """Operations per second (steps/sec)."""
        if self.execution_time <= 0:
            return float('inf')
        return self.steps_completed / self.execution_time
    
    def __repr__(self) -> str:
        return (
            f"ExecutionResult(backend={self.backend}, "
            f"steps={self.steps_completed}, "
            f"time={self.execution_time:.4f}s, "
            f"throughput={self.throughput:.1f} steps/s)"
        )
