#!/usr/bin/env python3
"""
ADR-008 Day 14–16 Gate: Commitment Collision Test

Spec Reference: PIRTM ADR-008-linker-coupling-gates.md

Gate Requirement:
  Commitment-collision test passes

This test validates:
  - Test 1: Duplicate identity_commitment is rejected with diagnostic
  - Test 2: Unique commitments are accepted (pass commitment check)

Two sessions sharing the same identity_commitment must be rejected.
This enforces L0 invariant #6: human names in coupling.json do not survive into IR.

Run with: python3 pirtm/tests/test_commitment_collision.py
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.pirtm_link import PIRTMLinker, CommitmentCollisionError


class CommitmentCollisionTests:
    """Day 14-16 gate commitment collision detection tests."""
    
    @staticmethod
    def test_duplicate_identity_commitment_rejected():
        """Test 1: Two sessions with same identity_commitment must fail linking."""
        print("\n" + "=" * 70)
        print("TEST 1: DUPLICATE COMMITMENT REJECTION")
        print("=" * 70)
        print("Expected: RuntimeError with 'duplicate identity_commitment' message")
        
        # Create coupling.json with duplicate commitment
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "SessionA",
                    "identity_commitment": "0xabc123",  # ← Duplicate!
                    "modules": [
                        {
                            "name": "ModA",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.05,
                            "op_norm_T": 0.90
                        }
                    ],
                    "coupling_matrix": [[0.0]]
                },
                {
                    "name": "SessionB",
                    "identity_commitment": "0xabc123",  # ← Duplicate!
                    "modules": [
                        {
                            "name": "ModB",
                            "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
                            "prime_index": 11,
                            "epsilon": 0.03,
                            "op_norm_T": 0.80
                        }
                    ],
                    "coupling_matrix": [[0.0]]
                }
            ]
        }
        
        # Write coupling.json to temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        # Attempt to link; should fail with duplicate identity error
        linker = PIRTMLinker(coupling_path)
        
        try:
            linker.link()
            print("❌ TEST 1 FAILED: Expected CommitmentCollisionError but linking completed")
            return False
        except CommitmentCollisionError as e:
            error_msg = str(e)
            if "duplicate identity_commitment" in error_msg:
                print(f"✅ TEST 1 PASSED: {error_msg}")
                return True
            else:
                print(f"❌ TEST 1 FAILED: Wrong error message: {error_msg}")
                return False
    
    @staticmethod
    def test_unique_commitments_accepted():
        """Test 2: Sessions with unique commitments should pass commitment check."""
        print("\n" + "=" * 70)
        print("TEST 2: UNIQUE COMMITMENTS ACCEPTED")
        print("=" * 70)
        print("Expected: Commitment check passes (no duplicate)")
        
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "SessionA",
                    "identity_commitment": "0xabc123",  # ← Unique
                    "modules": [
                        {
                            "name": "ModA",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.05,
                            "op_norm_T": 0.90
                        }
                    ],
                    "coupling_matrix": [[0.0]]
                },
                {
                    "name": "SessionB",
                    "identity_commitment": "0xdef456",  # ← Unique
                    "modules": [
                        {
                            "name": "ModB",
                            "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
                            "prime_index": 11,
                            "epsilon": 0.03,
                            "op_norm_T": 0.80
                        }
                    ],
                    "coupling_matrix": [[0.0]]
                }
            ]
        }
        
        # Write coupling.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path)
        
        try:
            linker.pass1_name_resolution()
            linker.pass2_commitment_crosscheck()
            print("✅ TEST 2 PASSED: Unique commitments accepted")
            return True
        except RuntimeError as e:
            print(f"❌ TEST 2 FAILED: {e}")
            return False


class GateRunner:
    """Run all Day 14-16 commitment collision tests."""
    
    @staticmethod
    def run():
        """Execute all commitment collision tests."""
        print("\n" + "=" * 70)
        print("ADR-008 DAY 14–16 GATE: COMMITMENT-COLLISION TEST")
        print("=" * 70)
        
        tests = [
            CommitmentCollisionTests.test_duplicate_identity_commitment_rejected,
            CommitmentCollisionTests.test_unique_commitments_accepted,
        ]
        
        results = []
        for test in tests:
            try:
                result = test()
                results.append(result)
            except Exception as e:
                print(f"❌ TEST EXCEPTION: {e}")
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 70)
        if all(results):
            print(f"✅ GATE PASS: {passed}/{total} tests passed")
            print("=" * 70)
            return True
        else:
            print(f"❌ GATE FAIL: {passed}/{total} tests passed")
            print("=" * 70)
            return False


if __name__ == "__main__":
    success = GateRunner.run()
    sys.exit(0 if success else 1)
