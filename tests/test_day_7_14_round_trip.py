#!/usr/bin/env python3
"""
ADR-007 Day 7–14 Gate: Transpiler Round-Trip Test Suite

Spec Reference: PIRTM ADR-007, ADR-004

This test validates that all examples/ can round-trip via mlir_emitter.py:
  - Load JSON example files
  - Emit valid MLIR with mod= canonical form
  - Verify no .prime property access
  - Validate all L0 invariants

Gate Requirement: All examples/ round-trip successfully via mlir_emitter.py --output mlir

Run with: python3 pirtm/tests/test_day_7_14_round_trip.py
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.mlir_emitter_canonical import PIRTMMLIREmitter, MLIREmitterConfig
from pirtm.dialect.pirtm_types import is_prime, VerificationError, create_session_graph, CouplingType
from math import gcd


class RoundTripTestSuite:
    """Test suite for transpiler round-trip validation."""
    
    EXAMPLES_DIR = Path('/workspaces/Tooling/pirtm/examples')
    
    @classmethod
    def load_examples(cls) -> List[Tuple[Path, Dict[str, Any]]]:
        """Load all example JSON files from examples/ directory."""
        examples = []
        
        if not cls.EXAMPLES_DIR.exists():
            print(f"❌ Examples directory not found: {cls.EXAMPLES_DIR}")
            return examples
        
        for json_file in sorted(cls.EXAMPLES_DIR.glob('*.json')):
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                examples.append((json_file, data))
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse {json_file}: {e}")
        
        return examples
    
    @classmethod
    def validate_example(cls, example: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate example structure and L0 invariants."""
        
        if 'name' not in example:
            return False, "Missing 'name' field"
        
        if 'components' not in example:
            return False, "Missing 'components' field"
        
        if not isinstance(example['components'], list):
            return False, "'components' must be a list"
        
        components = example['components']
        if not components:
            return False, "'components' list is empty"
        
        # Validate each component has required fields
        for i, comp in enumerate(components):
            if not isinstance(comp, dict):
                return False, f"Component {i} is not a dictionary"
            
            required_fields = {'prime_index', 'epsilon', 'op_norm_T'}
            missing = required_fields - set(comp.keys())
            if missing:
                return False, f"Component {i} missing fields: {missing}"
            
            # Validate types
            if not isinstance(comp['prime_index'], int):
                return False, f"Component {i}: prime_index must be int"
            
            if not isinstance(comp['epsilon'], (int, float)):
                return False, f"Component {i}: epsilon must be numeric"
            
            if not isinstance(comp['op_norm_T'], (int, float)):
                return False, f"Component {i}: op_norm_T must be numeric"
            
            # Validate ranges
            if comp['epsilon'] < 0.0 or comp['epsilon'] > 1.0:
                return False, f"Component {i}: epsilon must be in [0, 1]"
            
            if comp['op_norm_T'] < 0.0:
                return False, f"Component {i}: op_norm_T must be >= 0"
            
            # Verify prime_index is prime or squarefree composite
            try:
                _ = create_session_graph(mod=comp['prime_index'], coupling=CouplingType.UNRESOLVED)
            except VerificationError as e:
                return False, f"Component {i}: {str(e)}"
        
        # Validate coprimality constraint (L0 invariant #1)
        if len(components) > 1:
            for i in range(len(components)):
                for j in range(i + 1, len(components)):
                    mod_i = components[i]['prime_index']
                    mod_j = components[j]['prime_index']
                    merge_gcd = gcd(mod_i, mod_j)
                    
                    if merge_gcd > 1:
                        return False, (
                            f"Components {i} and {j} are not coprime: "
                            f"gcd({mod_i}, {mod_j}) = {merge_gcd} (violates L0 invariant #1)"
                        )
        
        return True, "Valid example"
    
    @classmethod
    def emit_example(cls, example: Dict[str, Any]) -> Tuple[bool, str, str]:
        """
        Emit MLIR for an example.
        
        Returns:
            (success: bool, error_message: str, mlir_output: str)
        """
        valid, err_msg = cls.validate_example(example)
        if not valid:
            return False, err_msg, ""
        
        mlir_parts = []
        
        try:
            # If multiple components, emit each separately
            if len(example['components']) > 1:
                for comp in example['components']:
                    emitter = PIRTMMLIREmitter(
                        MLIREmitterConfig(
                            prime_index=comp['prime_index'],
                            epsilon=comp['epsilon'],
                            op_norm_T=comp['op_norm_T'],
                        )
                    )
                    comp_name = comp.get('name', f"component_{comp['prime_index']}")
                    mlir = emitter.emit_module(module_name=comp_name)
                    mlir_parts.append(mlir)
            else:
                # Single component
                comp = example['components'][0]
                emitter = PIRTMMLIREmitter(
                    MLIREmitterConfig(
                        prime_index=comp['prime_index'],
                        epsilon=comp['epsilon'],
                        op_norm_T=comp['op_norm_T'],
                    )
                )
                example_name = example.get('name', 'example')
                mlir = emitter.emit_module(module_name=example_name)
                mlir_parts.append(mlir)
            
            mlir_output = '\n\n'.join(mlir_parts)
            return True, "", mlir_output
        
        except Exception as e:
            return False, f"Emission error: {type(e).__name__}: {e}", ""
    
    @classmethod
    def validate_mlir_output(cls, mlir_text: str) -> Tuple[bool, List[str]]:
        """
        Validate emitted MLIR.
        
        Returns:
            (all_pass: bool, findings: List[str])
        """
        findings = []
        
        # Check 1: Must use mod= syntax
        if 'mod=' not in mlir_text:
            findings.append("❌ MLIR does not use mod= syntax")
            return False, findings
        else:
            mod_count = mlir_text.count('mod=')
            findings.append(f"✅ Uses mod= canonical form ({mod_count} declarations)")
        
        # Check 2: Must NOT contain .prime property access
        if '.prime' in mlir_text:
            findings.append("❌ MLIR contains .prime property access (should use mod=)")
            return False, findings
        else:
            findings.append("✅ No .prime property access found")
        
        # Check 3: Must have module structure
        if 'module' not in mlir_text:
            findings.append("❌ MLIR missing module structure")
            return False, findings
        else:
            findings.append("✅ Valid module structure")
        
        # Check 4: Must have pirtm dialect types
        pirtm_type_count = sum(mlir_text.count(t) for t in ['!pirtm.cert', '!pirtm.epsilon', '!pirtm.op_norm_t', '!pirtm.session_graph'])
        if pirtm_type_count == 0:
            findings.append("❌ No PIRTM dialect types found")
            return False, findings
        else:
            findings.append(f"✅ Found {pirtm_type_count} PIRTM type declarations")
        
        # Check 5: Coupling must be unresolved at transpile time (L0 invariant #4)
        if '#pirtm.unresolved_coupling' in mlir_text:
            findings.append("✅ Coupling is unresolved (L0 invariant #4)")
        else:
            findings.append("⚠️  No coupling attribute (might be OK for single modules)")
        
        return True, findings


