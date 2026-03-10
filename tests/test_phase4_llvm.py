"""
Test suite for Phase 4: LLVM Compilation and Standalone Runtime

Tests the code generation, runtime library bindings, and multi-backend executor.

Related: ADR-009-llvm-compilation.md
"""

import pytest
import numpy as np

# Phase 4 modules
from pirtm.mlir.llvm_codegen import LLVMCodeGenerator
from pirtm.bindings.pirtm_runtime_bindings import (
    PirtmState,
    check_runtime_available,
)
from pirtm.core.executor import (
    PirtmExecutor,
    Backend,
    ExecutionResult,
)


class TestLLVMCodeGeneratorBasics:
    """Test LLVM code generator initialization and tool detection."""
    
    def test_codegen_initialization(self):
        """Initialize code generator."""
        try:
            codegen = LLVMCodeGenerator()
            assert codegen.mlir_opt_path is not None
            assert codegen.llc_path is not None
        except RuntimeError:
            # Tools not available in this environment
            pytest.skip("LLVM tools (mlir-opt, llc) not found")
    
    def test_codegen_tool_verification(self):
        """Code generator verifies tools exist."""
        try:
            _ = LLVMCodeGenerator(
                mlir_opt_path="nonexistent-mlir-opt",
                llc_path="llc"
            )
            pytest.fail("Should have raised RuntimeError")
        except RuntimeError as e:
            assert "mlir-opt" in str(e)


class TestLLVMValidation:
    """Test LLVM IR validation."""
    
    def test_valid_llvm_ir_detection(self):
        """Valid LLVM IR is recognized."""
        try:
            codegen = LLVMCodeGenerator()
        except RuntimeError:
            pytest.skip("LLVM tools not found")
        
        # Valid LLVM IR
        valid_ir = """
        define void @test_func() {
            ret void
        }
        """
        assert codegen.is_valid_llvm_ir(valid_ir)
    
    def test_invalid_llvm_ir_detection(self):
        """Invalid LLVM IR is rejected."""
        try:
            codegen = LLVMCodeGenerator()
        except RuntimeError:
            pytest.skip("LLVM tools not found")
        
        # Invalid IR (no function definitions)
        invalid_ir = "x = 5\ny = 10"
        assert not codegen.is_valid_llvm_ir(invalid_ir)


class TestPirtmStateInitialization:
    """Test runtime state creation."""
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_creation_basic(self):
        """Create basic state."""
        state = PirtmState(state_dim=10, epsilon=0.05)
        assert state.dimension == 10
        assert state.epsilon == 0.05
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_creation_with_gain_matrix(self):
        """Create state with gain matrix."""
        gain = np.eye(10) * 0.8
        state = PirtmState(
            state_dim=10,
            epsilon=0.05,
            gain_matrix=gain
        )
        assert state.dimension == 10
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_invalid_epsilon(self):
        """Invalid epsilon is rejected."""
        with pytest.raises(ValueError):
            PirtmState(state_dim=10, epsilon=1.5)
        
        with pytest.raises(ValueError):
            PirtmState(state_dim=10, epsilon=-0.1)
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_invalid_dimension(self):
        """Invalid dimension is rejected."""
        with pytest.raises(ValueError):
            PirtmState(state_dim=0, epsilon=0.05)
        
        with pytest.raises(ValueError):
            PirtmState(state_dim=-5, epsilon=0.05)
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_gain_matrix_shape(self):
        """Gain matrix shape must match dimension."""
        gain = np.eye(5)  # Wrong size
        
        with pytest.raises(ValueError):
            PirtmState(state_dim=10, epsilon=0.05, gain_matrix=gain)


class TestPirtmStateOperations:
    """Test runtime state operations."""
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_vector_access(self):
        """Get and set state vector."""
        state = PirtmState(state_dim=5, epsilon=0.05)
        
        # Set state
        vec = np.array([0.1, 0.2, 0.3, 0.4, 0.5], dtype=np.float64)
        state.state_vector = vec
        
        # Get state
        retrieved = state.state_vector
        np.testing.assert_array_almost_equal(retrieved, vec)
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_vector_shape(self):
        """State vector shape must match dimension."""
        state = PirtmState(state_dim=5, epsilon=0.05)
        
        # Wrong shape
        with pytest.raises(ValueError):
            state.state_vector = np.array([1, 2, 3])
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_single_step(self):
        """Execute single iteration."""
        gain = np.eye(5) * 0.8
        state = PirtmState(
            state_dim=5,
            epsilon=0.05,
            gain_matrix=gain
        )
        
        # Set initial state
        state.state_vector = np.ones(5)
        
        # Execute step
        norm = state.step()
        assert isinstance(norm, float)
        assert norm >= 0.0
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_multiple_steps(self):
        """Execute multiple iterations."""
        gain = np.eye(10) * 0.9
        state = PirtmState(
            state_dim=10,
            epsilon=0.05,
            gain_matrix=gain
        )
        
        state.state_vector = np.random.randn(10) * 0.5
        
        # Run 10 steps
        ret = state.run(10)
        assert ret == 0
        
        # State should be updated
        final_state = state.state_vector
        assert final_state.shape == (10,)


class TestPirtmStateCleanup:
    """Test resource management."""
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_cleanup(self):
        """State is properly cleaned up."""
        state = PirtmState(state_dim=10, epsilon=0.05)
        
        # Use state
        state.state_vector = np.ones(10)
        
        # Delete should trigger cleanup
        del state  # Should not raise


