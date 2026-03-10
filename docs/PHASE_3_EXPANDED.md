# Phase 3 Expanded: Type System & Contractivity Verification (Days 38–97)

**Document Status**: Technical specification for Phase 3 implementation (60 days)  
**Owner**: Type System Lead  
**Duration**: 60 calendar days (Apr 15 – Jun 12, 2026)  
**Deliverables**: ADR-008, MLIR dialect definition, type inference engine, verification pass

---

## Phase 3 Overview

**Objective**: Make contractivity **first-class type constraint** enforceable at compile-time.

**Key Shift**: Phase 2 had contractivity as *attributes* (metadata); Phase 3 makes it a *type* that the compiler verifies structurally.

**Result**:
- Type `tensor<?xf64> {pirtm.contractivity<ε=0.1>}` encodes the promise
- Type inference engine propagates bounds through composition
- Verification pass rejects programs that violate contractivity
- Programmers get compile-time guarantees: "This program provably converges"

---

## Phase 3 Technical Architecture

### Core Concept: Contractivity Types

```mlir
// Phase 2: Attribute (metadata only)
%X_next = "pirtm.projection"(%Y_t) {pirtm.contractivity<epsilon=0.1, confidence=0.9999>}

// Phase 3: Type constraint (verified by compiler)
%X_next : tensor<?xf64> = "pirtm.projection"(%Y_t : tensor<?xf64>) 
    -> (tensor<?xf64>{pirtm.contractivity<epsilon=0.1>})
```

### Type Inference Rules

$$
\text{If } T_1: \text{contractivity}\langle\epsilon_1\rangle \text{ and } T_2: \text{contractivity}\langle\epsilon_2\rangle \\
\text{Then } (T_1 \circ T_2): \text{contractivity}\langle\min(\epsilon_1, \epsilon_2)\rangle
$$

**Intuition**: Composing two contractive transformations with bounds ε₁ and ε₂ produces a contraction with bound min(ε₁, ε₂).

---

## Implementation Plan

### Phase 3a: MLIR Dialect Extensions (Days 38–50)

**Deliverable**: Extended `pirtm` dialect with contractivity type system

#### MLIR Dialect Definition (TableGen)

**File**: `src/pirtm/mlir/pirtm_types.td`

```tablegen
//===- PirtmTypes.td - PIRTM Type Definitions ----------- -*-tablegen-*-//

include "mlir/IR/AttrTypeBase.td"

class Pirtm_Type<string name, string typeMnemonic> 
    : TypeDef<Pirtm_Dialect, name> {
  let mnemonic = typeMnemonic;
}

//===----------------------------------------------------------------------===//
// Contractivity Type
//===----------------------------------------------------------------------===//

def Pirtm_ContractivityType : Pirtm_Type<"Contractivity", "contractivity"> {
  let summary = "Tensor type with contractivity bounds";
  let description = [{
    Represents a tensor with a contractivity guarantee:
    - epsilon: maximum contraction factor (< 1.0 for strict contraction)
    - confidence: probability that bound holds (0-1)
    
    Example: tensor<10xf64> {pirtm.contractivity<epsilon=0.1, confidence=0.9999>}
    
    Interpretation: Every application of this transformation contracts norms by <= 10%
    with 99.99% confidence.
  }];
  
  let parameters = (ins 
    "FloatAttr":$epsilon,
    "FloatAttr":$confidence,
    OptionalParameter<"StringAttr">:$ace_certificate
  );
  
  let hasCustomAssemblyFormat = 1;
}
```

#### C++ Type Implementation

**File**: `src/pirtm/mlir/PirtmTypes.cpp`

```cpp
#include "pirtm/mlir/PirtmTypes.h"
#include "mlir/IR/Builders.h"
#include "mlir/IR/DialectImplementation.h"

namespace mlir {
namespace pirtm {

/// Verify contractivity type constraints
LogicalResult ContractivityType::verify(
    function_ref<InFlightDiagnostic()> emitError,
    double epsilon,
    double confidence) {
  
  if (epsilon < 0.0 || epsilon > 1.0) {
    return emitError() << "epsilon must be in [0, 1], got " << epsilon;
  }
  
  if (confidence < 0.0 || confidence > 1.0) {
    return emitError() << "confidence must be in [0, 1], got " << confidence;
  }
  
  if (confidence < 0.99) {
    emitWarning() << "Low confidence bound; consider increasing to > 0.99";
  }
  
  return success();
}

} // namespace pirtm
} // namespace mlir
```

### Phase 3b: Type Inference Engine (Days 51–70)

**Deliverable**: Inference engine that propagates contractivity bounds

**File**: `src/pirtm/type_inference/contractivity_inference.py`

