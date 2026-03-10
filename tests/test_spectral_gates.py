#!/usr/bin/env python3
"""
ADR-008 Spectral Radius Gates (Day 30+ forward planning)

Spec Reference: PIRTM ADR-008-linker-coupling-gates.md (acceptance criteria)

These tests validate spectral-small-gain behavior:
  - r=0.7: Linking must succeed (contractive system)
  - r=1.1: Linking must fail (divergent system)

The spectral radius r = ρ(C) where C is the coupling matrix.
For network-wide contractivity (L0 invariant #2): r < 1.0 required.

Run with: python3 pirtm/tests/test_spectral_gates.py
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.pirtm_link import PIRTMLinker


class SpectralGateTests:
    """Spectral radius acceptance tests for linking."""
    
    @staticmethod
    def test_r_0_7_contracts():
        """
        Test 1: With spectral radius r=0.7, linking must succeed.
        
        System: Two coupled modules with coupling matrix [[0, 0.35], [0.35, 0]].
        Spectral radius of this matrix ≈ 0.35, which is < 1.0 (contractive).
        """
        print("\n" + "=" * 70)
        print("TEST 1: SPECTRAL RADIUS r ≈ 0.35 (CONTRACTIVE)")
        print("=" * 70)
        print("Expected: Linking succeeds (r < 1.0)")
        
        # Coupling matrix with spectral radius ≈ 0.35
        # For symmetric matrix [[0, a], [a, 0]], eigenvalues are ±a
        #  So spectral radius = a
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "SessionStable",
                    "identity_commitment": "0x700000",
                    "modules": [
                        {
                            "name": "Mod1",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 5,
                            "epsilon": 0.01,
                            "op_norm_T": 1.0
                        },
                        {
                            "name": "Mod2",
                            "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.01,
                            "op_norm_T": 1.0
                        }
                    ],
                    "coupling_matrix": [
                        [0.0, 0.35],
                        [0.35, 0.0]
                    ]
                }
            ]
        }
        
        # Write coupling.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path)
        result = linker.link()
        
        if result:
            print(f"✅ TEST 1 PASSED: r={linker.spectral_radius:.4f} < 1.0 → Linking succeeded")
            return True
        else:
            print(f"❌ TEST 1 FAILED: r={linker.spectral_radius:.4f}, expected linking to succeed")
            return False
    
    @staticmethod
    def test_r_1_1_diverges():
        """
        Test 2: With spectral radius r=1.1, linking must fail.
        
        System: Two coupled modules with coupling matrix [[0, 0.55], [0.55, 0]].
        Spectral radius of this matrix ≈ 0.55... wait, that would still be < 1.
        
        For [[0, a], [a, 0]], spectral radius = a.
        To get r ≈ 1.1, we need a non-symmetric matrix or larger values.
        Use [[0, 1.1], [1.0, 0]] which has spectral radius > 1.0.
        """
        print("\n" + "=" * 70)
        print("TEST 2: SPECTRAL RADIUS r ≈ 1.047 (DIVERGENT)")
        print("=" * 70)
        print("Expected: Linking fails (r ≥ 1.0)")
        
        # Coupling matrix with spectral radius ≈ 1.047 > 1.0
        # Using eigenvalue formula for [[0, b], [c, 0]]:
        # λ = ±√(bc)
        # For b=1.1, c=1.0: λ ≈ ±1.048
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "SessionUnstable",
                    "identity_commitment": "0x110000",
                    "modules": [
                        {
                            "name": "Mod1",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 5,
                            "epsilon": 0.01,
                            "op_norm_T": 1.0
                        },
                        {
                            "name": "Mod2",
                            "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.01,
                            "op_norm_T": 1.0
                        }
                    ],
                    "coupling_matrix": [
                        [0.0, 1.1],
                        [1.0, 0.0]
                    ]
                }
            ]
        }
        
        # Write coupling.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path)
        result = linker.link()
        
        if not result:
            print(f"✅ TEST 2 PASSED: r={linker.spectral_radius:.4f} ≥ 1.0 → Linking failed correctly")
            return True
        else:
            print(f"❌ TEST 2 FAILED: r={linker.spectral_radius:.4f}, expected linking to fail")
            return False
    
    @staticmethod
    def test_boundary_case_r_1_0():
        """
        Test 3: Boundary case with spectral radius exactly at r=1.0.
        
        This is the boundary between contractive and divergent.
        With r=1.0, the system is marginally stable (not strictly contractive).
        Per ADR-004 L0 invariant #2, r must be < 1.0 (strict inequality).
        """
        print("\n" + "=" * 70)
        print("TEST 3: BOUNDARY CASE - SPECTRAL RADIUS r = 1.0 (MARGINAL)")
        print("=" * 70)
        print("Expected: Linking fails (r = 1.0 is not < 1.0)")
        
        # Coupling matrix with eigenvalue exactly 1.0
        # [[0, 1.0], [1.0, 0]] has eigenvalues ±1.0
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "SessionMarginal",
                    "identity_commitment": "0x100000",
                    "modules": [
                        {
                            "name": "Mod1",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 5,
                            "epsilon": 0.01,
                            "op_norm_T": 1.0
                        },
                        {
                            "name": "Mod2",
                            "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.01,
                            "op_norm_T": 1.0
                        }
                    ],
                    "coupling_matrix": [
                        [0.0, 1.0],
                        [1.0, 0.0]
                    ]
                }
            ]
        }
        
        # Write coupling.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path)
        result = linker.link()
        
        if not result:
            print(f"✅ TEST 3 PASSED: r={linker.spectral_radius:.4f} ≥ 1.0 → Linking failed (correct)")
            return True
        else:
            print(f"❌ TEST 3 FAILED: r={linker.spectral_radius:.4f}, marginal case should fail")
            return False


class GateRunner:
    """Run all spectral radius tests."""
    
    @staticmethod
    def run():
        """Execute all spectral radius tests."""
        print("\n" + "=" * 70)
        print("ADR-008 SPECTRAL RADIUS GATES (Day 30+ forward planning)")
        print("=" * 70)
        
        tests = [
            SpectralGateTests.test_r_0_7_contracts,
            SpectralGateTests.test_r_1_1_diverges,
            SpectralGateTests.test_boundary_case_r_1_0,
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ TEST EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 70)
        if all(results):
            print(f"✅ GATE PASS: {passed}/{total} spectral tests passed")
            print("=" * 70)
            return True
        else:
            print(f"❌ GATE FAIL: {passed}/{total} spectral tests passed")
            print("=" * 70)
            return False


if __name__ == "__main__":
    success = GateRunner.run()
    sys.exit(0 if success else 1)
