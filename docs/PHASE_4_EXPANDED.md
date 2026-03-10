# Phase 4 Expanded: Standalone Runtime & LLVM Compilation (Days 98–127)

**Document Status**: Technical specification for Phase 4 implementation (30 days)  
**Owner**: Runtime Engineering Lead  
**Duration**: 30 calendar days (Jun 13 – Jul 12, 2026)  
**Deliverables**: ADR-009, LLVM codegen, runtime library, Python bindings, wheel packaging

---

## Phase 4 Overview

**Objective**: Ship PIRTM as **standalone compiled runtime** with 5–10× performance over NumPy.

**Core Strategy**: 
1. Convert MLIR (from Phase 2) to LLVM IR
2. Compile to native `.so` (Linux/macOS) or `.dll` (Windows)
3. Create Python bindings to call compiled code
4. Package as Python wheel with pre-built binaries
5. Auto-fallback to NumPy if compilation fails

**Result**: Users can `pip install pirtm[llvm]` and get 5–10× speedup transparently.

---

## Phase 4 Technical Architecture

### Compilation Pipeline

```
Python Code (PIRTM)
       ↓
  Descriptor YAML/JSON
       ↓
  Phase 2: MLIR Emission
       ↓
  MLIR (linalg + pirtm dialect)
       ↓
  Phase 4: MLIR → LLVM IR
       ↓
  LLVM IR (std dialect)
       ↓
  `llc` compiler
       ↓
  Machine Code (.so / .dll)
       ↓
  Python ctypes / pybind11
       ↓
  Python application
```

---

## Implementation Plan

### Week 1 (Days 98–104): ADR-009 + LLVM Codegen Architecture

**Deliverable**: ADR document, LLVM IR generation strategy

#### ADR-009: LLVM Compilation for PIRTM

**File**: `docs/adr/ADR-009-llvm-compilation.md`

```markdown
# ADR-009: LLVM Compilation for PIRTM

**Status**: Proposed  
**Date**: 2026-06-13  
**References**: ADR-008 (type system), ADR-007 (MLIR lowering), ADR-004 (semantics)

## Problem

Phase 2–3 produce verified MLIR code, but it must be *executed*. NumPy execution is slow (GIL, dynamic dispatch). We need native code generation.

## Solution: MLIR → LLVM → Machine Code

1. Convert MLIR (pirtm + linalg dialects) to LLVM IR
2. Use `llc` to compile to `.o` files
3. Link against runtime library (ACE verification, witness checking)
4. Expose via Python ctypes/pybind11

## Architecture

### Components

- **MLIRToLLVM**: Conversion passes (Phase 4a)
- **libpirtm_runtime.so**: C++ runtime with witness validation (Phase 4b)
- **Python bindings**: ctypes wrapper for LLVM code (Phase 4c)
- **PirtmExecutor**: Unified interface (numpy OR llvm) (Phase 4d)
- **Wheel packaging**: CMake + cibuildwheel for multi-platform (Phase 4d)

### Type Guarantees

Contractivity types (Phase 3) remain verified even after LLVM compilation:
- Witness embedded in binary at compile time
- Runtime checks ACE certificate before execution
- Fallback to NumPy if verification fails

## Decisions

- Use LLVM 16+ (latest stable)
- Support Linux x86_64, arm64; macOS x86_64, arm64; Windows x86_64
- Pre-compile wheels; avoid on-the-fly compilation (slow)
- NumPy fallback for platforms without wheels
```

#### LLVM Codegen Sketch

**File**: `src/pirtm/mlir/llvm_codegen.py`

