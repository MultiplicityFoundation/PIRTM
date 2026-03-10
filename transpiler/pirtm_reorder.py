"""
Margin-Driven Module Reordering (Day 30+ optimization, Task 2).

Strategy:
  The spectral radius of a coupling matrix can change based on module ordering.
  This module provides algorithms to find module permutations that minimize
  spectral radius (maximize margin = 1 - r) before linking.

Key insight: The order in which modules are arranged in the coupling matrix
  affects the eigenvalue distribution. By reordering, we can:
  - Reduce spectral radius
  - Increase safety margin
  - Avoid near-threshold cases

Algorithms:
  1. Greedy swap: Iteratively swap modules if it reduces r
  2. Simulated annealing: Probabilistic search for global optimum
  3. Hill climbing: Local optimization with restart

Reference: ADR-008 Day 30+ optimization phase
"""

import random
import math
from typing import List, Tuple, Dict, Callable
from pirtm.transpiler.pirtm_perf import OptimizedSpectralRadius


class ModuleReorderingOptimizer:
    """Optimize module ordering to minimize spectral radius."""
    
    def __init__(self, spectral_solver: OptimizedSpectralRadius = None):
        """
        Initialize optimizer.
        
        Args:
            spectral_solver: OptimizedSpectralRadius instance (if None, create new)
        """
        self.spectral_solver = spectral_solver or OptimizedSpectralRadius(use_cache=True)
        self.optimization_stats = {
            'initial_radius': None,
            'optimized_radius': None,
            'margin_improvement': None,
            'algorithm_used': None,
            'iterations': 0,
        }
    
    def optimize(self, coupling_matrix: List[List[float]], algorithm: str = 'greedy',
                 max_iterations: int = 100, seed: int = None) -> Tuple[List[List[float]], List[int]]:
        """
        Optimize module ordering.
        
        Args:
            coupling_matrix: Original coupling matrix
            algorithm: 'greedy', 'simulated_annealing', or 'hybrid'
            max_iterations: Maximum optimization iterations
            seed: Random seed for reproducibility
        
        Returns:
            (reordered_matrix, permutation)
            where permutation is the index mapping (old_index → new_position)
        """
        if seed is not None:
            random.seed(seed)
        
        n = len(coupling_matrix)
        initial_radius = self.spectral_solver.compute(coupling_matrix)
        self.optimization_stats['initial_radius'] = initial_radius
        
        if algorithm == 'greedy':
            result_matrix, perm = self._greedy_swap(coupling_matrix, max_iterations)
        elif algorithm == 'simulated_annealing':
            result_matrix, perm = self._simulated_annealing(coupling_matrix, max_iterations)
        elif algorithm == 'hybrid':
            # Use greedy first, then SA for refinement
            result_matrix, perm = self._greedy_swap(coupling_matrix, max_iterations // 2)
            result_matrix, perm2 = self._simulated_annealing(result_matrix, max_iterations // 2)
            # Combine permutations
            perm = [perm[perm2[i]] for i in range(n)]
            result_matrix = self._apply_permutation(coupling_matrix, perm)
        else:
            raise ValueError(f"Unknown algorithm: {algorithm}")
        
        optimized_radius = self.spectral_solver.compute(result_matrix)
        self.optimization_stats['optimized_radius'] = optimized_radius
        self.optimization_stats['margin_improvement'] = (1.0 - optimized_radius) - (1.0 - initial_radius)
        self.optimization_stats['algorithm_used'] = algorithm
        
        return result_matrix, perm
    
    def _greedy_swap(self, matrix: List[List[float]], max_iterations: int) -> Tuple[List[List[float]], List[int]]:
        """
        Greedy swap algorithm: iteratively swap modules if it reduces spectral radius.
        
        Fast but may get stuck in local minima.
        """
        n = len(matrix)
        perm = list(range(n))  # Identity permutation
        current_matrix = [row[:] for row in matrix]
        current_radius = self.spectral_solver.compute(current_matrix)
        
        improved = True
        iteration = 0
        
        while improved and iteration < max_iterations:
            improved = False
            iteration += 1
            
            # Try all adjacent swaps
            for i in range(n - 1):
                # Swap positions i and i+1
                test_perm = perm[:]
                test_perm[i], test_perm[i + 1] = test_perm[i + 1], test_perm[i]
                test_matrix = self._apply_permutation(matrix, test_perm)
                test_radius = self.spectral_solver.compute(test_matrix)
                
                if test_radius < current_radius:
                    perm = test_perm
                    current_matrix = test_matrix
                    current_radius = test_radius
                    improved = True
                    break  # Restart from beginning after improvement
        
        self.optimization_stats['iterations'] = iteration
        return current_matrix, perm
    
    def _simulated_annealing(self, matrix: List[List[float]], max_iterations: int) -> Tuple[List[List[float]], List[int]]:
        """
        Simulated annealing: probabilistic search that can escape local minima.
        
        Slower but more likely to find global optimum.
        """
        n = len(matrix)
        perm = list(range(n))
        current_matrix = [row[:] for row in matrix]
        current_radius = self.spectral_solver.compute(current_matrix)
        
        best_perm = perm[:]
        best_matrix = [row[:] for row in current_matrix]
        best_radius = current_radius
        
        temperature = 1.0
        cooling_rate = 0.95
        
        for iteration in range(max_iterations):
            # Random swap
            i, j = random.randint(0, n - 1), random.randint(0, n - 1)
            if i == j:
                continue
            if i > j:
                i, j = j, i
            
            test_perm = perm[:]
            test_perm[i], test_perm[j] = test_perm[j], test_perm[i]
            test_matrix = self._apply_permutation(matrix, test_perm)
            test_radius = self.spectral_solver.compute(test_matrix)
            
            # Acceptance criterion
            delta = test_radius - current_radius
            if delta < 0:  # Improvement
                perm = test_perm
                current_matrix = test_matrix
                current_radius = test_radius
                
                if test_radius < best_radius:
                    best_perm = perm[:]
                    best_matrix = [row[:] for row in current_matrix]
                    best_radius = test_radius
            else:
                # Accept worse solution with probability exp(-delta / temperature)
                if random.random() < math.exp(-delta / max(temperature, 0.01)):
                    perm = test_perm
                    current_matrix = test_matrix
                    current_radius = test_radius
            
            temperature *= cooling_rate
        
        self.optimization_stats['iterations'] = max_iterations
        return best_matrix, best_perm
    
    def _apply_permutation(self, matrix: List[List[float]], perm: List[int]) -> List[List[float]]:
        """
        Apply permutation to matrix rows and columns.
        
        If perm = [0, 2, 1, 3], then:
          new_matrix[i][j] = old_matrix[perm[i]][perm[j]]
        """
        n = len(matrix)
        result = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(n):
                result[i][j] = matrix[perm[i]][perm[j]]
        
        return result
    
    def print_optimization_report(self):
        """Print optimization results."""
        stats = self.optimization_stats
        print("\n" + "=" * 70)
        print("MODULE REORDERING OPTIMIZATION REPORT")
        print("=" * 70)
        print(f"Algorithm: {stats.get('algorithm_used', 'unknown').upper()}")
        print(f"Iterations: {stats.get('iterations', 0)}")
        print(f"\nSpectral Radius:")
        print(f"  Before: {stats['initial_radius']:.6f}")
        print(f"  After:  {stats['optimized_radius']:.6f}")
        print(f"  Reduction: {stats['initial_radius'] - stats['optimized_radius']:.6f}")
        print(f"\nMargin:")
        print(f"  Before: {1.0 - stats['initial_radius']:.6f}")
        print(f"  After:  {1.0 - stats['optimized_radius']:.6f}")
        print(f"  Improvement: {stats['margin_improvement']:.6f}")
        print("=" * 70 + "\n")
    
    def get_optimization_stats(self) -> Dict:
        """Return optimization statistics."""
        return self.optimization_stats.copy()


class ModuleOrderingAnalyzer:
    """Analyze how module ordering affects spectral radius."""
    
    def __init__(self, spectral_solver: OptimizedSpectralRadius = None):
        """Initialize analyzer."""
        self.spectral_solver = spectral_solver or OptimizedSpectralRadius(use_cache=True)
    
    def analyze_all_permutations(self, matrix: List[List[float]]) -> Dict:
        """
        Analyze all (or subset of) permutations.
        
        For small matrices (n ≤ 8), analyzes all n! permutations.
        For larger matrices, samples random permutations.
        """
        n = len(matrix)
        
        if n <= 8:
            return self._exhaustive_analysis(matrix)
        else:
            return self._sampling_analysis(matrix, num_samples=1000)
    
    def _exhaustive_analysis(self, matrix: List[List[float]]) -> Dict:
        """Exhaustive analysis for small matrices."""
        import itertools
        n = len(matrix)
        
        results = {
            'permutations': [],
            'spectral_radii': [],
            'min_radius': float('inf'),
            'max_radius': -float('inf'),
            'mean_radius': 0.0,
            'std_dev': 0.0,
            'best_perm': None,
            'worst_perm': None,
        }
        
        radii = []
        for perm in itertools.permutations(range(n)):
            perm_list = list(perm)
            perm_matrix = self._apply_permutation(matrix, perm_list)
            radius = self.spectral_solver.compute(perm_matrix)
            
            results['permutations'].append(perm_list)
            results['spectral_radii'].append(radius)
            radii.append(radius)
            
            if radius < results['min_radius']:
                results['min_radius'] = radius
                results['best_perm'] = perm_list
            if radius > results['max_radius']:
                results['max_radius'] = radius
                results['worst_perm'] = perm_list
        
        # Compute statistics
        results['mean_radius'] = sum(radii) / len(radii)
        variance = sum((r - results['mean_radius']) ** 2 for r in radii) / len(radii)
        results['std_dev'] = math.sqrt(variance)
        results['num_permutations'] = len(radii)
        
        return results
    
    def _sampling_analysis(self, matrix: List[List[float]], num_samples: int = 1000) -> Dict:
        """Sampling analysis for large matrices."""
        n = len(matrix)
        
        results = {
            'samples': num_samples,
            'spectral_radii': [],
            'min_radius': float('inf'),
            'max_radius': -float('inf'),
            'mean_radius': 0.0,
            'std_dev': 0.0,
            'best_perm': None,
            'worst_perm': None,
        }
        
        radii = []
        for _ in range(num_samples):
            perm = list(range(n))
            random.shuffle(perm)
            perm_matrix = self._apply_permutation(matrix, perm)
            radius = self.spectral_solver.compute(perm_matrix)
            
            results['spectral_radii'].append(radius)
            radii.append(radius)
            
            if radius < results['min_radius']:
                results['min_radius'] = radius
                results['best_perm'] = perm
            if radius > results['max_radius']:
                results['max_radius'] = radius
                results['worst_perm'] = perm
        
        # Statistics
        results['mean_radius'] = sum(radii) / len(radii)
        variance = sum((r - results['mean_radius']) ** 2 for r in radii) / len(radii)
        results['std_dev'] = math.sqrt(variance)
        
        return results
    
    def _apply_permutation(self, matrix: List[List[float]], perm: List[int]) -> List[List[float]]:
        """Apply permutation to matrix."""
        n = len(matrix)
        result = [[0.0] * n for _ in range(n)]
        for i in range(n):
            for j in range(n):
                result[i][j] = matrix[perm[i]][perm[j]]
        return result
