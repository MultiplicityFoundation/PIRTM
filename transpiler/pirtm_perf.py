"""
PIRTM Performance Optimization & Profiling (Day 30+ gate).

Targets:
  - Establish baseline measurements (NumPy vs power iteration)
  - Optimize spectral radius computation
  - Cache repeated computations
  - Day 90 gate: pirtm.step ≥10× NumPy on 512-dim tensor

Reference: ADR-008 Day 30+ optimization phase
"""

import time
import numpy as np
from typing import List, Dict, Tuple, Optional
from functools import lru_cache


class SpectralRadiusProfiler:
    """Benchmark spectral radius computation methods."""
    
    def __init__(self, enable_numpy=True):
        self.enable_numpy = enable_numpy
        self.timings = {}  # Track performance metrics
    
    def benchmark_numpy(self, matrix: List[List[float]], iterations: int = 5) -> Tuple[float, float, float]:
        """
        Benchmark NumPy eigenvalue computation.
        
        Returns: (avg_time_ms, spectral_radius, min_time)
        """
        times = []
        spectral_radii = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            A = np.array(matrix, dtype=np.float64)
            eigenvalues = np.linalg.eigvals(A)
            spectral_radius = float(np.max(np.abs(eigenvalues)))
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)  # Convert to ms
            spectral_radii.append(spectral_radius)
        
        avg_time = sum(times) / len(times)
        self.timings['numpy'] = {
            'avg_ms': avg_time,
            'min_ms': min(times),
            'max_ms': max(times),
            'spectral_radius': spectral_radii[0]
        }
        return avg_time, spectral_radii[0], min(times)
    
    def benchmark_sparse(self, matrix: List[List[float]], sparsity_threshold: float = 0.1, 
                         iterations: int = 5) -> Tuple[float, float, float]:
        """
        Benchmark sparse matrix eigenvalue computation (scipy).
        
        Only uses sparse solver if matrix sparsity > sparsity_threshold.
        Returns: (avg_time_ms, spectral_radius, min_time)
        """
        try:
            from scipy import sparse
            from scipy.sparse import linalg as spla
        except ImportError:
            return None, None, None
        
        # Check sparsity: count non-zero elements
        total_elements = len(matrix) ** 2
        nonzero_count = sum(1 for row in matrix for val in row if abs(val) > 1e-15)
        sparsity = 1.0 - (nonzero_count / total_elements)
        
        if sparsity < sparsity_threshold:
            return None, None, None  # Not sparse enough
        
        times = []
        spectral_radii = []
        
        for _ in range(iterations):
            start = time.perf_counter()
            # Convert to scipy sparse format
            A = np.array(matrix, dtype=np.float64)
            A_sparse = sparse.csr_matrix(A)
            
            # Use sparse eigenvalue solver (ARPACK)
            try:
                eigenvalues = spla.eigsh(A_sparse, k=1, which='LM', return_eigenvectors=False)
                spectral_radius = float(np.abs(eigenvalues[0]))
            except:
                # If sparse solver fails, fall back to dense
                eigenvalues = np.linalg.eigvals(A)
                spectral_radius = float(np.max(np.abs(eigenvalues)))
            
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)
            spectral_radii.append(spectral_radius)
        
        avg_time = sum(times) / len(times)
        self.timings['sparse'] = {
            'avg_ms': avg_time,
            'min_ms': min(times),
            'sparsity': sparsity,
            'spectral_radius': spectral_radii[0]
        }
        return avg_time, spectral_radii[0], min(times)
    
    def benchmark_power_iteration(self, matrix: List[List[float]], iterations: int = 100,
                                  bench_iters: int = 5) -> Tuple[float, float, float]:
        """
        Benchmark power iteration spectral radius.
        
        Returns: (avg_time_ms, spectral_radius, min_time)
        """
        times = []
        spectral_radii = []
        
        for _ in range(bench_iters):
            start = time.perf_counter()
            spectral_radius = self._power_iteration(matrix, iterations)
            elapsed = time.perf_counter() - start
            times.append(elapsed * 1000)
            spectral_radii.append(spectral_radius)
        
        avg_time = sum(times) / len(times)
        self.timings['power_iteration'] = {
            'avg_ms': avg_time,
            'min_ms': min(times),
            'iterations': iterations,
            'spectral_radius': spectral_radii[0]
        }
        return avg_time, spectral_radii[0], min(times)
    
    def _power_iteration(self, matrix: List[List[float]], iterations: int = 100) -> float:
        """Pure power iteration (no NumPy)."""
        n = len(matrix)
        if n == 0:
            return 0.0
        
        v = [1.0] * n
        for _ in range(iterations):
            v_new = [0.0] * n
            for i in range(n):
                for j in range(n):
                    v_new[i] += matrix[i][j] * v[j]
            
            norm = (sum(x**2 for x in v_new) ** 0.5)
            if norm < 1e-10:
                return 0.0
            
            v = [x / norm for x in v_new]
        
        Av = [0.0] * n
        for i in range(n):
            for j in range(n):
                Av[i] += matrix[i][j] * v[j]
        
        v_dot_Av = sum(v[i] * Av[i] for i in range(n))
        v_dot_v = sum(v[i] * v[i] for i in range(n))
        
        return float(v_dot_Av / v_dot_v) if v_dot_v > 1e-15 else 0.0
    
    def print_report(self):
        """Print benchmarking report."""
        print("\n" + "=" * 70)
        print("SPECTRAL RADIUS COMPUTATION BENCHMARK")
        print("=" * 70)
        
        for method, data in self.timings.items():
            print(f"\n{method.upper()}:")
            print(f"  Avg time:        {data['avg_ms']:.4f} ms")
            print(f"  Min time:        {data['min_ms']:.4f} ms")
            if 'spectral_radius' in data:
                print(f"  Spectral radius: {data['spectral_radius']:.6f}")
            if 'iterations' in data:
                print(f"  Iterations:      {data['iterations']}")
            if 'sparsity' in data:
                print(f"  Sparsity:        {data['sparsity']:.2%}")
        
        # Compute speedup factors
        if 'numpy' in self.timings and 'power_iteration' in self.timings:
            numpy_time = self.timings['numpy']['avg_ms']
            pi_time = self.timings['power_iteration']['avg_ms']
            print(f"\nPower Iteration vs NumPy: {pi_time / numpy_time:.2f}× slower")
        
        if 'numpy' in self.timings and 'sparse' in self.timings:
            numpy_time = self.timings['numpy']['avg_ms']
            sparse_time = self.timings['sparse']['avg_ms']
            speedup = numpy_time / sparse_time
            print(f"Sparse vs NumPy: {speedup:.2f}× {'faster' if speedup > 1 else 'slower'}")
        
        print("=" * 70 + "\n")


