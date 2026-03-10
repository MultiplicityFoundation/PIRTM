# Phase 2 Expanded: MLIR Emission & Transpiler Integration (Days 8–37)

**Document Status**: Technical specification for Phase 2 implementation (30 days)  
**Owner**: Transpiler Team Lead  
**Duration**: 30 calendar days (Mar 16 – Apr 14, 2026)  
**Deliverables**: ADR-007, MLIREmitter, transpiler CLI integration, verification tests

---

## Phase 2 Overview

**Objective**: Compile PIRTM recurrence loops to verifiable MLIR code with embedded contractivity bounds.

**Core Idea**: Take the abstract recurrence loop definition (JSON/YAML descriptor) and lower it to MLIR `linalg` dialect, encoding contractivity proofs as first-class attributes that the type system can reason about (Phase 3).

**Result**: `pirtm transpile --output mlir` produces `.mlir` files that:
1. Compile cleanly with `mlir-opt --verify-diagnostics`
2. Contain `contractivity` attributes with epsilon bounds
3. Carry ACE certificate witnesses as metadata
4. Enable Phase 3 (type system) to enforce contractivity at compile-time

---

## Phase 2 Technical Architecture

### Input: Computation Descriptor

```yaml
# examples/recurrence_descriptor.yaml
kind: Computation
metadata:
  name: "pirtm_recurrence"
  description: "Basic PIRTM contraction loop"
spec:
  recurrence:
    formula: "X_{t+1} = P(Ξ X_t + Λ T(X_t) + G)"
    parameters:
      beta: 1.5
      lambda_decay: 0.8
      convergence_mode: "steady_state"
  kernel:
    type: "sigmoid"  # tanh, sigmoid, softmax, exponential, power
    stability:
      gradient_clip: 10.0
      underflow_threshold: 1e-30
  certification:
    target_epsilon: 0.1  # Contractivity bound
    confidence: 0.9999
    ace_certificate: "sha256:abc123..."
```

### Output: MLIR Code

```mlir
module {
  // PIRTM recurrence as MLIR
  func.func @pirtm_recurrence(
    %X_t: tensor<?xf64>,
    %Xi: tensor<?x?xf64>,
    %Lambda: tensor<?x?xf64>,
    %G: tensor<?xf64>
  ) -> (tensor<?xf64> {pirtm.contractivity<epsilon = 0.1, confidence = 0.9999>}) {
    
    // Transform: T(X_t) = sigmoid(X_t)
    %X_transformed = "pirtm.sigmoid"(%X_t) : (tensor<?xf64>) -> tensor<?xf64>
    
    // Y_t = Ξ X_t + Λ T(X_t) + G
    %term1 = "linalg.matvec"(%Xi, %X_t) : ... -> tensor<?xf64>
    %term2 = "linalg.matvec"(%Lambda, %X_transformed) : ... -> tensor<?xf64>
    %Y_t = arith.addf %term1, %term2 : tensor<?xf64>
    %Y_t_plus_G = arith.addf %Y_t, %G : tensor<?xf64>
    
    // Projection: P(Y_t) = clip(Y_t, -clip_val, clip_val)
    %X_next = "pirtm.projection"(%Y_t_plus_G) : ... -> 
      tensor<?xf64> {pirtm.contractivity<epsilon = 0.1, confidence = 0.9999>}
    
    return %X_next : tensor<?xf64>
  }
}
```

---

## Milestones & Breakdown

### Week 1 (Days 8–14): ADR-007 + Lowering Architecture

**Deliverables**: ADR document, MLIR dialect specification, lowering plan

#### ADR-007: MLIR Lowering & Contractivity Attributes

**Key Decisions**:
1. Use `pirtm` custom dialect for contractivity semantics
2. Standard dialects (`std`, `linalg`, `arith`) for computation
3. Contractivity bounds as `Attribute` (not Type) — enables Phase 3 type inference
4. Witness encoding as double-hash (SHA256 + Poseidon)

**File**: `docs/adr/ADR-007-mlir-lowering.md` (~60 lines)

