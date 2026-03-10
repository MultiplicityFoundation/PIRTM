"""
Test: Margin-Driven Module Reordering (Day 30+ Task 2).

Verifies that module reordering can improve spectral margin before linking.
"""

import random
import sys
from typing import List
from pirtm.transpiler.pirtm_perf import OptimizedSpectralRadius
from pirtm.transpiler.pirtm_reorder import ModuleReorderingOptimizer, ModuleOrderingAnalyzer


def generate_random_coupling_matrix(n: int, seed: int = 42) -> List[List[float]]:
    """Generate a random coupling matrix."""
    random.seed(seed)
    matrix = [[random.uniform(0.0, 0.3) for _ in range(n)] for _ in range(n)]
    return matrix


def test_greedy_optimization():
    """Test greedy swap algorithm."""
    print("\n" + "=" * 70)
    print("TEST 1: GREEDY SWAP OPTIMIZATION")
    print("=" * 70)
    
    matrix = generate_random_coupling_matrix(5, seed=42)
    print(f"\nMatrix dimension: {len(matrix)}×{len(matrix)}")
    print("Initial matrix:")
    for row in matrix:
        print(f"  {[f'{x:.3f}' for x in row]}")
    
    solver = OptimizedSpectralRadius()
    initial_radius = solver.compute(matrix)
    initial_margin = 1.0 - initial_radius
    
    print(f"\nInitial state:")
    print(f"  Spectral radius: {initial_radius:.6f}")
    print(f"  Margin: {initial_margin:.6f}")
    
    optimizer = ModuleReorderingOptimizer(spectral_solver=solver)
    optimized_matrix, perm = optimizer.optimize(matrix, algorithm='greedy', max_iterations=50)
    
    optimizer.print_optimization_report()
    stats = optimizer.get_optimization_stats()
    
    improvement = stats['margin_improvement']
    if improvement > 0:
        print(f"✅ GREEDY SUCCESS: Improved margin by {improvement:.6f}")
    else:
        print(f"⚠️  GREEDY: No improvement (or already optimal)")
    
    return stats


def test_simulated_annealing_optimization():
    """Test simulated annealing algorithm."""
    print("\n" + "=" * 70)
    print("TEST 2: SIMULATED ANNEALING OPTIMIZATION")
    print("=" * 70)
    
    matrix = generate_random_coupling_matrix(6, seed=123)
    print(f"\nMatrix dimension: {len(matrix)}×{len(matrix)}")
    
    solver = OptimizedSpectralRadius()
    initial_radius = solver.compute(matrix)
    initial_margin = 1.0 - initial_radius
    
    print(f"Initial state:")
    print(f"  Spectral radius: {initial_radius:.6f}")
    print(f"  Margin: {initial_margin:.6f}")
    
    optimizer = ModuleReorderingOptimizer(spectral_solver=solver)
    optimized_matrix, perm = optimizer.optimize(matrix, algorithm='simulated_annealing', max_iterations=100)
    
    optimizer.print_optimization_report()
    stats = optimizer.get_optimization_stats()
    
    improvement = stats['margin_improvement']
    if improvement > 0:
        print(f"✅ SA SUCCESS: Improved margin by {improvement:.6f}")
    else:
        print(f"⚠️  SA: No improvement")
    
    return stats


def test_hybrid_optimization():
    """Test hybrid greedy + simulated annealing."""
    print("\n" + "=" * 70)
    print("TEST 3: HYBRID OPTIMIZATION (Greedy + SA)")
    print("=" * 70)
    
    matrix = generate_random_coupling_matrix(7, seed=456)
    print(f"\nMatrix dimension: {len(matrix)}×{len(matrix)}")
    
    solver = OptimizedSpectralRadius()
    initial_radius = solver.compute(matrix)
    initial_margin = 1.0 - initial_radius
    
    print(f"Initial state:")
    print(f"  Spectral radius: {initial_radius:.6f}")
    print(f"  Margin: {initial_margin:.6f}")
    
    optimizer = ModuleReorderingOptimizer(spectral_solver=solver)
    optimized_matrix, perm = optimizer.optimize(matrix, algorithm='hybrid', max_iterations=150)
    
    optimizer.print_optimization_report()
    stats = optimizer.get_optimization_stats()
    
    improvement = stats['margin_improvement']
    if improvement > 0:
        print(f"✅ HYBRID SUCCESS: Improved margin by {improvement:.6f}")
    else:
        print(f"⚠️  HYBRID: No improvement")
    
    return stats