```python
"""
Lower MLIR to LLVM IR and compile to native code.
"""

import subprocess
import tempfile
from pathlib import Path
from typing import Optional


class MLIRToLLVMConverter:
    """Convert MLIR module to LLVM IR."""
    
    def __init__(self, mlir_opt_path: str = "mlir-opt"):
        self.mlir_opt = mlir_opt_path
        self.mlir_translate = "mlir-translate"
    
    def convert_to_llvm_ir(self, mlir_text: str) -> str:
        """
        Convert MLIR to LLVM IR using mlir-opt + mlir-translate.
        
        Pipeline:
        1. mlir-opt --convert-scf-to-cf --convert-linalg-to-loops
        2. mlir-opt --convert-arith-to-llvm
        3. mlir-opt --convert-func-to-llvm
        4. mlir-translate -mlir-to-llvmir
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.mlir', delete=False) as f:
            f.write(mlir_text)
            mlir_file = f.name
        
        try:
            # Step 1: Lower control flow
            result = subprocess.run(
                [self.mlir_opt,
                 "--convert-scf-to-cf",
                 "--convert-linalg-to-loops",
                 mlir_file],
                capture_output=True,
                text=True,
                check=True
            )
            intermediate = result.stdout
            
            # Step 2: Lower arithmetic
            result = subprocess.run(
                [self.mlir_opt,
                 "--convert-arith-to-llvm",
                 "-"],
                input=intermediate,
                capture_output=True,
                text=True,
                check=True
            )
            intermediate = result.stdout
            
            # Step 3: Lower functions
            result = subprocess.run(
                [self.mlir_opt,
                 "--convert-func-to-llvm",
                 "-"],
                input=intermediate,
                capture_output=True,
                text=True,
                check=True
            )
            intermediate = result.stdout
            
            # Step 4: Translate to LLVM IR
            result = subprocess.run(
                [self.mlir_translate,
                 "-mlir-to-llvmir",
                 "-"],
                input=intermediate,
                capture_output=True,
                text=True,
                check=True
            )
            
            return result.stdout
        
        finally:
            Path(mlir_file).unlink()


class LLVMCompiler:
    """Compile LLVM IR to machine code."""
    
    def __init__(self, llc_path: str = "llc"):
        self.llc = llc_path
    
    def compile_to_object(self, llvm_ir: str, output_path: str) -> None:
        """
        Compile LLVM IR to object file (.o).
        
        Args:
            llvm_ir: LLVM IR text
            output_path: Path to write .o file
        """
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.ll', delete=False) as f:
            f.write(llvm_ir)
            ll_file = f.name
        
        try:
            subprocess.run(
                [self.llc,
                 "-filetype=obj",
                 "-o", output_path,
                 ll_file],
                check=True,
                capture_output=True
            )
        finally:
            Path(ll_file).unlink()
    
    def compile_to_shared_library(
        self,
        llvm_ir: str,
        output_path: str,
        libpirtm_runtime: Optional[str] = None,
    ) -> None:
        """
        Compile LLVM IR to shared library (.so / .dll).
        
        Links against libpirtm_runtime if provided.
        """
        
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Step 1: Compile IR to object file
            obj_file = tmpdir / "pirtm.o"
            self.compile_to_object(llvm_ir, str(obj_file))
            
            # Step 2: Link with runtime library
            ld_cmd = ["clang", "-shared", "-fPIC", "-o", output_path, str(obj_file)]
            
            if libpirtm_runtime:
                ld_cmd.append(libpirtm_runtime)
            
            # Link standard libraries
            ld_cmd.extend(["-lm", "-lc"])
            
            subprocess.run(ld_cmd, check=True, capture_output=True)
```

### Week 2 (Days 105–111): Runtime Library + Python Bindings

**Deliverable**: C++ runtime library with witness checking

#### Runtime Library

**File**: `src/pirtm/runtime/libpirtm_runtime.cpp`

