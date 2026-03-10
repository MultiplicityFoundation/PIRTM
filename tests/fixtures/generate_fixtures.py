#!/usr/bin/env python3
"""Generate test fixture bytecode files for Day 14–16 gate testing."""

import sys
import json
from pathlib import Path

sys.path.insert(0, '/workspaces/Tooling')

from pirtm.transpiler.pirtm_bytecode import PIRTMBytecode, ModuleMetadata, ProofHash

# Fixture directory
FIXTURES_DIR = Path(__file__).parent
FIXTURES_DIR.mkdir(exist_ok=True)


def create_fixture_bytecode(
    name: str, prime_index: int, epsilon: float, op_norm_T: float
) -> None:
    """Create a single bytecode fixture file."""
    
    # Compute contractivity
    margin = 1.0 - epsilon - op_norm_T
    status = "PASS" if margin > 0 else "FAIL"
    
    # Compute proof hash
    proof_hash_obj = ProofHash(prime_index, epsilon, op_norm_T)
    proof_hash = proof_hash_obj.compute()
    
    # Create module metadata
    metadata = ModuleMetadata(
        name=name,
        prime_index=prime_index,
        epsilon=epsilon,
        op_norm_T=op_norm_T,
        contractivity_check=status,
        proof_hash=proof_hash,
    )
    
    # Create bytecode
    bytecode = PIRTMBytecode(
        modules=[metadata],
        coupling="#pirtm.unresolved_coupling",
        mlir_source=f'!pirtm.module(mod={prime_index}, epsilon={epsilon}, op_norm_T={op_norm_T})',
        audit_trail=[f"Created fixture: {name}"],
    )
    
    # Write fixture
    fixture_path = FIXTURES_DIR / f"{name}.pirtm.bc"
    bytecode.write_to_file(fixture_path)
    print(f"✓ {fixture_path}")


if __name__ == "__main__":
    print("Generating test fixture bytecode files...\n")
    
    # basic.pirtm.bc - Simple contractive module
    create_fixture_bytecode("basic", prime_index=7, epsilon=0.05, op_norm_T=0.90)
    
    # secondary.pirtm.bc - Smaller coupling
    create_fixture_bytecode("secondary", prime_index=11, epsilon=0.03, op_norm_T=0.80)
    
    # module_a.pirtm.bc - Another contractive module
    create_fixture_bytecode("module_a", prime_index=13, epsilon=0.02, op_norm_T=0.85)
    
    # module_unstable.pirtm.bc - Divergent module (for contrast)
    create_fixture_bytecode("module_unstable", prime_index=17, epsilon=0.2, op_norm_T=0.95)
    
    print("\nAll fixtures created successfully!")
