"""
Contractivity Type Inference Engine for PIRTM.

Inference Algorithm:
  1. Forward pass (bottom-up): Assign contractivity types to operations
  2. Backward pass: Verify spectral conditions and Lipschitz bounds

See: ADR-008-contractivity-types.md
"""

import re
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional, Mapping
from enum import Enum


@dataclass
class ContractivityType:
    """Contractivity type annotation for tensor values."""
    epsilon: float
    confidence: float
    
    def __str__(self) -> str:
        return f"!pirtm.contractivity<epsilon = {self.epsilon}, confidence = {self.confidence}>"
    
    def __repr__(self) -> str:
        return f"ContractivityType(epsilon={self.epsilon}, confidence={self.confidence})"
    
    def compose(self, other: 'ContractivityType') -> 'ContractivityType':
        """
        Compose two contractivity types.
        
        Rule: ε' = min(ε₁, ε₂), δ' = δ₁ * δ₂
        
        Args:
            other: Second contractivity type
        
        Returns:
            Composed type with degraded bounds
        """
        return ContractivityType(
            epsilon=min(self.epsilon, other.epsilon),
            confidence=self.confidence * other.confidence,
        )


class OperationType(Enum):
    """Categories of operations for type inference."""
    PROJECTION = "projection"      # clip → max contractivity
    RECURRENCE = "recurrence"      # recurrence with gain matrix
    LINEAR = "linear"              # matmul, matvec (preserves type)
    NONLINEAR = "nonlinear"        # sigmoid, exp, log (loses type)
    AGGREGATION = "aggregation"    # add, multiply (combines types)
    UNKNOWN = "unknown"            # unrecognized


@dataclass
class TypedOperation:
    """Operation with inferred contractivity type."""
    name: str
    op_type: OperationType
    input_types: List[Optional[ContractivityType]]
    output_type: Optional[ContractivityType]
    attributes: Dict[str, str]
    
    def __str__(self) -> str:
        out_str = str(self.output_type) if self.output_type else "tensor<?xf64>"
        return f"{self.name}: {self.op_type.value} → {out_str}"