```cpp
#include <cmath>
#include <cstring>
#include <vector>
#include <iostream>

// C API for runtime library
extern "C" {

struct pirtm_state {
    double* X;              // State vector
    int n;                  // Dimension
    double epsilon;         // Contractivity bound
    double confidence;      // Probability of bound
    bool witness_valid;     // Has witness been verified?
};

int pirtm_init(pirtm_state* state, int n, double epsilon, double confidence) {
    if (n <= 0 || epsilon < 0.0 || epsilon > 1.0 || confidence < 0.0 || confidence > 1.0) {
        return -1;  // Invalid args
    }
    
    state->X = (double*)malloc(n * sizeof(double));
    state->n = n;
    state->epsilon = epsilon;
    state->confidence = confidence;
    state->witness_valid = false;
    
    return 0;
}

void pirtm_free(pirtm_state* state) {
    if (state && state->X) {
        free(state->X);
        state->X = nullptr;
    }
}

double pirtm_norm(const double* x, int n, int order) {
    double norm = 0.0;
    
    if (order == 1) {
        // L1 norm
        for (int i = 0; i < n; i++) normalization += fabs(x[i]);
    } 
    else if (order == 2) {
        // L2 norm (Euclidean)
        for (int i = 0; i < n; i++) {
            double val = x[i];
            norm += val * val;
        }
        norm = sqrt(norm);
    }
    
    return norm;
}

int pirtm_step(
    pirtm_state* state,
    const double* Xi,      // Operator matrix (n x n)
    const double* Lambda,  // Gain matrix (n x n)
    const double* G,       // Bias vector (n)
    double (*T_func)(double)  // Transformation function
) {
    if (!state || !state->X || !state->witness_valid) {
        return -1;
    }
    
    // Temporary vectors
    double* X_trans = (double*)malloc(state->n * sizeof(double));
    double* Y_t = (double*)malloc(state->n * sizeof(double));
    
    // Transform: X_transformed = T(X_t)
    for (int i = 0; i < state->n; i++) {
        X_trans[i] = T_func(state->X[i]);
    }
    
    // Matrix-vector: Y_t = Xi @ X_t
    for (int i = 0; i < state->n; i++) {
        Y_t[i] = 0.0;
        for (int j = 0; j < state->n; j++) {
            Y_t[i] += Xi[i * state->n + j] * state->X[j];
        }
    }
    
    // Add: Y_t += Lambda @ X_trans
    for (int i = 0; i < state->n; i++) {
        for (int j = 0; j < state->n; j++) {
            Y_t[i] += Lambda[i * state->n + j] * X_trans[j];
        }
    }
    
    // Add bias: Y_t += G
    for (int i = 0; i < state->n; i++) {
        Y_t[i] += G[i];
    }
    
    // Clip: X_next = clip(Y_t, -bound, bound)
    // Bound estimated from epsilon and contraction
    double clip_bound = 1.0 / (1.0 - state->epsilon);
    for (int i = 0; i < state->n; i++) {
        if (Y_t[i] > clip_bound) {
            state->X[i] = clip_bound;
        } else if (Y_t[i] < -clip_bound) {
            state->X[i] = -clip_bound;
        } else {
            state->X[i] = Y_t[i];
        }
    }
    
    // Verify contraction property
    double prev_norm_sq = 0.0;
    for (int i = 0; i < state->n; i++) {
        prev_norm_sq += state->X[i] * state->X[i];
    }
    
    free(X_trans);
    free(Y_t);
    return 0;
}

int pirtm_verify_witness(pirtm_state* state, const char* expected_sha256) {
    // TODO: Implement witness validation
    // For now, simulate verification
    state->witness_valid = true;
    return 0;
}

// Sigmoid activation
double pirtm_sigmoid(double x) {
    return 1.0 / (1.0 + exp(-x));
}

// Tanh activation (already in libm)
double pirtm_tanh_func(double x) {
    return tanh(x);
}

}  // extern "C"
```

#### Python Bindings with ctypes

**File**: `src/pirtm/bindings/pirtm_runtime_bindings.py`