```markdown
# ADR-007: MLIR Lowering & Contractivity Attributes

**Status**: Proposed  
**Date**: 2026-03-16  
**References**: ADR-004 (type semantics), ADR-006 (backend abstraction)

## Problem

PIRTM recurrence loops must be compilable to MLIR for verification and LLVM execution. Contractivity bounds (the core L0 invariant from ADR-004) must be:
- Embedded in the IR itself, not just assertions
- Verifiable by passes (Phase 3)
- Preserved through compilation

## Solution: Contractivity as IR Attribute

Define `pirtm.contractivity<epsilon, confidence>` as an MLIR Attribute:

```mlir
%X_next = "pirtm.something"(%X_t) {pirtm.contractivity<epsilon = 0.1, confidence = 0.9999>}
```

This encodes the contractivity promise directly in the IR, enabling:
1. Passes to reason about bounds compositionally
2. Witnesses to be encoded as metadata
3. Compile-time verification (Phase 3)

## Decisions

- Use custom MLIR dialect `pirtm` with standard operations
- Lower recurrence to `std` + `linalg` + `pirtm` ops
- Contractivity as attribute, not type (reserves types for Phase 3 type system)
- Witness encoding: SHA256 (speed) + Poseidon (ZK-compatible)

## Risks & Mitigations

- MLIR dialect definition is complex → Use LLVM's TableGen framework
- Phase 3 must parse these attributes → Design validation pass early
```

#### MLIR Dialect Definition Sketch

**File**: `src/pirtm/mlir/pirtm_dialect.td` (TableGen definition)

```tablegen
//===- PirtmDialect.td - PIRTM MLIR Dialect Definition -------- -*-tablegen-*-//

include "mlir/IR/OpBase.td"

def Pirtm_Dialect : Dialect {
  let name = "pirtm";
  let description = [{
    The PIRTM dialect encodes Prime-Indexed Recursive Tensor Mathematical operations
    with verifiable contractivity bounds. See ADR-007.
  }];
  let cppNamespace = "::mlir::pirtm";
}

//===----------------------------------------------------------------------===//
// PIRTM Attributes
//===----------------------------------------------------------------------===//

class Pirtm_Attr<string name> : AttrDef<Pirtm_Dialect, name> {
  let mnemonic = "contractivity";
}

def Pirtm_ContractivityAttr : Pirtm_Attr<"Contractivity"> {
  let description = [{
    Encodes contractivity bounds on a tensor operation.
    
    !pirtm.contractivity<epsilon = 0.1, confidence = 0.9999>
  }];
  let parameters = (ins "FloatAttr":$epsilon, "FloatAttr":$confidence);
  let assemblyFormat = "`<` `epsilon` `=` $epsilon `,` `confidence` `=` $confidence `>`";
}

//===----------------------------------------------------------------------===//
// PIRTM Operations
//===----------------------------------------------------------------------===//

class Pirtm_Op<string mnemonic, list<Trait> traits = []>
    : Op<Pirtm_Dialect, mnemonic, traits>;

def Pirtm_RecurrenceOp : Pirtm_Op<"recurrence"> {
  let arguments = (ins
    AnyTensor:$X_t,
    AnyTensor:$Xi,
    AnyTensor:$Lambda,
    AnyTensor:$G,
    OptionalAttr<Pirtm_ContractivityAttr>:$contractivity
  );
  let results = (outs AnyTensor:$X_next);
}

def Pirtm_ProjectionOp : Pirtm_Op<"projection"> {
  let arguments = (ins
    AnyTensor:$Y_t,
    F64Attr:$clip_val,
    OptionalAttr<Pirtm_ContractivityAttr>:$contractivity
  );
  let results = (outs AnyTensor:$result);
}

def Pirtm_SigmoidOp : Pirtm_Op<"sigmoid"> {
  let arguments = (ins AnyTensor:$input);
  let results = (outs AnyTensor:$output);
}

def Pirtm_TanhOp : Pirtm_Op<"tanh"> {
  let arguments = (ins AnyTensor:$input);
  let results = (outs AnyTensor:$output);
}
```

### Week 2–3 (Days 15–28): MLIREmitter Implementation

**Deliverables**: MLIREmitter class, transpiler CLI extension, round-trip tests

#### MLIREmitter Class Sketch

**File**: `src/pirtm/transpiler/mlir_lowering.py` (~400 lines)