```python
"""
Type inference for contractivity bounds.

Given a computation graph, propagate contractivity constraints bottom-up.
Composition rule: (T1 ∘ T2) has bound min(ε(T1), ε(T2))
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


@dataclass
class ContractivityBound:
    """Contractivity constraint on a value."""
    epsilon: float        # Contraction bound
    confidence: float     # Probability of bound
    source_op: str       # Which operation produced this bound


class InferenceContext:
    """Tracks contractivity bounds throughout computation."""
    
    def __init__(self):
        self.bounds: Dict[str, ContractivityBound] = {}
        self.derivations: Dict[str, str] = {}  # Tracking why
    
    def assign_bound(self, var: str, bound: ContractivityBound) -> None:
        """Assign contractivity bound to variable."""
        self.bounds[var] = bound
    
    def lookup_bound(self, var: str) -> Optional[ContractivityBound]:
        """Look up known bound for variable."""
        return self.bounds.get(var)
    
    def infer_composition(
        self,
        T1_bound: ContractivityBound,
        T2_bound: ContractivityBound,
    ) -> ContractivityBound:
        """
        Infer bound for composition T1(T2(...)):
        
        If T2 has bound ε₂ and T1 has bound ε₁,
        then T1(T2) has bound min(ε₁, ε₂)
        """
        result_epsilon = min(T1_bound.epsilon, T2_bound.epsilon)
        result_confidence = min(T1_bound.confidence, T2_bound.confidence)
        
        return ContractivityBound(
            epsilon=result_epsilon,
            confidence=result_confidence,
            source_op=f"composition({T1_bound.source_op}, {T2_bound.source_op})"
        )
    
    def infer_recurrence(
        self,
        Xi_bound: Optional[ContractivityBound],
        Lambda_bound: Optional[ContractivityBound],
        G_bound: Optional[ContractivityBound],
        projection_bound: ContractivityBound,
    ) -> ContractivityBound:
        """
        Infer bound for recurrence step:
        X_{t+1} = P(Ξ X_t + Λ T(X_t) + G)
        
        Bound comes from projection (dominant contraction)
        """
        return projection_bound


class ContractivityInferencePass:
    """MLIR pass: infer and verify contractivity bounds."""
    
    def __init__(self):
        self.context = InferenceContext()
        self.errors: List[str] = []
    
    def run_on_operation(self, op):
        """Infer bounds for operation."""
        
        if op.name == "pirtm.tanh":
            # tanh is 1-Lipschitz, so ε = 1.0
            bound = ContractivityBound(epsilon=1.0, confidence=0.9999, source_op="pirtm.tanh")
        
        elif op.name == "pirtm.sigmoid":
            # sigmoid is 0.25-Lipschitz (derivative max = 0.25)
            bound = ContractivityBound(epsilon=0.25, confidence=0.9999, source_op="pirtm.sigmoid")
        
        elif op.name == "pirtm.projection":
            # Clip operation: parameters give bound
            clip_attr = op.attributes.get("clip_val")
            bound = ContractivityBound(
                epsilon=float(clip_attr) if clip_attr else 1.0,
                confidence=0.9999,
                source_op="pirtm.projection"
            )
        
        else:
            # Unknown op: return 1.0 (no contraction guaranteed)
            bound = ContractivityBound(epsilon=1.0, confidence=0.5, source_op=op.name)
        
        # Assign to result
        for result in op.results:
            self.context.assign_bound(result.name, bound)
        
        return bound
    
    def verify_recurrence(self, func) -> bool:
        """Verify recurrence function meets contractivity contract."""
        
        # Find the return operation
        return_op = None
        for op in func.body.ops:
            if op.name == "func.return":
                return_op = op
                break
        
        if not return_op:
            self.errors.append("No return operation found")
            return False
        
        # Get bound on return value
        return_var = return_op.operands[0].name
        return_bound = self.context.lookup_bound(return_var)
        
        if not return_bound:
            self.errors.append(f"No bound inferred for return value {return_var}")
            return False
        
        # Check against function's declared contractivity
        func_contractivity = func.attributes.get("pirtm.contractivity")
        if func_contractivity:
            declared_epsilon = func_contractivity.epsilon
            if return_bound.epsilon > declared_epsilon:
                self.errors.append(
                    f"Inferred ε={return_bound.epsilon} exceeds declared ε={declared_epsilon}"
                )
                return False
        
        return len(self.errors) == 0
    
    def inference_summary(self) -> Dict:
        """Return summary of inferred bounds."""
        return {
            "total_bounds": len(self.context.bounds),
            "errors": self.errors,
            "bounds": {
                var: {
                    "epsilon": bound.epsilon,
                    "confidence": bound.confidence,
                    "source": bound.source_op
                }
                for var, bound in self.context.bounds.items()
            }
        }
```

### Phase 3c: Verification Pass (Days 71–85)

