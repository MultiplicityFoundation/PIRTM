#!/usr/bin/env python3
"""
MLIR Diagnostic Verifier for PIRTM Dialect Types

Simulates: mlir-opt --verify-diagnostics pirtm-types-basic.mlir

This validator:
1. Parses the MLIR test file
2. Extracts type definitions and expected-error directives
3. Uses the PIRTM dialect verifier to validate each type
4. Reports pass/fail for each test case
"""

import sys
import re
from pathlib import Path

# Add workspace to path
sys.path.insert(0, '/workspaces/Tooling')

from pirtm.dialect.pirtm_types import (
    is_prime,
    factorize,
    VerificationError,
    create_cert,
    create_session_graph,
)


class MLIRDiagnosticLine:
    """Represents a single test case with optional expected-error directive."""
    
    def __init__(self, line_num, mlir_code, expected_error=None):
        self.line_num = line_num
        self.mlir_code = mlir_code
        self.expected_error = expected_error
        self.passed = False
        self.actual_error = None
    
    def __repr__(self):
        return f"Line {self.line_num}: {self.mlir_code[:60]}..."


def parse_mlir_test_file(filepath):
    """Parse MLIR test file and extract test cases with expected errors."""
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    test_cases = []
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for expected-error directive
        expected_error_match = re.search(r'expected-error@\+1\s*{{(.+)}}', line)
        if expected_error_match:
            expected_error = expected_error_match.group(1)
            # Next line is the actual code to test
            i += 1
            if i < len(lines):
                test_code = lines[i].strip()
                test_cases.append(MLIRDiagnosticLine(
                    line_num=i+1,
                    mlir_code=test_code,
                    expected_error=expected_error
                ))
        else:
            # Check if this is a type definition without expected error (should pass)
            if re.search(r'!pirtm\.\w+\(', line):
                test_cases.append(MLIRDiagnosticLine(
                    line_num=i+1,
                    mlir_code=line.strip(),
                    expected_error=None
                ))
        i += 1
    
    return test_cases


def extract_type_definition(mlir_code):
    """Extract PIRTM type definition from MLIR line."""
    
    match = re.search(r'!pirtm\.(\w+)\(([^)]+)\)', mlir_code)
    if not match:
        return None, None, None
    
    type_name = match.group(1)
    params_str = match.group(2)
    
    # Parse mod= value
    mod_match = re.search(r'mod=(\d+)', params_str)
    mod_value = int(mod_match.group(1)) if mod_match else None
    
    return type_name, mod_value, params_str


def verify_type(type_name, mod_value, params_str):
    """Verify a PIRTM type using the dialect verifier."""
    
    if type_name == 'cert':
        try:
            cert = create_cert(mod=mod_value)
            return True, None
        except VerificationError as e:
            return False, str(e)
    
    elif type_name == 'session_graph':
        try:
            # Check if coupling is unresolved in params
            from pirtm.dialect.pirtm_types import CouplingType
            coupling = CouplingType.UNRESOLVED if '#pirtm.unresolved_coupling' in params_str else None
            sg = create_session_graph(mod=mod_value, coupling=coupling)
            return True, None
        except VerificationError as e:
            return False, str(e)
    
    else:
        return False, f"Unknown type: {type_name}"


def run_diagnostic_verification(test_cases):
    """Run verification on all test cases and check against expected errors."""
    
    total = len(test_cases)
    passed = 0
    failed = 0
    
    for test in test_cases:
        type_name, mod_value, params = extract_type_definition(test.mlir_code)
        
        if not type_name:
            print(f"⚠️  Line {test.line_num}: Could not parse type definition")
            continue
        
        # Verify the type
        verification_passed, error_msg = verify_type(type_name, mod_value, params)
        
        if test.expected_error is None:
            # Should pass verification
            if verification_passed:
                test.passed = True
                passed += 1
                print(f"✅ Line {test.line_num:3d} PASS: {type_name}(mod={mod_value})")
            else:
                failed += 1
                print(f"❌ Line {test.line_num:3d} FAIL: Expected PASS but got error: {error_msg}")
        else:
            # Should fail with specific error
            if not verification_passed:
                # Check if error message matches expected
                if error_msg and test.expected_error in error_msg:
                    test.passed = True
                    passed += 1
                    print(f"✅ Line {test.line_num:3d} PASS: Correct error message")
                    print(f"     {error_msg}")
                else:
                    failed += 1
                    print(f"❌ Line {test.line_num:3d} FAIL: Error mismatch")
                    print(f"     Expected substring: {test.expected_error}")
                    print(f"     Actual error:       {error_msg}")
            else:
                failed += 1
                print(f"❌ Line {test.line_num:3d} FAIL: Expected error but verification passed")
    
    print("\n" + "=" * 70)
    print(f"RESULTS: {passed}/{total} tests passed")
    print("=" * 70)
    
    return passed == total


def main():
    """Main entry point: mlir-opt --verify-diagnostics simulator."""
    
    test_file = Path('/workspaces/Tooling/pirtm/tests/pirtm-types-basic.mlir')
    
    if not test_file.exists():
        print(f"Error: Test file not found: {test_file}")
        sys.exit(1)
    
    print(f"Verifying: {test_file}")
    print("Using PIRTM Dialect Type Verifiers (Python-based)\n")
    
    test_cases = parse_mlir_test_file(test_file)
    
    if not test_cases:
        print("No test cases found")
        sys.exit(1)
    
    all_passed = run_diagnostic_verification(test_cases)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
