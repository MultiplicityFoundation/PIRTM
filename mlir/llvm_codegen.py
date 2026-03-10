"""
Phase 4: LLVM Code Generation Module

Handles conversion from typed MLIR (output of Phase 3) to executable LLVM IR.

This module interfaces with mlir-opt to apply the standard MLIR-to-LLVM lowering
passes, producing .ll files that can be compiled with llc and linked against
libpirtm_runtime.

Status: Phase 4 Implementation
Related: ADR-009-llvm-compilation.md
"""

import subprocess
import tempfile
import os
from typing import Optional, Tuple, List


class LLVMCodeGenerator:
    """
    MLIR → LLVM IR code generator.
    
    Handles the conversion pipeline:
    1. Parse typed MLIR
    2. Apply lowering passes (pirtm → std → llvm)
    3. Optimize with LLVM optimizer
    4. Emit LLVM IR (.ll format)
    """
    
    def __init__(self, mlir_opt_path: Optional[str] = None, 
                 llc_path: Optional[str] = None):
        """
        Initialize code generator.
        
        Args:
            mlir_opt_path: Path to mlir-opt tool (default: search PATH)
            llc_path: Path to llc tool (default: search PATH)
        """
        self.mlir_opt_path = mlir_opt_path or "mlir-opt"
        self.llc_path = llc_path or "llc"
        self._verify_tools()
    
    def _verify_tools(self):
        """Verify that required tools are available."""
        try:
            subprocess.run(
                [self.mlir_opt_path, "--version"],
                capture_output=True,
                timeout=5,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(
                f"mlir-opt not found at {self.mlir_opt_path}. "
                f"Install LLVM/MLIR or provide path via mlir_opt_path parameter."
            ) from e
        
        try:
            subprocess.run(
                [self.llc_path, "--version"],
                capture_output=True,
                timeout=5,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(
                f"llc not found at {self.llc_path}. "
                f"Install LLVM or provide path via llc_path parameter."
            ) from e
    
    def mlir_to_llvm_ir(self, mlir_text: str, 
                        target_triple: Optional[str] = None) -> str:
        """
        Convert typed MLIR to LLVM IR.
        
        Pipeline:
        1. (Input: typed MLIR with !pirtm.contractivity types)
        2. convert-pirtm-to-std — Remove PIRTM dialect types
        3. convert-linalg-to-affine — Prepare for affine lowering
        4. affine-loop-invariant-code-motion — Optimize affine loops
        5. convert-affine-to-standard — Lower affine to std
        6. convert-standard-to-llvm — Generate LLVM IR
        7. (Output: LLVM IR in .ll format)
        
        Args:
            mlir_text: Typed MLIR string (Phase 3 output)
            target_triple: LLVM target triple (optional, e.g., "x86_64-linux-gnu")
        
        Returns:
            LLVM IR text (.ll format)
        
        Raises:
            RuntimeError: If conversion fails
        """
        # Create temp file for input MLIR
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.mlir', delete=False
        ) as f_in:
            f_in.write(mlir_text)
            input_path = f_in.name
        
        try:
            # Apply lowering passes
            passes = [
                "convert-pirtm-to-std",
                "convert-linalg-to-affine",
                "affine-loop-invariant-code-motion",
                "convert-affine-to-standard",
                "convert-standard-to-llvm",
            ]
            
            # Add target-specific passes if provided
            if target_triple:
                passes.append(f"set-llvm-module-data-layout={{target-triple={target_triple}}}")
            
            # Build mlir-opt command
            cmd = [self.mlir_opt_path]
            for pass_name in passes:
                cmd.extend([f"--{pass_name}"])
            cmd.extend([input_path])
            
            # Run mlir-opt
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=False
            )
            
            if result.returncode != 0:
                raise RuntimeError(
                    f"mlir-opt failed with code {result.returncode}:\n"
                    f"stderr: {result.stderr}\nstdout: {result.stdout}"
                )
            
            llvm_ir = result.stdout
            
            # Verify output is valid LLVM IR (sanity check)
            if not self.is_valid_llvm_ir(llvm_ir):
                raise RuntimeError("Generated LLVM IR appears invalid")
            
            return llvm_ir
        
        finally:
            os.unlink(input_path)
    
    def is_valid_llvm_ir(self, llvm_ir: str) -> bool:
        """Sanity check that output looks like valid LLVM IR."""
        # Check for key LLVM IR markers
        has_define = "define " in llvm_ir
        has_attributes = "attributes " in llvm_ir or "declare " in llvm_ir
        
        # Both should be present in a typical LLVM module
        return has_define or has_attributes
    
    def compile_to_object(self, llvm_ir: str, 
                          output_path: str,
                          opt_level: int = 3,
                          target_triple: Optional[str] = None) -> str:
        """
        Compile LLVM IR to machine code object file.
        
        Args:
            llvm_ir: LLVM IR text (.ll format)
            output_path: Path to write .o file
            opt_level: Optimization level (0-3; default 3 for -O3)
            target_triple: LLVM target triple (e.g., "x86_64-linux-gnu")
        
        Returns:
            Path to generated .o file
        
        Raises:
            RuntimeError: If compilation fails
        """
        # Create temp file for LLVM IR input
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.ll', delete=False
        ) as f_in:
            f_in.write(llvm_ir)
            input_path = f_in.name
        
        try:
            # Build llc command
            cmd = [self.llc_path, f"-O{opt_level}", "-filetype=obj"]
            
            # Set target triple if provided
            if target_triple:
                cmd.extend(["-mtriple", target_triple])
            
            # Position-independent code for linking into .so
            cmd.append("-relocation-model=pic")
            
            # Output file
            cmd.extend(["-o", output_path, input_path])
            
            # Run llc
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=60,
                check=False
            )
            
            if result.returncode != 0:
                raise RuntimeError(
                    f"llc failed with code {result.returncode}:\n"
                    f"stderr: {result.stderr}"
                )
            
            return output_path
        
        finally:
            os.unlink(input_path)
    
    def generate(self, mlir_text: str, 
                 output_dir: str = ".",
                 output_name: str = "pirtm_compiled") -> Tuple[str, str]:
        """
        Complete code generation: MLIR → LLVM IR → Object file.
        
        Args:
            mlir_text: Typed MLIR (Phase 3 output)
            output_dir: Directory for output files
            output_name: Base name for outputs (without extension)
        
        Returns:
            (llvm_ir_path, object_file_path)
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Convert MLIR to LLVM IR
        print(f"[Phase 4] Converting MLIR to LLVM IR...")
        llvm_ir = self.mlir_to_llvm_ir(mlir_text)
        
        # Save LLVM IR to file
        llvm_ir_path = os.path.join(output_dir, f"{output_name}.ll")
        with open(llvm_ir_path, 'w') as f:
            f.write(llvm_ir)
        print(f"  ✓ LLVM IR saved to {llvm_ir_path}")
        
        # Step 2: Compile to object file
        print(f"[Phase 4] Compiling to machine code...")
        object_path = os.path.join(output_dir, f"{output_name}.o")
        self.compile_to_object(llvm_ir, object_path, opt_level=3)
        print(f"  ✓ Object file saved to {object_path}")
        
        return llvm_ir_path, object_path


class LLVMLinker:
    """Link compiled object files against runtime library."""
    
    def __init__(self, clang_path: Optional[str] = None):
        """
        Initialize linker.
        
        Args:
            clang_path: Path to clang++ (default: search PATH)
        """
        self.clang_path = clang_path or "clang++"
        self._verify_tool()
    
    def _verify_tool(self):
        """Verify clang++ is available."""
        try:
            subprocess.run(
                [self.clang_path, "--version"],
                capture_output=True,
                timeout=5,
                check=True
            )
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise RuntimeError(
                f"clang++ not found at {self.clang_path}"
            ) from e
    
    def link_shared_library(self, object_files: List[str],
                           output_so: str,
                           runtime_lib_path: Optional[str] = None) -> str:
        """
        Link object files into shared library (.so).
        
        Args:
            object_files: List of .o file paths
            output_so: Path to output .so file
            runtime_lib_path: Path to libpirtm_runtime.so
        
        Returns:
            Path to generated .so file
        
        Raises:
            RuntimeError: If linking fails
        """
        # Build clang++ command
        cmd = [self.clang_path, "-shared", "-fPIC"]
        
        # Add object files
        cmd.extend(object_files)
        
        # Link against runtime library
        if runtime_lib_path:
            cmd.extend(["-L", os.path.dirname(runtime_lib_path)])
            cmd.append("-lpirtm_runtime")
        
        # Output
        cmd.extend(["-o", output_so])
        
        # Run linker
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )
        
        if result.returncode != 0:
            raise RuntimeError(
                f"Linking failed with code {result.returncode}:\n"
                f"stderr: {result.stderr}"
            )
        
        return output_so


def compile_mlir_to_binary(mlir_text: str,
                           output_dir: str = ".",
                           output_name: str = "pirtm_compiled",
                           runtime_lib_path: Optional[str] = None,
                           mlir_opt_path: Optional[str] = None,
                           llc_path: Optional[str] = None,
                           clang_path: Optional[str] = None) -> str:
    """
    Convenience function: MLIR → binary in one call.
    
    Args:
        mlir_text: Typed MLIR (Phase 3 output)
        output_dir: Directory for output files/libraries
        output_name: Base name for generated files
        runtime_lib_path: Path to libpirtm_runtime.so
        mlir_opt_path: Path to mlir-opt tool
        llc_path: Path to llc tool
        clang_path: Path to clang++ tool
    
    Returns:
        Path to generated .so file
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Code generation (MLIR → LLVM IR → .o)
    codegen = LLVMCodeGenerator(mlir_opt_path=mlir_opt_path, llc_path=llc_path)
    _, object_path = codegen.generate(
        mlir_text,
        output_dir=output_dir,
        output_name=output_name
    )
    
    # Step 2: Linking (.o → .so)
    print(f"[Phase 4] Linking shared library...")
    linker = LLVMLinker(clang_path=clang_path)
    so_path = os.path.join(output_dir, f"{output_name}.so")
    linker.link_shared_library(
        [object_path],
        so_path,
        runtime_lib_path=runtime_lib_path
    )
    print(f"  ✓ Shared library saved to {so_path}")
    
    return so_path


class CompilationError(Exception):
    """Raised when compilation fails."""
    pass