```python
"""
Lower PIRTM recurrence and certification to MLIR.
Spec: ADR-007 (MLIR lowering policy)
"""

from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import json
from pirtm.carry_forward_policy import CarryForwardPolicy
from pirtm.asymmetric_kernel import FullAsymmetricAttributionKernel, KernelType


@dataclass
class ContractivityBound:
    """Contractivity attribute data."""
    epsilon: float
    confidence: float
    ace_certificate_hash: str = ""
    
    def to_mlir_attr(self) -> str:
        """Emit MLIR syntax: pirtm.contractivity<epsilon=..., confidence=...>"""
        return f'pirtm.contractivity<epsilon = {self.epsilon}, confidence = {self.confidence}>'


class MLIRModule:
    """In-memory MLIR module representation."""
    
    def __init__(self, name: str = "pirtm_module"):
        self.name = name
        self.functions: Dict[str, MLIRFunction] = {}
        self.imports: List[str] = []
    
    def add_function(self, func: 'MLIRFunction') -> None:
        """Add a function to the module."""
        self.functions[func.name] = func
    
    def emit(self) -> str:
        """Generate MLIR text format."""
        lines = ["module {"]
        
        for func in self.functions.values():
            lines.append(func.emit())
        
        lines.append("}")
        return "\n".join(lines)
    
    def to_file(self, path: str) -> None:
        """Write MLIR to file."""
        with open(path, 'w') as f:
            f.write(self.emit())


class MLIRFunction:
    """Represents an MLIR function."""
    
    def __init__(self, name: str, args: List[Tuple[str, str]], return_type: str):
        self.name = name
        self.args = args  # List of (name, type) pairs
        self.return_type = return_type
        self.blocks: List[str] = []
        self.contractivity_attr: Optional[ContractivityBound] = None
    
    def add_block(self, block_ir: str) -> None:
        """Add IR block (operations)."""
        self.blocks.append(block_ir)
    
    def set_contractivity(self, bound: ContractivityBound) -> None:
        """Set contractivity attribute on function result."""
        self.contractivity_attr = bound
    
    def emit(self) -> str:
        """Generate function MLIR."""
        # Build signature
        arg_strs = [f"%{name}: {ty}" for name, ty in self.args]
        sig = f"func.func @{self.name}({', '.join(arg_strs)}) -> ({self.return_type}"
        
        if self.contractivity_attr:
            attr_str = "{" + self.contractivity_attr.to_mlir_attr() + "}"
            sig += f" {attr_str}"
        
        sig += ") {{"
        
        # Body
        body = "\n    ".join(self.blocks)
        return f"{sig}\n    {body}\n  }}"


class MLIREmitter:
    """
    Emit MLIR code from PIRTM computation descriptors.
    
    Usage:
        descriptor = load_yaml("recurrence.yaml")
        emitter = MLIREmitter()
        mlir_module = emitter.emit_recurrence(
            policy=policy,
            kernel=kernel,
            num_steps=10,
            contractivity_epsilon=0.1
        )
        mlir_module.to_file("output.mlir")
    """
    
    def __init__(self):
        self.module = MLIRModule()
        self.counter = 0
    
    def _unique_var(self, prefix: str = "v") -> str:
        """Generate unique variable name."""
        self.counter += 1
        return f"%{prefix}_{self.counter}"
    
    def emit_recurrence(
        self,
        policy: CarryForwardPolicy,
        kernel: FullAsymmetricAttributionKernel,
        num_steps: int = 1,
        contractivity_epsilon: float = 0.1,
        confidence: float = 0.9999,
    ) -> MLIRModule:
        """
        Emit MLIR for recurrence loop.
        
        Generates: func @pirtm_recurrence(...) -> tensor with contractivity attribute
        """
        
        # Create function
        args = [
            ("X_t", "tensor<?xf64>"),
            ("Xi", "tensor<?x?xf64>"),
            ("Lambda", "tensor<?x?xf64>"),
            ("G", "tensor<?xf64>"),
        ]
        func = MLIRFunction("pirtm_recurrence", args, "tensor<?xf64>")
        
        # Build recurrence IR
        ir_lines = []
        
        # Step 1: Kernel application (e.g., sigmoid)
        kernel_name = kernel.kernel_type.value  # "sigmoid", "tanh", etc.
        sig_op = self._unique_var("X_transformed")
        ir_lines.append(
            f'{sig_op} = "pirtm.{kernel_name}"(%X_t) : '
            f'(tensor<?xf64>) -> tensor<?xf64>'
        )
        
        # Step 2: Matrix-vector products
        term1 = self._unique_var("term1")
        ir_lines.append(
            f'{term1} = "linalg.matvec"(%Xi, %X_t) : '
            f'(tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>'
        )
        
        term2 = self._unique_var("term2")
        ir_lines.append(
            f'{term2} = "linalg.matvec"(%Lambda, {sig_op}) : '
            f'(tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>'
        )
        
        # Step 3: Addition
        sum12 = self._unique_var("sum")
        ir_lines.append(f'{sum12} = arith.addf {term1}, {term2} : tensor<?xf64>')
        
        Y_t = self._unique_var("Y_t")
        ir_lines.append(f'{Y_t} = arith.addf {sum12}, %G : tensor<?xf64>')
        
        # Step 4: Projection (clipping)
        clip_val = policy.max_surplus_clip
        X_next = self._unique_var("X_next")
        ir_lines.append(
            f'{X_next} = "pirtm.projection"({Y_t} : tensor<?xf64>, '
            f'clip_val={clip_val} : f64) -> tensor<?xf64>'
        )
        
        # Step 5: Return
        ir_lines.append(f"return {X_next} : tensor<?xf64>")
        
        for line in ir_lines:
            func.add_block(line)
        
        # Add contractivity attribute
        bound = ContractivityBound(
            epsilon=contractivity_epsilon,
            confidence=confidence,
        )
        func.set_contractivity(bound)
        
        self.module.add_function(func)
        return self.module
    
    def emit_witness_metadata(
        self,
        ace_certificate: str,
        poseidon_hash: str,
    ) -> str:
        """
        Emit metadata comment with witness hashes.
        
        Example:
            // Witness: ACE certificate
            // SHA256: abc123...
            // Poseidon: def456...
        """
        lines = [
            "// ===== Witness Information =====",
            f"// ACE Certificate: {ace_certificate}",
            f"// Poseidon Hash: {poseidon_hash}",
        ]
        return "\n".join(lines)
```