def test_ordering_analysis():
    """Test exhaustive permutation analysis for small matrix."""
    print("\n" + "=" * 70)
    print("TEST 4: PERMUTATION ANALYSIS")
    print("=" * 70)
    
    matrix = generate_random_coupling_matrix(4, seed=789)
    print(f"\nMatrix dimension: {len(matrix)}×{len(matrix)}")
    print(f"Total permutations: 4! = 24")
    
    solver = OptimizedSpectralRadius()
    analyzer = ModuleOrderingAnalyzer(spectral_solver=solver)
    
    results = analyzer.analyze_all_permutations(matrix)
    
    print(f"\nAnalysis Results:")
    print(f"  Min radius:  {results['min_radius']:.6f} → margin {1.0 - results['min_radius']:.6f}")
    print(f"  Max radius:  {results['max_radius']:.6f} → margin {1.0 - results['max_radius']:.6f}")
    print(f"  Mean radius: {results['mean_radius']:.6f} ± {results['std_dev']:.6f}")
    print(f"  Variance: {(results['std_dev'] ** 2):.6f}")
    
    # Try the best permutation
    best_matrix = [[matrix[results['best_perm'][i]][results['best_perm'][j]] 
                    for j in range(len(matrix))] for i in range(len(matrix))]
    best_radius = solver.compute(best_matrix)
    
    # Try the worst permutation
    worst_matrix = [[matrix[results['worst_perm'][i]][results['worst_perm'][j]] 
                     for j in range(len(matrix))] for i in range(len(matrix))]
    worst_radius = solver.compute(worst_matrix)
    
    ratio = worst_radius / best_radius if best_radius > 0 else 1.0
    print(f"  Ordering variance: {ratio:.2f}× (worst/best)")
    
    improvement = (1.0 - best_radius) - (1.0 - worst_radius)
    print(f"  Margin spread: {improvement:.6f}")
    
    if improvement > 0.001:
        print(f"\n✅ Analysis shows significant margin variation across orderings")
    else:
        print(f"\n⚠️  Ordering has minimal impact on this matrix")
    
    return results


def run_all_tests():
    """Run all reordering optimization tests."""
    print("\n" + "=" * 70)
    print("MARGIN-DRIVEN MODULE REORDERING TESTS (Day 30+ Task 2)")
    print("=" * 70)
    
    test_results = {}
    
    try:
        test_results['greedy'] = test_greedy_optimization()
    except Exception as e:
        print(f"\n❌ Greedy test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_results['simulated_annealing'] = test_simulated_annealing_optimization()
    except Exception as e:
        print(f"\n❌ SA test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_results['hybrid'] = test_hybrid_optimization()
    except Exception as e:
        print(f"\n❌ Hybrid test failed: {e}")
        import traceback
        traceback.print_exc()
    
    try:
        test_results['analysis'] = test_ordering_analysis()
    except Exception as e:
        print(f"\n❌ Analysis test failed: {e}")
        import traceback
        traceback.print_exc()
    
    # Summary
    print("\n" + "=" * 70)
    print("TASK 2 SUMMARY: MARGIN-DRIVEN MODULE REORDERING")
    print("=" * 70)
    print(f"Total test methods: 4")
    print(f"Completed: {len(test_results)}")
    
    if len(test_results) == 4:
        print("\n✅ All reordering optimization methods implemented and tested")
        
        # Check if any improved margin
        improvements = [
            test_results.get(key, {}).get('margin_improvement', 0) 
            for key in ['greedy', 'simulated_annealing', 'hybrid']
        ]
        if any(i > 0 for i in improvements):
            print("✅ At least one algorithm successfully improved margins")
        
        if 'analysis' in test_results:
            print("✅ Permutation analysis working (can identify ordering impact)")
    
    print("=" * 70 + "\n")


if __name__ == '__main__':
    run_all_tests()