class OptimizedSpectralRadius:
    """Optimized spectral radius computation with caching and sparse support."""
    
    def __init__(self, use_cache=True, sparse_threshold=0.05):
        self.use_cache = use_cache
        self.sparse_threshold = sparse_threshold  # Default: try sparse for anything ≥5% sparsity
        self._cache = {}
    
    def compute(self, matrix: List[List[float]]) -> float:
        """
        Compute spectral radius with automatic optimization.
        
        Selection strategy:
          1. If sparse (density < sparse_threshold): use scipy sparse solver
          2. Otherwise: use NumPy dense eigenvalue
          3. Fallback: power iteration (no NumPy)
        """
        # Convert to tuple for hashing (cache key)
        if self.use_cache:
            matrix_key = self._matrix_to_key(matrix)
            if matrix_key in self._cache:
                return self._cache[matrix_key]
        
        # Check if matrix is sparse
        spectral_radius = self._compute_optimized(matrix)
        
        if self.use_cache:
            self._cache[matrix_key] = spectral_radius
        
        return spectral_radius
    
    def _matrix_to_key(self, matrix: List[List[float]]) -> tuple:
        """Convert matrix to hashable key."""
        return tuple(tuple(round(x, 8) for x in row) for row in matrix)
    
    def _compute_optimized(self, matrix: List[List[float]]) -> float:
        """Internal optimized computation."""
        # Check sparsity
        total_elements = len(matrix) ** 2
        if total_elements == 0:
            return 0.0
        
        nonzero_count = sum(1 for row in matrix for val in row if abs(val) > 1e-15)
        sparsity = 1.0 - (nonzero_count / total_elements)
        
        # Try sparse solver if sparse
        if sparsity > self.sparse_threshold:
            result = self._try_scipy_sparse(matrix)
            if result is not None:
                return result
        
        # Fall back to NumPy dense
        try:
            import numpy as np
            A = np.array(matrix, dtype=np.float64)
            eigenvalues = np.linalg.eigvals(A)
            return float(np.max(np.abs(eigenvalues)))
        except ImportError:
            # No NumPy: use power iteration
            return self._power_iteration(matrix)
    
    def _try_scipy_sparse(self, matrix: List[List[float]]) -> Optional[float]:
        """Try scipy sparse solver; return None if unavailable."""
        try:
            from scipy import sparse
            from scipy.sparse import linalg as spla
            import numpy as np
            
            A = np.array(matrix, dtype=np.float64)
            A_sparse = sparse.csr_matrix(A)
            
            # Compute largest eigenvalue
            eigenvalues = spla.eigsh(A_sparse, k=1, which='LM', return_eigenvectors=False)
            return float(np.abs(eigenvalues[0]))
        except:
            return None
    
    def _power_iteration(self, matrix: List[List[float]], iterations: int = 150) -> float:
        """Power iteration fallback."""
        n = len(matrix)
        if n == 0:
            return 0.0
        
        v = [1.0] * n
        for _ in range(iterations):
            v_new = [0.0] * n
            for i in range(n):
                for j in range(n):
                    v_new[i] += matrix[i][j] * v[j]
            
            norm = (sum(x**2 for x in v_new) ** 0.5)
            if norm < 1e-10:
                return 0.0
            
            v = [x / norm for x in v_new]
        
        Av = [0.0] * n
        for i in range(n):
            for j in range(n):
                Av[i] += matrix[i][j] * v[j]
        
        v_dot_Av = sum(v[i] * Av[i] for i in range(n))
        v_dot_v = sum(v[i] * v[i] for i in range(n))
        
        return float(v_dot_Av / v_dot_v) if v_dot_v > 1e-15 else 0.0
    
    def clear_cache(self):
        """Clear the computation cache."""
        self._cache.clear()
    
    def cache_stats(self) -> Dict:
        """Return cache statistics."""
        return {
            'cached_matrices': len(self._cache),
            'cache_enabled': self.use_cache
        }