#### Transpiler CLI Extension

**File**: `src/pirtm/transpiler/cli.py` (modifications)

```python
"""
CLI extensions for Phase 2: MLIR emission.
"""

import argparse
import json
import yaml
from pathlib import Path
from pirtm.transpiler.mlir_lowering import MLIREmitter
from pirtm.carry_forward_policy import StandardCarryForwardPolicy
from pirtm.asymmetric_kernel import FullAsymmetricAttributionKernel, KernelType


def add_mlir_command(subparsers):
    """Add 'pirtm transpile --output mlir' command."""
    
    mlir_parser = subparsers.add_parser(
        'transpile',
        help='Transpile PIRTM computation to MLIR',
    )
    
    mlir_parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input descriptor file (JSON or YAML)',
    )
    
    mlir_parser.add_argument(
        '--output',
        choices=['mlir', 'llvm', 'c'],
        default='mlir',
        help='Output format (default: mlir)',
    )
    
    mlir_parser.add_argument(
        '--mlir-dialect',
        choices=['std+pirtm', 'linalg', 'full'],
        default='std+pirtm',
        help='MLIR dialect subset to use',
    )
    
    mlir_parser.add_argument(
        '--emit-contractivity',
        action='store_true',
        help='Embed contractivity bounds as attributes (required for Phase 3)',
    )
    
    mlir_parser.add_argument(
        '--witness-format',
        choices=['sha256', 'poseidon', 'dual'],
        default='dual',
        help='Witness hash format',
    )
    
    mlir_parser.add_argument(
        '--outfile',
        type=str,
        help='Output file (default: stdout)',
    )
    
    mlir_parser.set_defaults(func=handle_transpile)


def handle_transpile(args):
    """Execute 'pirtm transpile' command."""
    
    # Load descriptor
    descriptor_path = Path(args.input)
    if not descriptor_path.exists():
        raise FileNotFoundError(f"Descriptor not found: {args.input}")
    
    with open(descriptor_path) as f:
        if descriptor_path.suffix == '.yaml':
            descriptor = yaml.safe_load(f)
        else:
            descriptor = json.load(f)
    
    # Extract parameters
    spec = descriptor.get('spec', {})
    recurrence = spec.get('recurrence', {})
    kernel_spec = spec.get('kernel', {})
    cert = spec.get('certification', {})
    
    # Create policy
    policy = StandardCarryForwardPolicy(
        beta=recurrence.get('parameters', {}).get('beta', 1.5),
        lambda_decay=recurrence.get('parameters', {}).get('lambda_decay', 0.8),
        convergence_mode=recurrence.get('parameters', {}).get('convergence_mode', 'steady_state'),
    )
    
    # Create kernel
    kernel_type_str = kernel_spec.get('type', 'sigmoid')
    kernel = FullAsymmetricAttributionKernel(
        beta=policy.beta,
        kernel_type=KernelType(kernel_type_str),
    )
    
    # Emit MLIR
    emitter = MLIREmitter()
    module = emitter.emit_recurrence(
        policy=policy,
        kernel=kernel,
        num_steps=1,
        contractivity_epsilon=cert.get('target_epsilon', 0.1),
        confidence=cert.get('confidence', 0.9999),
    )
    
    # Output
    mlir_text = module.emit()
    
    if args.emit_contractivity:
        # Prepend witness metadata
        witness = emitter.emit_witness_metadata(
            ace_certificate=cert.get('ace_certificate', 'unknown'),
            poseidon_hash=cert.get('witness_hash', 'unknown'),
        )
        mlir_text = witness + "\n\n" + mlir_text
    
    if args.outfile:
        with open(args.outfile, 'w') as f:
            f.write(mlir_text)
        print(f"Wrote MLIR to {args.outfile}")
    else:
        print(mlir_text)
```