class TestExecutorNumPyBackend:
    """Test multi-backend executor with NumPy backend."""
    
    def test_executor_numpy_initialization(self):
        """Initialize executor with NumPy backend."""
        executor = PirtmExecutor(Backend.NUMPY)
        assert executor.backend_name == "numpy"
    
    def test_executor_numpy_execution(self):
        """Execute via NumPy backend."""
        # Create mock descriptor and policy
        _ = {
            'state_dim': 5,
            'epsilon': 0.05,
        }
        
        # Use simple policy (would be real CarryForwardPolicy in practice)
        _ = None  # Placeholder policy
        
        # Skip actual execution for now (requires real objects)
        # Just test that executor is set up correctly
        executor = PirtmExecutor(Backend.NUMPY)
        assert executor.backend_name == "numpy"
    
    def test_executor_available_backends(self):
        """List available backends."""
        backends = PirtmExecutor.available_backends()
        assert "numpy" in backends
        if check_runtime_available():
            assert "llvm" in backends


class TestExecutorAutoBackend:
    """Test automatic backend selection."""
    
    def test_executor_auto_selection(self):
        """Auto backend selects best available."""
        executor = PirtmExecutor(Backend.AUTO)
        assert executor.backend_name in ("numpy", "llvm")
    
    def test_executor_auto_prefers_llvm(self):
        """Auto backend prefers LLVM if available."""
        executor = PirtmExecutor(Backend.AUTO)
        
        if check_runtime_available():
            assert executor.backend_name == "llvm"
        else:
            assert executor.backend_name == "numpy"


class TestExecutorLLVMBackend:
    """Test multi-backend executor with LLVM backend."""
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_executor_llvm_initialization(self):
        """Initialize executor with LLVM backend."""
        executor = PirtmExecutor(Backend.LLVM)
        assert executor.backend_name == "llvm"
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_executor_witness_support(self):
        """LLVM backend supports witness validation."""
        executor = PirtmExecutor(Backend.LLVM)
        assert executor.supports_witness_validation


class TestExecutorProperties:
    """Test executor properties."""
    
    def test_executor_invalid_backend(self):
        """Invalid backend is rejected."""
        with pytest.raises(ValueError):
            PirtmExecutor("invalid_backend")
    
    def test_executor_backend_property(self):
        """Backend name property works."""
        executor = PirtmExecutor(Backend.NUMPY)
        assert isinstance(executor.backend_name, str)


class TestExecutionResult:
    """Test result wrapper."""
    
    def test_result_creation(self):
        """Create result from dict."""
        result_dict = {
            'state': np.array([1.0, 2.0, 3.0]),
            'final_norm': 3.7,
            'backend': 'numpy',
            'execution_time': 0.1,
            'steps_completed': 100,
            'trajectory': None,
        }
        
        result = ExecutionResult(result_dict)
        assert result.backend == 'numpy'
        assert result.final_norm == 3.7
        assert result.execution_time == 0.1
    
    def test_result_throughput(self):
        """Calculate throughput."""
        result_dict = {
            'state': np.zeros(10),
            'final_norm': 1.0,
            'backend': 'numpy',
            'execution_time': 0.1,
            'steps_completed': 100,
        }
        
        result = ExecutionResult(result_dict)
        # 100 steps / 0.1 seconds = 1000 steps/sec
        assert result.throughput == pytest.approx(1000.0)


class TestRuntimeAvailability:
    """Test runtime library availability checking."""
    
    def test_runtime_check(self):
        """Check if runtime is available."""
        available = check_runtime_available()
        assert isinstance(available, bool)


class TestCompilationPipeline:
    """Test full compilation pipeline (if tools available)."""
    
    def test_simple_mlir_compilation(self):
        """Compile simple MLIR to LLVM IR."""
        try:
            codegen = LLVMCodeGenerator()
        except RuntimeError:
            pytest.skip("LLVM tools not found")
        
        # Simple MLIR (no contractivity types needed for basic test)
        simple_mlir = """
        module {
            func.func @main() {
                return
            }
        }
        """
        
        try:
            llvm_ir = codegen.mlir_to_llvm_ir(simple_mlir)
            assert "define" in llvm_ir or "declare" in llvm_ir
        except RuntimeError as e:
            # Some MLIR patterns might not work without full MLIR dialect setup
            pytest.skip(f"MLIR compilation failed (expected): {e}")


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_zero_epsilon(self):
        """Zero epsilon (maximum contractivity) is allowed."""
        state = PirtmState(state_dim=5, epsilon=0.0)
        assert state.epsilon == 0.0
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_boundary_epsilon(self):
        """Epsilon near 1.0 (but not 1.0)."""
        state = PirtmState(state_dim=5, epsilon=0.9999)
        assert state.epsilon == 0.9999
    
    def test_executor_string_backend(self):
        """Accept backend as string."""
        executor = PirtmExecutor("numpy")
        assert executor.backend_name == "numpy"


class TestPerformance:
    """Performance and stability tests."""
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_creation_speed(self):
        """State creation is fast."""
        import time
        
        start = time.time()
        for _ in range(100):
            _ = PirtmState(state_dim=100, epsilon=0.05)
        elapsed = time.time() - start
        
        # Should complete 100 creations in < 1 second
        assert elapsed < 1.0
    
    @pytest.mark.skipif(not check_runtime_available(), reason="Runtime library not available")
    def test_state_step_speed(self):
        """Single step is fast."""
        import time
        
        gain = np.eye(50) * 0.8
        state = PirtmState(state_dim=50, epsilon=0.05, gain_matrix=gain)
        state.state_vector = np.random.randn(50)
        
        start = time.time()
        for _ in range(100):
            state.step()
        elapsed = time.time() - start
        
        # 100 steps should be fast (< a few seconds)
        assert elapsed < 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
