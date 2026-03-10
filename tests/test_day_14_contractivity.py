#!/usr/bin/env python3
"""
ADR-007 Day 14 Gate: Contractivity Check Transpile-Time Verification

Spec Reference: PIRTM ADR-004 L0 invariant #2, ADR-007 Day 14

Gate Requirement:
  pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"

This test validates:
  - Test 1: Contractive system (‖T‖ + ε < 1) → PASS
  - Test 2: Marginally stable system (‖T‖ + ε = 1) → FAIL
  - Test 3: Divergent system (‖T‖ + ε > 1) → FAIL
  - Test 4: Bytecode generation and inspection workflow

Run with: python3 pirtm/tests/test_day_14_contractivity.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.pirtm_bytecode import (
    ContractivityCheckPass,
    ProofHash,
    ModuleMetadata,
    PIRTMBytecode,
    create_bytecode_from_mlir,
)
from pirtm.tools.pirtm_inspect import PIRTMInspector


class Day14GateTests:
    """Day 14 gate contractivity verification tests."""
    
    @staticmethod
    def test_contractive_system():
        """Test 1: Contractive system (margin > 0) → PASS."""
        print("\n" + "=" * 70)
        print("TEST 1: CONTRACTIVE SYSTEM (margin > 0)")
        print("=" * 70)
        
        # Module: ε=0.05, ‖T‖=0.90
        # Margin: 1 - 0.05 - 0.90 = 0.05 > 0 ✓
        status, reason = ContractivityCheckPass.check_module(
            module_name="linear_recurrence",
            prime_index=7919,
            epsilon=0.05,
            op_norm_T=0.90,
        )
        
        print(f"Module: linear_recurrence")
        print(f"  prime_index=7919, ε=0.05, ‖T‖=0.90")
        print(f"  Margin = 1 - 0.05 - 0.90 = 0.05")
        print(f"  Status: {status}")
        print(f"  Reason: {reason}")
        
        if status == "PASS":
            print(f"✅ TEST 1 PASS: System is contractive")
            return True
        else:
            print(f"❌ TEST 1 FAIL: Expected PASS but got {status}")
            return False
    
    @staticmethod
    def test_marginally_stable_system():
        """Test 2: Marginally stable system (margin = 0) → FAIL."""
        print("\n" + "=" * 70)
        print("TEST 2: MARGINALLY STABLE SYSTEM (margin = 0)")
        print("=" * 70)
        
        # Module: ε=0.05, ‖T‖=0.95
        # Margin: 1 - 0.05 - 0.95 = 0 (NOT contractive)
        status, reason = ContractivityCheckPass.check_module(
            module_name="marginal_system",
            prime_index=8191,
            epsilon=0.05,
            op_norm_T=0.95,
        )
        
        print(f"Module: marginal_system")
        print(f"  prime_index=8191, ε=0.05, ‖T‖=0.95")
        print(f"  Margin = 1 - 0.05 - 0.95 = 0")
        print(f"  Status: {status}")
        print(f"  Reason: {reason}")
        
        if status == "FAIL":
            print(f"✅ TEST 2 PASS: System correctly rejected")
            return True
        else:
            print(f"❌ TEST 2 FAIL: Expected FAIL but got {status}")
            return False
    
    @staticmethod
    def test_divergent_system():
        """Test 3: Divergent system (margin < 0) → FAIL."""
        print("\n" + "=" * 70)
        print("TEST 3: DIVERGENT SYSTEM (margin < 0)")
        print("=" * 70)
        
        # Module: ε=0.05, ‖T‖=1.10
        # Margin: 1 - 0.05 - 1.10 = -0.15 (DIVERGENT)
        status, reason = ContractivityCheckPass.check_module(
            module_name="divergent_system",
            prime_index=11,
            epsilon=0.05,
            op_norm_T=1.10,
        )
        
        print(f"Module: divergent_system")
        print(f"  prime_index=11, ε=0.05, ‖T‖=1.10")
        print(f"  Margin = 1 - 0.05 - 1.10 = -0.15")
        print(f"  Status: {status}")
        print(f"  Reason: {reason}")
        
        if status == "FAIL":
            print(f"✅ TEST 3 PASS: System correctly rejected")
            return True
        else:
            print(f"❌ TEST 3 FAIL: Expected FAIL but got {status}")
            return False
    
    @staticmethod
    def test_bytecode_generation_and_inspection():
        """Test 4: Bytecode generation and inspection workflow."""
        print("\n" + "=" * 70)
        print("TEST 4: BYTECODE GENERATION AND INSPECTION WORKFLOW")
        print("=" * 70)
        
        # Create MLIR-like input
        mlir_text = (
            "module @basic_contractive_system {\n"
            "  func.func @recurrence(%x : tensor<?xf32>) -> tensor<?xf32> {\n"
            "    %result = %x : tensor<?xf32>\n"
            "    return %result : tensor<?xf32>\n"
            "  }\n"
            "}\n"
        )
        
        modules = [
            {
                "name": "linear_recurrence",
                "prime_index": 7919,
                "epsilon": 0.05,
                "op_norm_T": 0.90,
            }
        ]
        
        # Generate bytecode
        print("Step 1: Creating bytecode from MLIR...")
        bytecode = create_bytecode_from_mlir(mlir_text, modules)
        print(f"  ✅ Created bytecode with {len(bytecode.modules)} module(s)")
        
        # Verify all modules are contractive
        if not bytecode.all_modules_contractive():
            print(f"❌ TEST 4 FAIL: Not all modules are contractive")
            return False
        print(f"  ✅ All modules passed contractivity check")
        
        # Write to temporary file
        print("Step 2: Writing bytecode to file...")
        with tempfile.NamedTemporaryFile(suffix=".pirtm.bc", delete=False) as f:
            temp_bc_path = Path(f.name)
        
        bytecode.write_to_file(temp_bc_path)
        print(f"  ✅ Wrote bytecode to {temp_bc_path}")
        
        # Read back and verify
        print("Step 3: Reading bytecode back...")
        loaded_bytecode = PIRTMBytecode.read_from_file(temp_bc_path)
        if len(loaded_bytecode.modules) != 1:
            print(f"❌ TEST 4 FAIL: Module count mismatch")
            return False
        print(f"  ✅ Loaded bytecode with {len(loaded_bytecode.modules)} module(s)")
        
        # Verify round-trip
        original_hash = bytecode.modules[0].proof_hash
        loaded_hash = loaded_bytecode.modules[0].proof_hash
        if original_hash != loaded_hash:
            print(f"❌ TEST 4 FAIL: Proof hash mismatch after round-trip")
            return False
        print(f"  ✅ Proof hash verified: {original_hash}")
        
        # Clean up
        temp_bc_path.unlink()
        
        print(f"✅ TEST 4 PASS: Bytecode generation and inspection workflow successful")
        return True
    
    @staticmethod
    def test_inspection_tool_output():
        """Test 5: Inspection tool produces correct output format."""
        print("\n" + "=" * 70)
        print("TEST 5: INSPECTION TOOL OUTPUT FORMAT")
        print("=" * 70)
        
        # Create bytecode with contractive modules
        mlir_text = "module @test { }\n"
        modules = [
            {
                "name": "module_A",
                "prime_index": 7919,
                "epsilon": 0.12,
                "op_norm_T": 0.75,
            },
            {
                "name": "module_B",
                "prime_index": 8191,
                "epsilon": 0.08,
                "op_norm_T": 0.85,
            }
        ]
        
        bytecode = create_bytecode_from_mlir(mlir_text, modules)
        
        # Write to temporary file
        with tempfile.NamedTemporaryFile(suffix=".pirtm.bc", delete=False) as f:
            temp_bc_path = Path(f.name)
        
        bytecode.write_to_file(temp_bc_path)
        
        # Capture inspection output
        import io
        from contextlib import redirect_stdout
        
        f = io.StringIO()
        with redirect_stdout(f):
            result = PIRTMInspector.inspect_file(temp_bc_path, verbose=False)
        
        output = f.getvalue()
        
        # Verify output contains contractivity_check: PASS
        if "contractivity_check: PASS" not in output:
            print(f"❌ TEST 5 FAIL: Missing 'contractivity_check: PASS' in output")
            print(f"Output:\n{output}")
            return False
        
        print(f"Output excerpt:")
        for line in output.split('\n'):
            if 'contractivity_check' in line:
                print(f"  {line}")
        
        # Clean up
        temp_bc_path.unlink()
        
        if result == 0:
            print(f"✅ TEST 5 PASS: Tool reports PASS for contractive system")
            return True
        else:
            print(f"❌ TEST 5 FAIL: Tool returned non-zero exit code")
            return False


def run_day_14_tests():
    """Run all Day 14 gate tests."""
    print("\n" + "=" * 70)
    print("ADR-007 DAY 14 GATE: CONTRACTIVITY CHECK VERIFICATION")
    print("=" * 70)
    print("Requirement: pirtm inspect basic.pirtm.bc | grep 'contractivity_check: PASS'\n")
    
    tests = [
        ("Contractive system", Day14GateTests.test_contractive_system),
        ("Marginally stable system", Day14GateTests.test_marginally_stable_system),
        ("Divergent system", Day14GateTests.test_divergent_system),
        ("Bytecode generation & inspection", Day14GateTests.test_bytecode_generation_and_inspection),
        ("Inspection tool output format", Day14GateTests.test_inspection_tool_output),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test_name}: Exception: {e}")
            failed += 1
    
    # Summary
    print("\n" + "=" * 70)
    if failed == 0:
        print(f"✅ GATE PASS: {passed}/{len(tests)} tests passed")
        print("=" * 70)
        return 0
    else:
        print(f"❌ GATE FAIL: {passed}/{len(tests)} tests passed ({failed} failed)")
        print("=" * 70)
        return 1


def main():
    """Main entry point."""
    return run_day_14_tests()


if __name__ == '__main__':
    sys.exit(main())
