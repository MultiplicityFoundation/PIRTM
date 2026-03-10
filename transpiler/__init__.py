"""
PIRTM Transpiler: Compose descriptors to verifiable code.

This module handles lowering PIRTM recurrence loops to various backends:
- MLIR (Phase 2): Compile to mlir-opt for verification
- LLVM (Phase 4): Machine code generation
- Circom (Future): zk-circuit integration

See: ADR-007-mlir-lowering.md
"""

from .mlir_lowering import (
    MLIREmitter,
    MLIRConfig,
    MLIRRoundTripValidator,
    emit_mlir_test_fixture,
)
from .cli import PirtmCLI, main

__all__ = [
    "MLIREmitter",
    "MLIRConfig",
    "MLIRRoundTripValidator",
    "emit_mlir_test_fixture",
    "PirtmCLI",
    "main",
]
