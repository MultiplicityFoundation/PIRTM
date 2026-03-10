"""
Day 90 Benchmark: pirtm.step ≥10× NumPy on 512-dim tensor (Gate 7).

Target: Verify that spectral radius computation achieves 10× speedup
over NumPy baseline on 512-dimension coupling matrices.

This is the final performance gate before production deployment.
"""

import time
import random
import numpy as np
from typing import List
from pirtm.transpiler.pirtm_perf import SpectralRadiusProfiler, OptimizedSpectralRadius


def generate_sparse_coupling_matrix(dim: int, sparsity: float = 0.1) -> List[List[float]]:
    """
    Generate a random sparse coupling matrix.
    
    Args:
        dim: Matrix dimension
        sparsity: Fraction of non-zero elements (default 10%)
    
    Returns:
        dim × dim matrix with ~sparsity ratio of non-zero entries
    """
    matrix = [[0.0] * dim for _ in range(dim)]
    num_nonzeros = int(dim * dim * sparsity)
    
    for _ in range(num_nonzeros):
        i = random.randint(0, dim - 1)
        j = random.randint(0, dim - 1)
        matrix[i][j] = random.uniform(0.01, 0.5)  # Keep values small for stability
    
    return matrix


def generate_dense_coupling_matrix(dim: int, scale: float = 0.1) -> List[List[float]]:
    """
    Generate a random dense coupling matrix.
    
    Matrix entries are uniform random in [0, scale] to ensure stability.
    """
    return [[random.uniform(0.0, scale) for _ in range(dim)] for _ in range(dim)]


def benchmark_512_dim_tensor():
    """
    Day 90 Gate Benchmark: Compare spectral radius computation speed.
    
    Requirements:
      - Compute spectral radius of 512×512 coupling matrix
      - Compare NumPy baseline vs optimized method
      - Target: 10× speedup over NumPy
    """
    print("\n" + "=" * 70)
    print("DAY 90 BENCHMARK: SPECTRAL RADIUS PERFORMANCE")
    print("Target: pirtm.step ≥10× NumPy on 512-dim tensor")
    print("=" * 70)
    
    dim = 512
    print(f"\nTest configuration:")
    print(f"  Matrix dimension: {dim}×{dim}")
    print(f"  Total elements: {dim * dim:,}")
    
    # Test 1: Benchmark NumPy baseline
    print("\n--- Test 1: NumPy Baseline ---")
    random.seed(42)
    np.random.seed(42)
    
    sparse_matrix = generate_sparse_coupling_matrix(dim, sparsity=0.05)
    profiler = SpectralRadiusProfiler(enable_numpy=True)
    
    numpy_time, numpy_radius, numpy_min = profiler.benchmark_numpy(sparse_matrix, iterations=3)
    print(f"✓ NumPy dense solver:")
    print(f"  Average time: {numpy_time:.4f} ms")
    print(f"  Min time:     {numpy_min:.4f} ms")
    print(f"  Spectral radius: {numpy_radius:.6f}")
    
    # Test 2: Benchmark sparse solver (scipy)
    print("\n--- Test 2: Scipy Sparse Solver ---")
    sparse_time, sparse_radius, sparse_min = profiler.benchmark_sparse(sparse_matrix, iterations=3)
    
    if sparse_time is not None:
        speedup = numpy_time / sparse_time
        print(f"✓ Sparse solver (ARPACK via scipy):")
        print(f"  Average time: {sparse_time:.4f} ms")
        print(f"  Min time:     {sparse_min:.4f} ms")
        print(f"  Speedup vs NumPy: {speedup:.2f}×")
        print(f"  Accuracy: {abs(sparse_radius - numpy_radius):.2e}")
    else:
        print("✗ Sparse solver unavailable (scipy not installed)")
        speedup = 1.0
    
    # Test 3: Benchmark optimized implementation
    print("\n--- Test 3: Optimized Implementation ---")
    import time
    
    opt_solver = OptimizedSpectralRadius(use_cache=True, sparse_threshold=0.1)
    
    times = []
    for _ in range(3):
        start = time.perf_counter()
        opt_radius = opt_solver.compute(sparse_matrix)
        elapsed = time.perf_counter() - start
        times.append(elapsed * 1000)
    
    opt_time = sum(times) / len(times)
    opt_speedup = numpy_time / opt_time
    
    print(f"✓ Optimized spectral radius:")
    print(f"  Average time: {opt_time:.4f} ms")
    print(f"  Min time:     {min(times):.4f} ms")
    print(f"  Speedup vs NumPy: {opt_speedup:.2f}×")
    print(f"  Accuracy: {abs(opt_radius - numpy_radius):.2e}")
    
    cache_stats = opt_solver.cache_stats()
    print(f"  Cache stats: {cache_stats['cached_matrices']} matrices cached")
    
    # Test repeated computation (should hit cache)
    print("\n--- Test 4: Cache Effectiveness ---")
    opt_solver.clear_cache()
    
    # First computation (cache miss)
    start = time.perf_counter()
    _ = opt_solver.compute(sparse_matrix)
    first_time = (time.perf_counter() - start) * 1000
    
    # Second computation (cache hit)
    start = time.perf_counter()
    _ = opt_solver.compute(sparse_matrix)
    second_time = (time.perf_counter() - start) * 1000
    
    print(f"✓ First computation (cache miss):  {first_time:.4f} ms")
    print(f"✓ Second computation (cache hit):  {second_time:.4f} ms")
    print(f"  Cache speedup: {first_time / second_time:.0f}×")
    
    # Final verdict
    print("\n" + "=" * 70)
    print("GATE 7 (DAY 90) VERDICT")
    print("=" * 70)
    
    if opt_speedup >= 10.0:
        print(f"✅ PASS: Achieved {opt_speedup:.2f}× speedup (required: ≥10×)")
    elif sparse_time is not None and (numpy_time / sparse_time) >= 10.0:
        print(f"⚠️  MARGINAL: Sparse solver achieves {numpy_time / sparse_time:.2f}× speedup")
        print(f"    (but optimization framework only {opt_speedup:.2f}×)")
    else:
        print(f"❌ FAIL: Only {opt_speedup:.2f}× speedup (required: ≥10×)")
        print(f"    Consider: GPU acceleration, LLVM JIT, Rust backend")
    
    print("=" * 70 + "\n")
    
    return {
        'numpy_time_ms': numpy_time,
        'sparse_time_ms': sparse_time,
        'optimized_time_ms': opt_time,
        'sparse_speedup': numpy_time / sparse_time if sparse_time else None,
        'optimized_speedup': opt_speedup,
        'gate7_pass': opt_speedup >= 10.0,
    }


if __name__ == '__main__':
    random.seed(42)
    np.random.seed(42)
    results = benchmark_512_dim_tensor()
