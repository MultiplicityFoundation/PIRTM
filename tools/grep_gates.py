#!/usr/bin/env python3
"""
Grep Gate Validators for ADR-007 Day 3–7 and Day 7–14 Gates.

These validators check that code migration is complete per the grep gate
requirements in ADR-007.

Usage:
    python3 grep_gates.py gate1  # Check Day 3-7: No .prime properties
    python3 grep_gates.py gate2  # Check Day 7-14: No _prime attributes
"""

import subprocess
import re
import sys
from pathlib import Path
from typing import List, Tuple


class GrepGateValidator:
    """Validates migration using grep gates."""
    
    PIRTM_ROOT = Path("/workspaces/Tooling/pirtm")
    
    # Exclude patterns
    EXCLUDE_DIRS = {"__pycache__", ".pytest_cache", ".git"}
    EXCLUDE_PATTERNS = ["*.pyc", "*.pyo"]
    
    @classmethod
    def _get_python_files(cls) -> List[Path]:
        """Get list of all Python files in pirtm production code, excluding tools and tests."""
        py_files = []
        
        # Only check production directories
        production_dirs = [
            cls.PIRTM_ROOT / "channels",
            cls.PIRTM_ROOT / "core",
            cls.PIRTM_ROOT / "transpiler",
            cls.PIRTM_ROOT / "backend",
            cls.PIRTM_ROOT / "dialect",
        ]
        
        for prod_dir in production_dirs:
            if not prod_dir.exists():
                continue
            
            for py_file in prod_dir.rglob("*.py"):
                # Skip cache and compiled files
                if any(exclude in py_file.parts for exclude in cls.EXCLUDE_DIRS):
                    continue
                py_files.append(py_file)
        
        return sorted(py_files)
    
    @classmethod
    def gate1_check_no_prime_properties(cls) -> Tuple[bool, str]:
        """
        Gate 1 (Day 3–7): No .prime property access in live code.
        
        Checks that no Python file contains .prime property access (e.g., channel.prime)
        except in:
          - Comments marked with # COMPAT: ...
          - Shim compatibility layer (temporary)
        
        Returns:
            (passed: bool, message: str)
        """
        py_files = cls._get_python_files()
        violations = []
        
        for py_file in py_files:
            content = py_file.read_text()
            
            # Skip the shim itself (it's temporary compatibility)
            if "shim.py" in str(py_file):
                continue
            
            # Look for actual .prime property access (not just the string ".prime" in comments)
            # Patterns: .prime followed by (whitespace, operator, or line end)
            lines = content.split('\n')
            for line_no, line in enumerate(lines, 1):
                # Skip full-line comments
                if line.strip().startswith('#'):
                    continue
                
                # Skip compatibility markers
                if '# COMPAT:' in line:
                    continue
                
                # Check for .prime property access (actual code, not string literals/comments)
                # Look for patterns like: .prime[, .prime), .prime ,  .prime\n, etc.
                # But NOT in strings like ".prime nomenclature" in comments
                
                # Remove string literals and comments first to reduce false positives
                code_only = re.sub(r'#.*$', '', line)  # Remove rest-of-line comments
                
                # Search for .prime followed by non-alphanumeric (indicating property access)
                # but be more strict: look for patterns like variable.prime
                if re.search(r'\w\.prime\b', code_only) and r'".prime' not in code_only and r"'\.prime" not in code_only:
                    violations.append((py_file, line_no, line.strip()))
        
        if not violations:
            return True, "✅ GATE 1 PASS: No .prime property access found"
        
        msg = f"❌ GATE 1 FAIL: Found {len(violations)} .prime property access violations:\n"
        for py_file, line_no, line in violations[:10]:  # Show first 10
            msg += f"  {py_file}:{line_no}: {line[:80]}\n"
        if len(violations) > 10:
            msg += f"  ... and {len(violations) - 10} more\n"
        
        return False, msg
    
    @classmethod
    def gate2_check_no_prime_attributes(cls) -> Tuple[bool, str]:
        """
        Gate 2 (Day 7–14): No _prime internal attributes in live code.
        
        Checks that no Python file contains _prime attributes (e.g., obj._prime)
        except in:
          - Comments marked with # COMPAT: ...
          - Core algorithm layer transitioning (if pre-approved)
        
        Returns:
            (passed: bool, message: str)
        """
        py_files = cls._get_python_files()
        violations = []
        
        for py_file in py_files:
            content = py_file.read_text()
            
            # Skip shim
            if "shim.py" in str(py_file):
                continue
            
            lines = content.split('\n')
            for line_no, line in enumerate(lines, 1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue
                
                # Skip compatibility markers
                if '# COMPAT:' in line:
                    continue
                
                # Check for _prime attribute access (including assignment)
                if re.search(r'\b_prime\b', line):
                    violations.append((py_file, line_no, line.strip()))
        
        if not violations:
            return True, "✅ GATE 2 PASS: No _prime attributes found"
        
        msg = f"❌ GATE 2 FAIL: Found {len(violations)} _prime references:\n"
        for py_file, line_no, line in violations[:10]:
            msg += f"  {py_file}:{line_no}: {line[:80]}\n"
        if len(violations) > 10:
            msg += f"  ... and {len(violations) - 10} more\n"
        
        return False, msg
    
    @classmethod
    def check_mlir_emission(cls) -> Tuple[bool, str]:
        """
        Verify that MLIR emitter produces mod= form (no .prime).
        
        Returns:
            (passed: bool, message: str)
        """
        # Add workspace to path for imports
        import sys
        if '/workspaces/Tooling' not in sys.path:
            sys.path.insert(0, '/workspaces/Tooling')
        
        try:
            from pirtm.transpiler.mlir_emitter_canonical import PIRTMMLIREmitter, MLIREmitterConfig
            
            emitter = PIRTMMLIREmitter(
                MLIREmitterConfig(prime_index=7919, epsilon=0.12, op_norm_T=4.35)
            )
            mlir = emitter.emit_module("test_module")
            
            has_prime_property = ".prime" in mlir
            has_mod_canonical = "mod=" in mlir
            
            if has_prime_property:
                return False, f"❌ MLIR Emitter FAIL: Contains .prime property access"
            
            if not has_mod_canonical:
                return False, f"❌ MLIR Emitter FAIL: Missing mod= canonical form"
            
            mod_count = mlir.count("mod=")
            return True, f"✅ MLIR Emitter PASS: Uses {mod_count} mod= declarations (no .prime)"
        
        except Exception as e:
            return False, f"❌ MLIR Emitter ERROR: {type(e).__name__}: {e}"


def main():
    """Run specified gate check."""
    if len(sys.argv) < 2:
        print("Usage: python3 grep_gates.py <gate1|gate2|mlir|all>")
        sys.exit(1)
    
    gate = sys.argv[1].lower()
    validator = GrepGateValidator()
    
    if gate == "gate1":
        passed, msg = validator.gate1_check_no_prime_properties()
        print(msg)
        sys.exit(0 if passed else 1)
    
    elif gate == "gate2":
        passed, msg = validator.gate2_check_no_prime_attributes()
        print(msg)
        sys.exit(0 if passed else 1)
    
    elif gate == "mlir":
        passed, msg = validator.check_mlir_emission()
        print(msg)
        sys.exit(0 if passed else 1)
    
    elif gate == "all":
        print("=" * 70)
        print("GREP GATE 1: No .prime property access")
        print("=" * 70)
        passed1, msg1 = validator.gate1_check_no_prime_properties()
        print(msg1)
        
        print("\n" + "=" * 70)
        print("GREP GATE 2: No _prime attributes")
        print("=" * 70)
        passed2, msg2 = validator.gate2_check_no_prime_attributes()
        print(msg2)
        
        print("\n" + "=" * 70)
        print("MLIR Emission Check: mod= canonical form")
        print("=" * 70)
        passed3, msg3 = validator.check_mlir_emission()
        print(msg3)
        
        if passed1 and passed2 and passed3:
            print("\n" + "=" * 70)
            print("✅ ALL GATES PASSED")
            print("=" * 70)
            sys.exit(0)
        else:
            print("\n" + "=" * 70)
            print("❌ SOME GATES FAILED")
            print("=" * 70)
            sys.exit(1)
    
    else:
        print(f"Unknown gate: {gate}")
        print("Valid options: gate1, gate2, mlir, all")
        sys.exit(1)


if __name__ == "__main__":
    main()