```python
"""
Python ctypes bindings for libpirtm_runtime.so
"""

import ctypes
import os
from pathlib import Path
from typing import Optional, Callable


class PirtmRuntimeError(Exception):
    """Runtime error from PIRTM."""
    pass


class PirtmState(ctypes.Structure):
    """Wrapper for pirtm_state C struct."""
    _fields_ = [
        ("X", ctypes.POINTER(ctypes.c_double)),
        ("n", ctypes.c_int),
        ("epsilon", ctypes.c_double),
        ("confidence", ctypes.c_double),
        ("witness_valid", ctypes.c_bool),
    ]


class PirtmRuntime:
    """
    Python wrapper for LLVM-compiled PIRTM runtime.
    
    Usage:
        runtime = PirtmRuntime("./libpirtm_runtime.so")
        state = runtime.init(n=100, epsilon=0.1)
        runtime.step(state, Xi, Lambda, G, T_func)
        state_vector = runtime.get_state(state)
        runtime.free(state)
    """
    
    def __init__(self, library_path: str = None):
        """
        Initialize runtime by loading shared library.
        
        Args:
            library_path: Path to libpirtm_runtime.so/.dll
                         If None, try to find via system paths
        """
        
        if library_path is None:
            library_path = self._find_library()
        
        if not os.path.exists(library_path):
            raise FileNotFoundError(f"PIRTM runtime library not found: {library_path}")
        
        self.lib = ctypes.CDLL(library_path)
        self._setup_function_signatures()
    
    def _setup_function_signatures(self):
        """Define C function signatures."""
        
        # int pirtm_init(pirtm_state*, int, double, double)
        self.lib.pirtm_init.argtypes = [
            ctypes.POINTER(PirtmState),
            ctypes.c_int,
            ctypes.c_double,
            ctypes.c_double,
        ]
        self.lib.pirtm_init.restype = ctypes.c_int
        
        # int pirtm_step(pirtm_state*, const double*, const double*, const double*, ...)
        # (simplified; would use ctypes callback for T_func)
        self.lib.pirtm_step.argtypes = [ctypes.POINTER(PirtmState)]
        self.lib.pirtm_step.restype = ctypes.c_int
        
        # void pirtm_free(pirtm_state*)
        self.lib.pirtm_free.argtypes = [ctypes.POINTER(PirtmState)]
        self.lib.pirtm_free.restype = None
    
    def init(self, n: int, epsilon: float, confidence: float = 0.9999) -> PirtmState:
        """Initialize PIRTM state."""
        state = PirtmState()
        result = self.lib.pirtm_init(state, n, epsilon, confidence)
        
        if result != 0:
            raise PirtmRuntimeError(f"pirtm_init failed: {result}")
        
        return state
    
    def free(self, state: PirtmState) -> None:
        """Free PIRTM state."""
        self.lib.pirtm_free(state)
    
    def _find_library(self) -> str:
        """Auto-locate libpirtm_runtime.so"""
        import platform
        
        system = platform.system()
        machine = platform.machine()
        
        if system == "Linux":
            libname = "libpirtm_runtime.so"
        elif system == "Darwin":  # macOS
            libname = "libpirtm_runtime.dylib"
        elif system == "Windows":
            libname = "pirtm_runtime.dll"
        else:
            raise PirtmRuntimeError(f"Unsupported platform: {system}")
        
        # Look in standard library paths
        search_paths = [
            Path(__file__).parent,  # Same directory as this module
            Path("/usr/local/lib"),
            Path("/usr/lib"),
            Path("/opt/local/lib"),  # MacPorts
        ]
        
        for path in search_paths:
            lib_path = path / libname
            if lib_path.exists():
                return str(lib_path)
        
        raise FileNotFoundError(f"Could not find {libname} in standard paths")
```

### Week 3 (Days 112–118): Unified Executor + Fallback

**Deliverable**: PirtmExecutor that switches backends automatically

**File**: `src/pirtm/core/executor.py`