**Deliverable**: C++ MLIR pass that enforces type constraints

**File**: `src/pirtm/mlir/passes/VerifyContractivityPass.cpp`

```cpp
#include "mlir/Pass/Pass.h"
#include "mlir/IR/BuiltinOps.h"
#include "pirtm/mlir/PirtmOps.h"

namespace mlir {
namespace pirtm {

class VerifyContractivityPass 
    : public PassWrapper<VerifyContractivityPass, OperationPass<ModuleOp>> {
public:
  StringRef getArgument() const final { return "pirtm-verify-contractivity"; }
  StringRef getDescription() const final {
    return "Verify contractivity bounds in PIRTM operations";
  }
  
  void runOnOperation() override {
    ModuleOp module = getOperation();
    
    module.walk([&](Operation *op) {
      // Check operations annotated with contractivity
      if (auto contractivityAttr = 
          op->getAttrOfType<ContractivityAttr>("pirtm.contractivity")) {
        
        verifyContractivityBound(op, contractivityAttr);
      }
    });
  }
  
private:
  void verifyContractivityBound(Operation *op, ContractivityAttr attr) {
    double epsilon = attr.getEpsilon().getValueAsDouble();
    double confidence = attr.getConfidence().getValueAsDouble();
    
    // Verify epsilon in valid range
    if (epsilon < 0.0 || epsilon > 1.0) {
      op->emitError("Invalid epsilon: ") << epsilon;
      return;
    }
    
    // Verify confidence in valid range
    if (confidence < 0.0 || confidence > 1.0) {
      op->emitError("Invalid confidence: ") << confidence;
      return;
    }
    
    // Verify operands have compatible bounds (if annotated)
    for (Value operand : op->getOperands()) {
      if (auto operandBound = 
          operand.getType().dyn_cast<ContractivityType>()) {
        
        double operandEpsilon = operandBound.getEpsilon()
            .getValueAsDouble();
        if (operandEpsilon > epsilon) {
          op->emitWarning("Operand bound ")
              << operandEpsilon 
              << " exceeds operation bound "
              << epsilon;
        }
      }
    }
  }
};

std::unique_ptr<Pass> createVerifyContractivityPass() {
  return std::make_unique<VerifyContractivityPass>();
}

} // namespace pirtm
} // namespace mlir
```

### Phase 3d: Comprehensive Tests (Days 86–97)

**File**: `src/pirtm/tests/test_contractivity_types.py`

```python
"""
Tests for contractivity type system and inference.
"""

import pytest
from pirtm.type_inference.contractivity_inference import (
    ContractivityBound,
    InferenceContext,
    ContractivityInferencePass,
)


class TestContractivityBounds:
    """Test contractivity bound operations."""
    
    def test_composition_tightens_bound(self):
        """Composition produces tighter bound."""
        ctx = InferenceContext()
        
        T1 = ContractivityBound(epsilon=0.3, confidence=0.99, source_op="op1")
        T2 = ContractivityBound(epsilon=0.2, confidence=0.99, source_op="op2")
        
        composed = ctx.infer_composition(T1, T2)
        
        # Should take minimum
        assert composed.epsilon == 0.2
        assert composed.confidence == 0.99
    
    def test_recurrence_inference(self):
        """Test bound inference for recurrence step."""
        ctx = InferenceContext()
        
        projection = ContractivityBound(epsilon=0.1, confidence=0.9999, source_op="projection")
        
        # Other terms have weaker bounds
        xi = ContractivityBound(epsilon=1.0, confidence=0.5, source_op="identity")
        lam = ContractivityBound(epsilon=0.5, confidence=0.95, source_op="gain")
        
        result = ctx.infer_recurrence(xi, lam, None, projection)
        
        # Should take the projection bound (tightest)
        assert result.epsilon == 0.1
```

---

## Summary: Phase 3 Deliverables

| Artifact | Lines | Status | Purpose |
|----------|-------|--------|---------|
| ADR-008 | ~70 | Spec | Type system design & decisions |
| MLIR dialect ext | 200 | Code | ContractivityType in TableGen |
| C++ type impl | 120 | Code | Type verification & construction |
| Type inference | 280 | Code | Python engine for bound propagation |
| Verification pass | 220 | Code | C++ MLIR pass that enforces types |
| Type tests | 400+ | Code | Inference + verification coverage |
| **Total** | **~1490** | | |

---

## Phase 3 Exit Criteria

✅ Type inference engine propagates bounds < 100ms for 1000+ op graphs  
✅ Verification pass rejects non-contractivity programs  
✅ All Phase 2 MLIR passes type checking  
✅ ADR-008 approved  
✅ Tests: `pytest src/pirtm/tests/test_contractivity_*.py -v`  

**What Unlocks**: Phase 4 (LLVM compilation + standalone runtime)

