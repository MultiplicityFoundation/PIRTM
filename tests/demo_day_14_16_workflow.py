#!/usr/bin/env python3
"""
ADR-008 Day 14–16 Gate: End-to-End Linking Workflow Demo

Complete demonstration of PIRTM linker infrastructure:
  Pass 1: Name Resolution (locate .pirtm.bc files)
  Pass 2: Commitment Crosscheck (detect duplicate identity)
  Pass 3: Matrix Construction (build full coupling matrix)
  Pass 4: Spectral Small-Gain (verify network-wide stability)

Run with: python3 pirtm/tests/demo_day_14_16_workflow.py
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.pirtm_link import PIRTMLinker, CommitmentCollisionError


class Day1416WorkflowDemo:
    """End-to-end workflow demonstration for Day 14–16 gate."""
    
    @staticmethod
    def demo_successful_linking():
        """Demo 1: Successful linking with contractive network."""
        print("\n" + "=" * 70)
        print("DEMO 1: SUCCESSFUL LINKING (Contractive Network)")
        print("=" * 70)
        
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "ServiceA",
                    "identity_commitment": "0xservice_a_commitment",
                    "modules": [
                        {
                            "name": "ProcessorA1",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.05,
                            "op_norm_T": 0.90
                        },
                        {
                            "name": "ProcessorA2",
                            "path": "pirtm/tests/fixtures/module_a.pirtm.bc",
                            "prime_index": 13,
                            "epsilon": 0.02,
                            "op_norm_T": 0.85
                        }
                    ],
                    "coupling_matrix": [
                        [0.0, 0.20],
                        [0.15, 0.0]
                    ]
                },
                {
                    "name": "ServiceB",
                    "identity_commitment": "0xservice_b_commitment",
                    "modules": [
                        {
                            "name": "ProcessorB1",
                            "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
                            "prime_index": 11,
                            "epsilon": 0.03,
                            "op_norm_T": 0.80
                        }
                    ],
                    "coupling_matrix": [[0.0]]
                }
            ],
            "cross_session_coupling": [
                [0.0, 0.10],
                [0.08, 0.0]
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path)
        result = linker.link()
        
        return result
    
    @staticmethod
    def demo_commitment_collision_rejection():
        """Demo 2: Commitment collision detection and rejection."""
        print("\n" + "=" * 70)
        print("DEMO 2: COMMITMENT COLLISION DETECTION")
        print("=" * 70)
        
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "AuthenticService",
                    "identity_commitment": "0xshared_identity",
                    "modules": [
                        {
                            "name": "Module1",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.05,
                            "op_norm_T": 0.90
                        }
                    ],
                    "coupling_matrix": [[0.0]]
                },
                {
                    "name": "SpoofedService",
                    "identity_commitment": "0xshared_identity",  # ← DUPLICATE!
                    "modules": [
                        {
                            "name": "Module2",
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
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path)
        
        try:
            linker.link()
            print("❌ Demo 2 FAILED: Expected CommitmentCollisionError")
            return False
        except CommitmentCollisionError as e:
            print(f"✅ Demo 2 SUCCESS: Collision detected and rejected")
            print(f"   Error message: {str(e).split(chr(10))[0]}")
            return True
    
    @staticmethod
    def demo_divergent_network_rejection():
        """Demo 3: Divergent network detection (spectral radius > 1)."""
        print("\n" + "=" * 70)
        print("DEMO 3: DIVERGENT NETWORK REJECTION (r > 1.0)")
        print("=" * 70)
        
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "UnstableSystem",
                    "identity_commitment": "0xunstable_system",
                    "modules": [
                        {
                            "name": "Module1",
                            "path": "pirtm/tests/fixtures/basic.pirtm.bc",
                            "prime_index": 7,
                            "epsilon": 0.05,
                            "op_norm_T": 0.90
                        },
                        {
                            "name": "Module2",
                            "path": "pirtm/tests/fixtures/secondary.pirtm.bc",
                            "prime_index": 11,
                            "epsilon": 0.03,
                            "op_norm_T": 0.80
                        }
                    ],
                    "coupling_matrix": [
                        [0.0, 1.2],
                        [1.1, 0.0]
                    ]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path)
        result = linker.link()
        
        if not result:
            print(f"✅ Demo 3 SUCCESS: Divergent network rejected (r={linker.spectral_radius:.4f} > 1.0)")
            return True
        else:
            print(f"❌ Demo 3 FAILED: Expected linking to fail for divergent network")
            return False


class DemoRunner:
    """Run all workflow demos."""
    
    @staticmethod
    def run():
        """Execute all demonstration workflows."""
        print("\n" + "=" * 70)
        print("ADR-008 DAY 14–16 GATE: COMPLETE WORKFLOW DEMONSTRATION")
        print("=" * 70)
        
        demos = [
            ("Successful Linking", Day1416WorkflowDemo.demo_successful_linking),
            ("Commitment Collision Rejection", Day1416WorkflowDemo.demo_commitment_collision_rejection),
            ("Divergent Network Rejection", Day1416WorkflowDemo.demo_divergent_network_rejection),
        ]
        
        results = []
        for name, demo_fn in demos:
            try:
                result = demo_fn()
                results.append(result)
            except Exception as e:
                print(f"❌ DEMO EXCEPTION: {e}")
                import traceback
                traceback.print_exc()
                results.append(False)
        
        # Summary
        passed = sum(results)
        total = len(results)
        
        print("\n" + "=" * 70)
        if all(results):
            print(f"✅ ALL DEMOS SUCCESSFUL: {passed}/{total} complete workflows passed")
            print("=" * 70)
            print("\nDay 14–16 Gate Infrastructure Status:")
            print("  ✅ Three-pass linker (name resolution, commitment check, matrix build)")
            print("  ✅ Commitment collision detection (security gate)")
            print("  ✅ Spectral radius computation (network stability)")
            print("  ✅ Error handling and diagnostics")
            print("\nReady for production linking!")
            return True
        else:
            print(f"❌ DEMOS FAILED: {passed}/{total} workflows passed")
            print("=" * 70)
            return False


if __name__ == "__main__":
    success = DemoRunner.run()
    sys.exit(0 if success else 1)