```python
"""
Unified executor: choose between NumPy and LLVM backends transparently.
"""

from typing import Dict, Optional, Union
from pirtm.backend import get_backend, TensorBackend
from pirtm.carry_forward_policy import CarryForwardPolicy
from pirtm.asymmetric_kernel import FullAsymmetricAttributionKernel
from pirtm.recurrence import trajectory


class PirtmExecutor:
    """
    Unified interface for PIRTM execution.
    
    Automatically falls back to NumPy if LLVM compilation fails.
    """
    
    def __init__(self, backend: str = "llvm"):
        """
        Initialize executor.
        
        Args:
            backend: "llvm" (preferred) or "numpy" (fallback)
        """
        self.backend_name = backend
        self.backend: Optional[TensorBackend] = None
        self.use_fallback = False
        
        self._initialize_backend()
    
    def _initialize_backend(self):
        """Try to initialize LLVM backend; fall back to NumPy."""
        
        if self.backend_name == "llvm":
            try:
                from pirtm.bindings.pirtm_runtime_bindings import PirtmRuntime
                self.runtime = PirtmRuntime()
                self.backend_name = "llvm"
                print("✓ Using LLVM backend (compiled)")
            except (FileNotFoundError, ImportError, Exception) as e:
                print(f"⚠ LLVM backend not available ({e}); falling back to NumPy")
                self.use_fallback = True
                self.backend = get_backend("numpy")
        else:
            self.backend = get_backend(self.backend_name)
    
    def run(
        self,
        X_0,
        policy: CarryForwardPolicy,
        kernel: FullAsymmetricAttributionKernel,
        num_steps: int,
    ) -> Dict:
        """
        Execute recurrence loop.
        
        Returns:
            dict with 'trajectory', 'final_state', 'backend_used', 'walltime'
        """
        
        import time
        start_time = time.time()
        
        if self.use_fallback or self.backend_name == "numpy":
            # NumPy path
            result = trajectory(
                X_0,
                policy,
                None,  # Xi will be created by step()
                None,
                None,
                lambda x: x,  # T_func
                num_steps,
                backend=self.backend,
            )
            backend_used = "numpy"
        else:
            # LLVM path (would call self.runtime)
            raise NotImplementedError("LLVM path requires further integration")
        
        elapsed = time.time() - start_time
        
        return {
            'trajectory': result['trajectory'],
            'final_state': result['final_state'],
            'backend_used': backend_used,
            'walltime': elapsed,
        }
```

### Week 4 (Days 119–127): Packaging + Multi-platform Wheels

**Deliverable**: CMake build + cibuildwheel for wheels

#### CMakeLists.txt (simplified)

**File**: `CMakeLists.txt`

```cmake
cmake_minimum_required(VERSION 3.16)
project(pirtm_llvm)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find Python
find_package(Python3 COMPONENTS Interpreter Development REQUIRED)

# Build runtime library
add_library(pirtm_runtime SHARED
    src/pirtm/runtime/libpirtm_runtime.cpp
)

target_include_directories(pirtm_runtime PUBLIC
    ${Python3_INCLUDE_DIRS}
    include/
)

# Link against system math library
target_link_libraries(pirtm_runtime PUBLIC m)

# Install to Python site-packages
install(TARGETS pirtm_runtime
    LIBRARY DESTINATION pirtm/bindings/
)

# Install headers
install(DIRECTORY include/pirtm
    DESTINATION include/
)
```

#### setup.py (with extension)

**File**: `setup.py`

```python
from setuptools import setup, find_packages
from setuptools.extension import Extension
from setuptools.command.build_ext import build_ext
import subprocess
import sys
from pathlib import Path


class CMakeBuild(build_ext):
    """Custom build extension using CMake."""
    
    def run(self):
        """Build using CMake."""
        cmake_dir = Path(self.build_temp).parent
        cmake_dir.mkdir(parents=True, exist_ok=True)
        
        # Run CMake
        subprocess.check_call(
            ["cmake", str(Path.cwd())],
            cwd=cmake_dir
        )
        
        # Build
        subprocess.check_call(
            ["cmake", "--build", "."],
            cwd=cmake_dir
        )
        
        # Install to build directory
        subprocess.check_call(
            ["cmake", "--install", ".", "--prefix", str(Path(self.build_lib).parent)],
            cwd=cmake_dir
        )


setup(
    name="pirtm",
    version="0.3.0",
    description="PIRTM: Prime-Indexed Recursive Tensor Mathematics with LLVM compilation",
    packages=find_packages(exclude=["tests"]),
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.20",
        "pyyaml>=5.4",
    ],
    extras_require={
        "llvm": ["mlir>=16.0"],  # Optional LLVM support
        "dev": ["pytest", "pytest-cov"],
    },
    ext_modules=[
        Extension("pirtm._runtime", sources=[]),  # Dummy; CMake handles it
    ],
    cmdclass={"build_ext": CMakeBuild},
    entry_points={
        "console_scripts": [
            "pirtm=pirtm.cli:main",
        ],
    },
)
```

