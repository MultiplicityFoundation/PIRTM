"""
Day 3–7 Gate: Coprime Merge Validation

Spec Reference: ADR-007, ADR-004
Gate Requirement: "Coprime merge passes; non-coprime emits the specified diagnostic"

This test validates:
  - Test 1: Merging two coprime session graphs (gcd = 1) → PASS
  - Test 2: Merging two non-coprime graphs (gcd > 1) → FAIL with diagnostic
"""

import sys
sys.path.insert(0, '/workspaces/Tooling')

from math import gcd
from pirtm.dialect.pirtm_types import (
    SessionGraphType,
    CouplingType,
    VerificationError,
    create_session_graph,
)


def merge_session_graphs(sg1: SessionGraphType, sg2: SessionGraphType) -> SessionGraphType:
    """
    Merge two session graphs.
    
    The merged graph has:
      - mod = sg1.mod * sg2.mod
      - Coprimality check: gcd(sg1.mod, sg2.mod) must be 1 (L0 invariant #1)
    
    Raises VerificationError if merge would violate L0 invariant.
    """
    merged_mod = sg1.mod * sg2.mod
    merge_gcd = gcd(sg1.mod, sg2.mod)
    
    if merge_gcd > 1:
        raise VerificationError(
            f"Cannot merge session graphs: mod={sg1.mod} and mod={sg2.mod} "
            f"are not coprime (gcd={merge_gcd}); "
            f"merged graph would have mod={merged_mod} with shared factors (L0 invariant #1)"
        )
    
    # Coprime merge succeeds
    return create_session_graph(mod=merged_mod, coupling=CouplingType.UNRESOLVED)


def test_coprime_merge():
    """Test 1: Merging coprime session graphs."""
    
    print("\n" + "=" * 70)
    print("TEST 1: COPRIME MERGE (should pass)")
    print("=" * 70)
    
    # Create two session graphs with coprime moduli
    # sg1: mod=7 (prime)
    # sg2: mod=11 (prime, different)
    # merged: mod=77, gcd(7,11)=1 → COPRIME
    
    sg1 = create_session_graph(mod=7, coupling=CouplingType.UNRESOLVED)
    sg2 = create_session_graph(mod=11, coupling=CouplingType.UNRESOLVED)
    
    print(f"sg1.mod = {sg1.mod} (prime)")
    print(f"sg2.mod = {sg2.mod} (prime)")
    print(f"gcd({sg1.mod}, {sg2.mod}) = {gcd(sg1.mod, sg2.mod)} → coprime")
    
    try:
        merged = merge_session_graphs(sg1, sg2)
        print(f"✅ PASS: Merged graph has mod={merged.mod}")
        return True
    except VerificationError as e:
        print(f"❌ FAIL: Merge rejected with error: {e}")
        return False


def test_non_coprime_merge():
    """Test 2: Merging non-coprime session graphs."""
    
    print("\n" + "=" * 70)
    print("TEST 2: NON-COPRIME MERGE (should fail with diagnostic)")
    print("=" * 70)
    
    # Create two session graphs with non-coprime moduli
    # sg1: mod=6 (2*3, squarefree)
    # sg2: mod=10 (2*5, squarefree)
    # gcd(6,10)=2 → NOT COPRIME
    
    sg1 = create_session_graph(mod=6, coupling=CouplingType.UNRESOLVED)
    sg2 = create_session_graph(mod=10, coupling=CouplingType.UNRESOLVED)
    
    print(f"sg1.mod = {sg1.mod} (product 2*3, squarefree)")
    print(f"sg2.mod = {sg2.mod} (product 2*5, squarefree)")
    merge_gcd = gcd(sg1.mod, sg2.mod)
    print(f"gcd({sg1.mod}, {sg2.mod}) = {merge_gcd} → NOT coprime")
    
    try:
        merged = merge_session_graphs(sg1, sg2)
        print(f"❌ FAIL: Merge should have been rejected but succeeded with mod={merged.mod}")
        return False
    except VerificationError as e:
        error_msg = str(e)
        # Check diagnostic contains key information
        required_parts = [
            "Cannot merge",
            "not coprime",
            f"gcd={merge_gcd}",
            "L0 invariant #1",
        ]
        
        all_found = all(part in error_msg for part in required_parts)
        
        if all_found:
            print(f"✅ PASS: Correct error diagnostic emitted")
            print(f"   {error_msg}")
            return True
        else:
            print(f"❌ FAIL: Error message missing required components")
            print(f"   Expected to contain: {required_parts}")
            print(f"   Actual: {error_msg}")
            return False


def main():
    """Run Day 3–7 gate tests."""
    
    print("\n" + "=" * 70)
    print("ADR-007 DAY 3–7 GATE: COPRIME MERGE VALIDATION")
    print("=" * 70)
    print("Spec Reference: ADR-004 L0 Invariant #1 (coprimality)")
    
    test1_pass = test_coprime_merge()
    test2_pass = test_non_coprime_merge()
    
    # Summary
    print("\n" + "=" * 70)
    if test1_pass and test2_pass:
        print("RESULTS: ✅ DAY 3–7 GATE PASSED (2/2 tests)")
        print("=" * 70)
        return 0
    else:
        print("RESULTS: ❌ DAY 3–7 GATE FAILED")
        print("=" * 70)
        return 1


if __name__ == '__main__':
    sys.exit(main())
