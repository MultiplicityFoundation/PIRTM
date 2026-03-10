// PIRTM Types Basic Test Suite
// ADR-006: Dialect Type-Layer Gate (Day 0–3)
// 
// This file defines four test cases to validate type-layer verification:
//   Test 1: Prime cert (PASS)
//   Test 2: Non-prime composite cert via 7921 = 89 * 89 (FAIL)
//   Test 3: Non-squarefree cert via 49 = 7 * 7 (FAIL)
//   Test 4: Valid session graph with squarefree mod (PASS)
//
// Run with: mlir-opt --verify-diagnostics pirtm-types-basic.mlir

module {
  // ===== Test 1: Prime Cert (PASS) =====
  // Certificate with prime mod=7 should succeed verification
  %t1 = "test.op"() {type = !pirtm.cert(mod=7)} : () -> !pirtm.cert(mod=7)
  
  // ===== Test 2: Non-Prime Composite (FAIL) =====
  // Certificate with composite mod=7921 (89^2) should fail
  // expected-error@+1 {{mod=7921 is not prime (89^2)}}
  %t2 = "test.op"() {type = !pirtm.cert(mod=7921)} : () -> !pirtm.cert(mod=7921)
  
  // ===== Test 3: Non-Squarefree Composite (FAIL) =====
  // Certificate with non-squarefree mod=49 (7^2) should fail
  // expected-error@+1 {{mod=49 is not prime (7^2)}}
  %t3 = "test.op"() {type = !pirtm.cert(mod=49)} : () -> !pirtm.cert(mod=49)
  
  // ===== Test 4: Valid Session Graph (PASS) =====
  // Session graph with squarefree mod=210 (2 * 3 * 5 * 7) should succeed
  %t4 = "test.op"() {
    type = !pirtm.session_graph(mod=210, coupling=#pirtm.unresolved_coupling)
  } : () -> !pirtm.session_graph(mod=210, coupling=#pirtm.unresolved_coupling)
}