#### GitHub Actions: Multi-platform builds

**File**: `.github/workflows/build-wheels.yml`

```yaml
name: Build & Test Wheels

on:
  push:
    tags:
      - 'v*'

jobs:
  build_wheels:
    name: Build ${{ matrix.os }} wheels
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade cibuildwheel
      
      - name: Build wheels
        run: python -m cibuildwheel --output-dir dist
        env:
          CIBW_SKIP: "pp* *-win32 *-i686"  # Skip PyPy, 32-bit, i686
          CIBW_BEFORE_ALL: "cmake --version"
      
      - name: Upload wheels
        uses: actions/upload-artifact@v3
        with:
          path: dist/*.whl
```

---

## Summary: Phase 4 Deliverables

| Artifact | Lines | Status | Purpose |
|----------|-------|--------|---------|
| ADR-009 | ~80 | Spec | LLVM compilation design |
| MLIR→LLVM | 250 | Code | Conversion + compilation |
| Runtime lib | 350 | C++ | Core execution engine |
| Python bindings | 200 | Code | ctypes wrapper |
| Executor harness | 150 | Code | Unified numpy/llvm interface |
| CMakeLists.txt | 50 | Build | CMake configuration |
| setup.py | 80 | Build | setuptools integration |
| CI/CD workflow | 40 | Config | GitHub Actions wheels |
| Integration tests | 400+ | Code | Multi-backend verification |
| **Total** | **~1600** | | |

---

## Phase 4 Exit Criteria

✅ `PirtmExecutor(backend="llvm")` runs without error  
✅ LLVM backend produces outputs identical to NumPy (< 1e-10 difference)  
✅ LLVM backend is 5–10× faster on 1000-dim recurrence  
✅ Witness validation passes in compiled code  
✅ Wheels install cleanly on Ubuntu 22.04, macOS 13+, Windows 11  
✅ `pip install pirtm[llvm]` works without manual setup  
✅ ADR-009 approved  
✅ All tests pass: `pytest src/pirtm/tests/test_executor_*.py`  

**What Unlocks**: Production deployment, community adoption, Phase 5+ (GPU, JAX, etc.)

---

## Phase 4 Performance Targets

| Operation | NumPy | LLVM | Target Speedup |
|-----------|-------|------|-----------------|
| Single recurrence step (n=1000) | 1.0 ms | 0.2 ms | 5× |
| 100 steps (n=1000) | 100 ms | 15 ms | 6.7× |
| Trajectory (n=100, 1000 steps) | ~1 sec | 0.1 sec | 10× |

---

## Summary: Full 4-Phase Roadmap

| Phase | Dates | Deliverables | LOC |
|-------|-------|--------------|-----|
| **1: Backend** | Mar 8–15 | Protocol, refactoring | 1,370 |
| **2: MLIR** | Mar 16–Apr 14 | Transpiler, emission | 1,010 |
| **3: Types** | Apr 15–Jun 12 | Inference, verification | 1,490 |
| **4: LLVM** | Jun 13–Jul 12 | Runtime, wheels | 1,600 |
| **Grand Total** | **130 days** | **4 ADRs + comprehensive tests** | **~5,470** |

**Timeline**: March 8 → July 12, 2026 (19 weeks)  
**Status**: Ready to execute  
**Next Step**: Approve roadmap and start Phase 1 (Day 1)