class ContractivityInference:
    """
    Type inference engine for contractivity bounds.
    
    Algorithm:
      1. Parse MLIR module
      2. Identify operations and their dependencies
      3. Forward pass: assign types bottom-up
      4. Backward pass: verify spectral conditions
      5. Return typed module
    """
    
    def __init__(
        self,
        epsilon: float = 0.05,
        confidence: float = 0.9999,
        spectral_radius: Optional[float] = None,
    ):
        """
        Initialize inference engine.
        
        Args:
            epsilon: Default contractivity margin
            confidence: Default confidence level
            spectral_radius: Pre-computed spectral radius of gain matrix (optional)
        """
        self.epsilon = epsilon
        self.confidence = confidence
        self.spectral_radius = spectral_radius
        
        # Inference state
        self.operations: Dict[str, TypedOperation] = {}
        self.operation_order: List[str] = []
        self.dependencies: Dict[str, List[str]] = {}
        self.inferred_types: Dict[str, Optional[ContractivityType]] = {}
    
    # ========== Public API ==========
    
    def infer_types(self, mlir_str: str) -> str:
        """
        Infer contractivity types from MLIR module.
        
        Args:
            mlir_str: MLIR module as string
        
        Returns:
            Typed MLIR module with contractivity annotations
        """
        # 1. Parse
        self._parse_mlir(mlir_str)
        
        # 2. Forward pass: assign types
        self._forward_pass()
        
        # 3. Backward pass: verify
        self._backward_pass()
        
        # 4. Rewrite MLIR with type annotations
        return self._rewrite_mlir(mlir_str)
    
    def get_operation_types(self) -> Mapping[str, ContractivityType]:
        """
        Get inferred contractivity types for all operations.
        
        Returns:
            Mapping from operation name → contractivity type
        """
        result: Dict[str, ContractivityType] = {}
        for op_name, opt in self.operations.items():
            if opt.output_type:
                result[op_name] = opt.output_type
        return result
    
    def verify_spectral_condition(self, spectral_radius: float) -> Tuple[bool, Optional[str]]:
        """
        Verify spectral radius satisfies contractivity threshold.
        
        Args:
            spectral_radius: r(Λ) pre-computed
        
        Returns:
            (is_valid, error_message)
        """
        threshold = 1.0 - self.epsilon
        
        if spectral_radius >= threshold:
            return False, (
                f"Spectral radius r(Λ)={spectral_radius:.6f} exceeds "
                f"threshold 1 - ε = {threshold:.6f}"
            )
        
        return True, None
    
    # ========== Private Methods: Parsing ==========
    
    def _parse_mlir(self, mlir_str: str) -> None:
        """Parse MLIR module and extract operation metadata."""
        lines = mlir_str.split("\n")
        
        # Regex patterns
        op_pattern = r'%(\w+)\s*=\s*"(\w+\.\w+)"\(%([^)]*)\)'
        attr_pattern = r'\{\s*([^}]+)\s*\}'
        
        for line in lines:
            match = re.search(op_pattern, line)
            if not match:
                continue
            
            result_name = match.group(1)
            op_name = match.group(2)
            inputs_str = match.group(3)
            
            # Extract inputs
            input_names = [x.strip() for x in inputs_str.split(",") if x.strip().startswith("%")]
            
            # Extract attributes
            attrs: Dict[str, str] = {}
            attr_match = re.search(attr_pattern, line)
            if attr_match:
                attr_str = attr_match.group(1)
                # Simple key-value parsing
                for pair in attr_str.split(","):
                    if "=" in pair:
                        k, v = pair.split("=", 1)
                        attrs[k.strip()] = v.strip()
            
            # Classify operation
            op_type = self._classify_operation(op_name)
            
            # Create operation record
            typed_op = TypedOperation(
                name=result_name,
                op_type=op_type,
                input_types=[None] * len(input_names),
                output_type=None,
                attributes=attrs,
            )
            
            self.operations[result_name] = typed_op
            self.operation_order.append(result_name)
            self.dependencies[result_name] = input_names
    
    def _classify_operation(self, op_name: str) -> OperationType:
        """Classify operation type for type inference."""
        if "clip" in op_name:
            return OperationType.PROJECTION
        elif "recurrence" in op_name or "aggregate" in op_name:
            return OperationType.RECURRENCE
        elif "matvec" in op_name or "matmul" in op_name:
            return OperationType.LINEAR
        elif "sigmoid" in op_name or "exp" in op_name or "log" in op_name or "tanh" in op_name:
            return OperationType.NONLINEAR
        elif "add" in op_name or "multiply" in op_name:
            return OperationType.AGGREGATION
        else:
            return OperationType.UNKNOWN
    
    # ========== Private Methods: Type Inference ==========
    
    def _forward_pass(self) -> None:
        """Forward pass: assign types bottom-up."""
        for op_name in self.operation_order:
            op = self.operations[op_name]
            
            # Get input types
            input_types: list[ContractivityType | None] = []
            for dep in self.dependencies[op_name]:
                if dep in self.inferred_types:
                    input_types.append(self.inferred_types[dep])
                else:
                    input_types.append(None)
            
            # Assign output type based on operation
            if op.op_type == OperationType.PROJECTION:
                # clip → maximum contractivity
                output_type = ContractivityType(epsilon=0.0, confidence=1.0)
            
            elif op.op_type == OperationType.RECURRENCE:
                # recurrence → inherits from epsilon/confidence
                output_type = ContractivityType(epsilon=self.epsilon, confidence=self.confidence)
            
            elif op.op_type == OperationType.LINEAR:
                # Linear map: preserve input type
                output_type = input_types[0] if input_types else None
            
            elif op.op_type == OperationType.NONLINEAR:
                # Nonlinear: loses contractivity
                output_type = None
            
            elif op.op_type == OperationType.AGGREGATION:
                # Aggregation: combine input types
                valid_types = [t for t in input_types if t is not None]
                if valid_types:
                    output_type = valid_types[0]
                    for t in valid_types[1:]:
                        output_type = output_type.compose(t)
                else:
                    output_type = None
            
            else:
                output_type = None
            
            self.inferred_types[op_name] = output_type
    
    def _backward_pass(self) -> None:
        """Backward pass: verify spectral conditions and bounds."""
        for op_name in reversed(self.operation_order):
            op = self.operations[op_name]
            
            # Verify spectral condition for recurrence/aggregation
            if op.op_type in (OperationType.RECURRENCE, OperationType.AGGREGATION):
                if self.spectral_radius is not None:
                    is_valid, error = self.verify_spectral_condition(self.spectral_radius)
                    if not is_valid:
                        print(f"⚠️  Warning in {op_name}: {error}")
    
    # ========== Private Methods: MLIR Rewriting ==========
    
    def _rewrite_mlir(self, mlir_str: str) -> str:
        """Rewrite MLIR with inferred type annotations."""
        output_lines: list[str] = []
        
        for line in mlir_str.split("\n"):
            # Check if line contains an operation with inferred type
            for op_name, inferred_type in self.inferred_types.items():
                if inferred_type and f"%{op_name}" in line and "=" in line:
                    # Inject type annotation
                    # Pattern: %name = ... -> tensor<?xf64>
                    # Rewrite to: %name = ... -> tensor<?xf64, !pirtm.contractivity<...>>
                    
                    # Find the return type
                    if "->tensor<?xf64>" in line:
                        line = line.replace(
                            "->tensor<?xf64>",
                            f"->tensor<?xf64, {inferred_type}>",
                        )
                    elif "-> tensor<?xf64>" in line:
                        line = line.replace(
                            "-> tensor<?xf64>",
                            f"-> tensor<?xf64, {inferred_type}>",
                        )
            
            output_lines.append(line)
        
        return "\n".join(output_lines)
    
    # ========== Statistics ==========
    
    def get_statistics(self) -> Dict[str, int | float | Mapping[str, ContractivityType]]:
        """Get inference statistics."""
        total_ops = len(self.operations)
        typed_ops = sum(1 for t in self.inferred_types.values() if t is not None)
        
        return {
            "total_operations": total_ops,
            "typed_operations": typed_ops,
            "untyped_operations": total_ops - typed_ops,
            "coverage": typed_ops / total_ops if total_ops > 0 else 0.0,
            "inferred_types": self.get_operation_types(),
        }


