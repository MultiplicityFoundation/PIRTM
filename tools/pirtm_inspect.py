#!/usr/bin/env python3
"""
PIRTM Inspection Tool: pirtm inspect

Reads .pirtm.bc bytecode files and reports on contractivity verification,
module metadata, and proof information.

Spec Reference: ADR-007 Day 14 gate requirement
  pirtm inspect basic.pirtm.bc | grep "contractivity_check: PASS"

Usage:
  pirtm_inspect.py <bytecode_file>
  pirtm_inspect.py -v <bytecode_file>  # Verbose output
"""

import sys
import json
from pathlib import Path
from typing import Optional

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.pirtm_bytecode import PIRTMBytecode, ModuleMetadata


class PIRTMInspector:
    """Inspection tool for PIRTM bytecode files."""
    
    @staticmethod
    def load_bytecode(filepath: Path) -> Optional[PIRTMBytecode]:
        """Load bytecode from .pirtm.bc file."""
        try:
            return PIRTMBytecode.read_from_file(filepath)
        except Exception as e:
            print(f"Error loading bytecode: {e}", file=sys.stderr)
            return None
    
    @staticmethod
    def format_module_report(metadata: ModuleMetadata) -> str:
        """Format a module report line."""
        status = metadata.contractivity_check
        symbol = "✅" if status == "PASS" else "❌"
        return (
            f"{symbol} {metadata.name:30s} "
            f"mod={metadata.prime_index:6d} "
            f"ε={metadata.epsilon:.4f} "
            f"‖T‖={metadata.op_norm_T:.4f} "
            f"contractivity_check: {status}"
        )
    
    @staticmethod
    def inspect_file(filepath: Path, verbose: bool = False) -> int:
        """
        Inspect bytecode file and report status.
        
        Args:
            filepath: Path to .pirtm.bc file
            verbose: If True, print detailed information
        
        Returns:
            0 if all modules are contractive, 1 otherwise
        """
        bytecode = PIRTMInspector.load_bytecode(filepath)
        if bytecode is None:
            return 1
        
        print(f"PIRTM Bytecode Inspection Report")
        print(f"File: {filepath.name}")
        print()
        
        if verbose:
            print(f"Coupled via: {bytecode.coupling}")
            if bytecode.modules:
                print(f"Audit trail:")
                for entry in bytecode.audit_trail:
                    print(f"  - {entry}")
                print()
        
        print("Module Status:")
        print("─" * 90)
        
        all_pass = True
        for metadata in bytecode.modules:
            print(PIRTMInspector.format_module_report(metadata))
            if metadata.contractivity_check != "PASS":
                all_pass = False
        
        print("─" * 90)
        
        if bytecode.all_modules_contractive():
            overall = "✅ contractivity_check: PASS"
        else:
            overall = "❌ contractivity_check: FAIL"
        
        print(f"{overall}")
        
        if verbose:
            print()
            print("Proof Hashes (for audit):")
            for metadata in bytecode.modules:
                print(f"  {metadata.name}: {metadata.proof_hash}")
            
            if bytecode.modules:
                print()
                print("Margin Analysis:")
                for metadata in bytecode.modules:
                    margin = 1.0 - metadata.epsilon - metadata.op_norm_T
                    print(f"  {metadata.name}: margin = 1 - {metadata.epsilon:.4f} - {metadata.op_norm_T:.4f} = {margin:.6f}")
        
        return 0 if all_pass else 1


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="PIRTM Inspection Tool - Verify contractivity in bytecode"
    )
    parser.add_argument("bytecode_file", help="Path to .pirtm.bc bytecode file")
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print detailed diagnostics"
    )
    
    args = parser.parse_args()
    
    bytecode_file = Path(args.bytecode_file)
    if not bytecode_file.exists():
        print(f"Error: File not found: {bytecode_file}", file=sys.stderr)
        return 1
    
    return PIRTMInspector.inspect_file(bytecode_file, verbose=args.verbose)


if __name__ == '__main__':
    sys.exit(main())