### Week 4 (Days 29–37): Verification & Integration

**Deliverables**: Verification tests, documentation, CI integration

#### Tests: `src/pirtm/tests/test_mlir_verification.py`

```python
"""
MLIR verification tests: round-trip + witness validation.
"""

import pytest
import tempfile
from pathlib import Path
from pirtm.transpiler.mlir_lowering import MLIREmitter, ContractivityBound
from pirtm.carry_forward_policy import StandardCarryForwardPolicy
from pirtm.asymmetric_kernel import FullAsymmetricAttributionKernel, KernelType


class TestMLIREmission:
    """Test MLIR code generation."""
    
    def test_emit_recurrence(self):
        """Test basic recurrence emission."""
        policy = StandardCarryForwardPolicy(beta=1.5)
        kernel = FullAsymmetricAttributionKernel(
            beta=1.5,
            kernel_type=KernelType.SIGMOID
        )
        
        emitter = MLIREmitter()
        module = emitter.emit_recurrence(
            policy=policy,
            kernel=kernel,
            contractivity_epsilon=0.1,
            confidence=0.9999,
        )
        
        mlir_text = module.emit()
        
        # Verify structure
        assert "module {" in mlir_text
        assert "func.func @pirtm_recurrence" in mlir_text
        assert "return" in mlir_text
    
    def test_contractivity_attribute(self):
        """Test that contractivity bounds are emitted."""
        policy = StandardCarryForwardPolicy(beta=1.5)
        kernel = FullAsymmetricAttributionKernel(
            beta=1.5,
            kernel_type=KernelType.TANH
        )
        
        emitter = MLIREmitter()
        module = emitter.emit_recurrence(
            policy=policy,
            kernel=kernel,
            contractivity_epsilon=0.15,
            confidence=0.999,
        )
        
        mlir_text = module.emit()
        
        # Verify attribute in output
        assert "pirtm.contractivity" in mlir_text
        assert "epsilon = 0.15" in mlir_text
        assert "confidence = 0.999" in mlir_text
    
    def test_mlir_parses(self):
        """Test that emitted MLIR is syntactically valid."""
        # This would require calling mlir-opt; for now, just check structure
        policy = StandardCarryForwardPolicy()
        kernel = FullAsymmetricAttributionKernel(beta=1.5)
        
        emitter = MLIREmitter()
        module = emitter.emit_recurrence(policy, kernel)
        mlir_text = module.emit()
        
        # Basic syntax checks
        assert mlir_text.count("func.func") == 1
        assert mlir_text.count("module {") == 1
        assert mlir_text.count("}") >= 2
```

---

## Summary: Phase 2 Deliverables

| Artifact | Lines | Status | Purpose |
|----------|-------|--------|---------|
| ADR-007 | ~60 | Spec | MLIR design & contractivity attribute decisions |
| MLIREmitter | 400 | Code | Core lowering logic |
| Transpiler CLI | 80 | Code | `pirtm transpile --output mlir` command |
| MLIR dialect def | 120 | Code | TableGen PIRTM dialect |
| Verification tests | 300+ | Code | Round-trip + witness validation |
| Examples | 50+ | Docs | YAML descriptors + expected MLIR output |
| **Total** | **~1010** | | |

---

## Phase 2 Exit Criteria

✅ `pirtm transpile --output mlir` produces valid MLIR  
✅ `mlir-opt --verify-diagnostics` passes (no errors)  
✅ Contractivity bounds appear as attributes  
✅ Witness hashes encoded in metadata  
✅ Round-trip tests pass (descriptor → MLIR → back)  
✅ ADR-007 approved with team sign-off  
✅ All tests pass: `pytest src/pirtm/tests/test_mlir_*.py`  

**What Unlocks**: Phase 3 (type system + verification pass)