class ContractivityTypeChecker:
    """
    Type checking for contractivity constraints.
    
    Verifies that operations respect contractivity rules.
    """
    
    def __init__(self, inference: ContractivityInference):
        """Initialize with inference engine results."""
        self.inference = inference
        self.errors: List[str] = []
        self.warnings: List[str] = []
    
    def check(self) -> Tuple[bool, List[str], List[str]]:
        """
        Run type checking.
        
        Returns:
            (is_valid, errors, warnings)
        """
        # Check composition rules
        self._check_composition_bounds()
        
        # Check spectral conditions
        self._check_spectral_conditions()
        
        return len(self.errors) == 0, self.errors, self.warnings
    
    def _check_composition_bounds(self) -> None:
        """Verify composition rules weaken bounds."""
        types = self.inference.get_operation_types()
        
        # Check that epsilon never increases
        for op_name, typ in types.items():
            if typ.epsilon > self.inference.epsilon + 0.001:  # tolerance
                self.warnings.append(
                    f"{op_name}: epsilon={typ.epsilon} exceeds configured value "
                    f"epsilon={self.inference.epsilon}"
                )
    
    def _check_spectral_conditions(self) -> None:
        """Verify spectral radius conditions."""
        if self.inference.spectral_radius is None:
            return
        
        is_valid, error = self.inference.verify_spectral_condition(
            self.inference.spectral_radius
        )
        
        if not is_valid:
            self.errors.append(f"Spectral condition failed: {error}")


def infer_and_check(
    mlir_str: str,
    epsilon: float = 0.05,
    confidence: float = 0.9999,
    spectral_radius: Optional[float] = None,
) -> Tuple[str, Dict[str, int | float | Mapping[str, ContractivityType]], List[str], List[str]]:
    """
    Convenience function: infer types, check validity, return results.
    
    Args:
        mlir_str: MLIR module as string
        epsilon: Contractivity margin
        confidence: Confidence level
        spectral_radius: Pre-computed spectral radius (optional)
    
    Returns:
        (typed_mlir, stats, errors, warnings)
    """
    # Run inference
    inferencer = ContractivityInference(
        epsilon=epsilon,
        confidence=confidence,
        spectral_radius=spectral_radius,
    )
    typed_mlir = inferencer.infer_types(mlir_str)
    
    # Type check
    checker = ContractivityTypeChecker(inferencer)
    _, errors, warnings = checker.check()
    
    # Get statistics
    stats = inferencer.get_statistics()
    
    return typed_mlir, stats, errors, warnings