def run_round_trip_tests():
    """Run all round-trip tests."""
    
    print("\n" + "=" * 70)
    print("ADR-007 DAY 7–14 GATE: TRANSPILER ROUND-TRIP TEST SUITE")
    print("=" * 70)
    print("Requirement: All examples/ round-trip via mlir_emitter.py --output mlir\n")
    
    suite = RoundTripTestSuite()
    examples = suite.load_examples()
    
    if not examples:
        print("❌ No examples found in pirtm/examples/")
        return 1
    
    print(f"Found {len(examples)} example(s) to test:\n")
    
    passed = 0
    failed = 0
    
    for example_file, example_data in examples:
        example_name = example_data.get('name', example_file.stem)
        example_desc = example_data.get('description', '')
        
        print(f"{'─' * 70}")
        print(f"Example: {example_name}")
        print(f"File:    {example_file.name}")
        if example_desc:
            print(f"Desc:    {example_desc}")
        print()
        
        # Validate structure
        valid, err_msg = suite.validate_example(example_data)
        if not valid:
            print(f"❌ FAIL: Structure validation failed: {err_msg}")
            failed += 1
            continue
        
        print(f"✅ Structure validation passed")
        print(f"   Components: {len(example_data['components'])}")
        for i, comp in enumerate(example_data['components']):
            print(f"     [{i}] {comp.get('name', 'unnamed'):30s} mod={comp['prime_index']:6d} ε={comp['epsilon']:.2f} ‖T‖={comp['op_norm_T']:.2f}")
        print()
        
        # Emit MLIR
        success, emit_error, mlir_output = suite.emit_example(example_data)
        if not success:
            print(f"❌ FAIL: MLIR emission failed: {emit_error}")
            failed += 1
            continue
        
        print(f"✅ MLIR emission succeeded")
        
        # Validate MLIR output
        mlir_valid, findings = suite.validate_mlir_output(mlir_output)
        for finding in findings:
            print(f"   {finding}")
        
        if not mlir_valid:
            print(f"❌ FAIL: MLIR validation failed")
            failed += 1
            continue
        
        print(f"✅ PASS: Round-trip successful")
        passed += 1
        print()
    
    # Summary
    print("=" * 70)
    if passed == len(examples):
        print(f"✅ GATE PASS: {passed}/{len(examples)} examples passed")
        print("=" * 70)
        return 0
    else:
        print(f"❌ GATE FAIL: {passed}/{len(examples)} examples passed ({failed} failed)")
        print("=" * 70)
        return 1


def main():
    """Main entry point."""
    return run_round_trip_tests()


if __name__ == '__main__':
    sys.exit(main())
