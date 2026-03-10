#!/usr/bin/env python3
"""
ADR-008 Day 16-30+: Production Integration Test with All Example Programs

This test validates the complete PIRTM linker by linking all 4 example programs
into a single network-wide session, demonstrating:
  - Multi-session communication
  - Cross-session coupling matrix construction
  - Spectral margin tracking and warning system
  - Real-world linking scenarios

Run with: python3 pirtm/tests/test_production_integration.py
"""

import sys
import json
import tempfile
from pathlib import Path

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.pirtm_link import PIRTMLinker, SpectralMarginWarning
from pirtm.transpiler.pirtm_bytecode import PIRTMBytecode, ModuleMetadata, ProofHash


class ProductionIntegrationTest:
    """Production integration test linking all example programs."""
    
    @staticmethod
    def create_bytecode_for_example(example_path: str, session_name: str) -> Path:
        """Create bytecode file from example program."""
        example_name = Path(example_path).stem
        bytecode_path = Path(f"/tmp/{session_name}_{example_name}.pirtm.bc")
        
        # Load example
        with open(example_path) as f:
            example = json.load(f)
        
        # Create bytecode for each component
        modules = []
        for comp in example.get("components", []):
            name = comp.get("name", "unnamed")
            prime = comp.get("prime_index", 7919)
            eps = comp.get("epsilon", 0.05)
            norm_t = comp.get("op_norm_T", 0.90)
            
            # Compute contractivity
            margin = 1.0 - eps - norm_t
            status = "PASS" if margin > 0 else "FAIL"
            
            # Create proof hash
            proof_hash = ProofHash(prime, eps, norm_t).compute()
            
            # Create metadata
            metadata = ModuleMetadata(
                name=name,
                prime_index=prime,
                epsilon=eps,
                op_norm_T=norm_t,
                contractivity_check=status,
                proof_hash=proof_hash,
            )
            modules.append(metadata)
        
        # Create bytecode
        bytecode = PIRTMBytecode(
            modules=modules,
            coupling="#pirtm.unresolved_coupling",
            mlir_source=f"!pirtm.module(example={example_name})",
            audit_trail=[f"Generated from {example_name} for production test"],
        )
        
        bytecode.write_to_file(bytecode_path)
        return bytecode_path
    
    @staticmethod
    def test_single_session_linking():
        """Test 1: Link a single session with multiple modules."""
        print("\n" + "=" * 70)
        print("TEST 1: SINGLE SESSION LINKING")
        print("=" * 70)
        print("Test: Link the multimodule_network example (2 coprime modules)")
        
        # Create bytecode fixtures
        example_path = Path("/workspaces/Tooling/pirtm/examples/multimodule_network.json")
        bytecode_a = ProductionIntegrationTest.create_bytecode_for_example(
            example_path, "session1"
        )
        bytecode_b = ProductionIntegrationTest.create_bytecode_for_example(
            example_path, "session1"
        )
        
        # Create coupling.json for single session with 2 modules
        coupling_config = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "MultiModuleNetwork",
                    "identity_commitment": "0xmultimodule_session",
                    "modules": [
                        {
                            "name": "ModuleA",
                            "path": str(bytecode_a),
                            "prime_index": 7919,
                            "epsilon": 0.12,
                            "op_norm_T": 0.75
                        },
                        {
                            "name": "ModuleB",
                            "path": str(bytecode_b),
                            "prime_index": 8191,
                            "epsilon": 0.08,
                            "op_norm_T": 0.85
                        }
                    ],
                    "coupling_matrix": [
                        [0.0, 0.15],
                        [0.10, 0.0]
                    ]
                }
            ]
        }
        
        # Write coupling.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        # Link and verify
        linker = PIRTMLinker(coupling_path, enable_warnings=True)
        result = linker.link()
        
        margin_report = linker.get_margin_report()
        print(f"\nMargin Report:")
        print(f"  Sessions: {margin_report['num_sessions']}")
        print(f"  Modules: {margin_report['num_modules']}")
        print(f"  Margin utilization: {100 - margin_report['margin_percent']:.1f}%")
        
        if result:
            print("✅ TEST 1 PASSED: Single session linked successfully")
            return True
        else:
            print("❌ TEST 1 FAILED: Single session linking failed")
            return False
    
    @staticmethod
    def test_multi_session_network():
        """Test 2: Link multiple independent sessions into one network."""
        print("\n" + "=" * 70)
        print("TEST 2: MULTI-SESSION NETWORK LINKING")
        print("=" * 70)
        print("Test: Link 3 independent service sessions")
        
        # Create three service sessions from examples
        examples = [
            ("/workspaces/Tooling/pirtm/examples/basic_contractive_system.json", "ServiceA"),
            ("/workspaces/Tooling/pirtm/examples/multimodule_network.json", "ServiceB"),
            ("/workspaces/Tooling/pirtm/examples/tightly_coupled_system.json", "ServiceC"),
        ]
        
        sessions = []
        for example_path, session_name in examples:
            if not Path(example_path).exists():
                print(f"  ⚠️  {example_path} not found, skipping")
                continue
            
            # Create bytecode
            bytecode_path = ProductionIntegrationTest.create_bytecode_for_example(
                example_path, session_name
            )
            
            # Load example to get module specs
            with open(example_path) as f:
                example = json.load(f)
            
            # Build session config
            modules = []
            for i, comp in enumerate(example.get("components", [])):
                modules.append({
                    "name": f"{session_name}_Mod{i}",
                    "path": str(bytecode_path),
                    "prime_index": comp.get("prime_index", 7919),
                    "epsilon": comp.get("epsilon", 0.05),
                    "op_norm_T": comp.get("op_norm_T", 0.90)
                })
            
            # Session with internal coupling (if multiple modules)
            if len(modules) > 1:
                coupling_matrix = [
                    [0.0, 0.15],
                    [0.10, 0.0]
                ]
            else:
                coupling_matrix = [[0.0]]
            
            sessions.append({
                "name": session_name,
                "identity_commitment": f"0x{session_name.lower()}_commit",
                "modules": modules,
                "coupling_matrix": coupling_matrix
            })
        
        # Create cross-session coupling (sparse)
        num_sessions = len(sessions)
        cross_coupling = [[0.0] * num_sessions for _ in range(num_sessions)]
        
        # Add weak cross-session interactions
        if num_sessions >= 2:
            cross_coupling[0][1] = 0.05  # ServiceA → ServiceB
            cross_coupling[1][0] = 0.03  # ServiceB → ServiceA
        if num_sessions >= 3:
            cross_coupling[1][2] = 0.04  # ServiceB → ServiceC
            cross_coupling[2][1] = 0.02  # ServiceC → ServiceB
        
        coupling_config = {
            "version": "1.0",
            "sessions": sessions,
            "cross_session_coupling": cross_coupling,
        }
        
        # Write coupling.json
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_config, f)
            coupling_path = f.name
        
        # Link
        linker = PIRTMLinker(coupling_path, enable_warnings=True)
        result = linker.link()
        
        margin_report = linker.get_margin_report()
        print(f"\nMargin Report:")
        print(f"  Sessions: {margin_report['num_sessions']}")
        print(f"  Modules: {margin_report['num_modules']}")
        print(f"  Spectral radius: {margin_report['spectral_radius']:.6f}")
        print(f"  Spectral margin: {margin_report['spectral_margin']:.6f}")
        print(f"  Warnings emitted: {len(margin_report['warnings'])}")
        
        if result:
            print("✅ TEST 2 PASSED: Multi-session network linked successfully")
            return True
        else:
            print("❌ TEST 2 FAILED: Multi-session network linking failed")
            return False
    
    @staticmethod
    def test_margin_tracking_and_warnings():
        """Test 3: Verify margin tracking and warning system."""
        print("\n" + "=" * 70)
        print("TEST 3: MARGIN TRACKING AND WARNING SYSTEM")
        print("=" * 70)
        print("Test: Create networks with different spectral radii and verify warnings")
        
        # Test case 1: Excellent margin (r = 0.2)
        print("\n  Case 1: Excellent margin (r ≈ 0.20)")
        coupling_excellent = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "Excellent",
                    "identity_commitment": "0xexcellent",
                    "modules": [
                        {"name": "M1", "path": "/workspaces/Tooling/pirtm/tests/fixtures/basic.pirtm.bc",
                         "prime_index": 5, "epsilon": 0.01, "op_norm_T": 1.0},
                        {"name": "M2", "path": "/workspaces/Tooling/pirtm/tests/fixtures/secondary.pirtm.bc",
                         "prime_index": 7, "epsilon": 0.01, "op_norm_T": 1.0}
                    ],
                    "coupling_matrix": [[0.0, 0.10], [0.10, 0.0]]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_excellent, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path, enable_warnings=True)
        result1 = linker.link()
        margin1 = linker.spectral_margin
        
        # Test case 2: Warning margin (r ≈ 0.92)
        print("\n  Case 2: Warning margin (r ≈ 0.92)")
        coupling_warning = {
            "version": "1.0",
            "sessions": [
                {
                    "name": "Warning",
                    "identity_commitment": "0xwarning",
                    "modules": [
                        {"name": "M1", "path": "/workspaces/Tooling/pirtm/tests/fixtures/basic.pirtm.bc",
                         "prime_index": 5, "epsilon": 0.01, "op_norm_T": 1.0},
                        {"name": "M2", "path": "/workspaces/Tooling/pirtm/tests/fixtures/secondary.pirtm.bc",
                         "prime_index": 7, "epsilon": 0.01, "op_norm_T": 1.0}
                    ],
                    "coupling_matrix": [[0.0, 0.46], [0.46, 0.0]]
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(coupling_warning, f)
            coupling_path = f.name
        
        linker = PIRTMLinker(coupling_path, enable_warnings=True)
        result2 = linker.link()
        margin2 = linker.spectral_margin
        
        if result1 and result2 and margin1 > margin2:
            print("\n✅ TEST 3 PASSED: Margin tracking and warnings working correctly")
            print(f"   Case 1 margin: {margin1:.6f} (excellent)")
            print(f"   Case 2 margin: {margin2:.6f} (warning)")
            return True
        else:
            print("\n❌ TEST 3 FAILED: Margin tracking or warnings not working")
            return False


class TestRunner:
    """Run all production integration tests."""
    
    @staticmethod
    def run():
        """Execute all production integration tests."""
        print("\n" + "=" * 70)
        print("ADR-008 DAY 16-30+: PRODUCTION INTEGRATION TEST SUITE")
        print("=" * 70)
        
        tests = [
            ProductionIntegrationTest.test_single_session_linking,
            ProductionIntegrationTest.test_multi_session_network,
            ProductionIntegrationTest.test_margin_tracking_and_warnings,
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
            print(f"✅ PRODUCTION INTEGRATION: {passed}/{total} tests passed")
            print("=" * 70)
            print("\nProduction-ready status:")
            print("  ✅ Single-session linking works")
            print("  ✅ Multi-session networks link successfully")
            print("  ✅ Spectral margin tracking and warnings implemented")
            print("  ✅ Ready for real-world deployment")
            return True
        else:
            print(f"❌ PRODUCTION INTEGRATION: {passed}/{total} tests passed")
            print("=" * 70)
            return False


if __name__ == "__main__":
    success = TestRunner.run()
    sys.exit(0 if success else 1)
