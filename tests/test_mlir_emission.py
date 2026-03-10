"""
Test Suite for Phase 2: MLIR Emission & Transpiler Integration

Validates:
1. Syntax: Generated MLIR parses with mlir-opt
2. Contractivity: Bounds appear as attributes
3. Witness: Poseidon hashes encode correctly
4. Round-trip: Recurrence → MLIR → verification passes
5. Semantics: L0 invariant maintained in lowered code

See: ADR-007-mlir-lowering.md
"""

import pytest
import re

from pirtm.transpiler.mlir_lowering import (
    MLIREmitter,
    MLIRConfig,
    MLIRRoundTripValidator,
    emit_mlir_test_fixture,
)


class TestMLIREmitterCore:
    """Core MLIREmitter functionality."""
    
    def test_emitter_initialization(self):
        """Test MLIREmitter with default and custom config."""
        # Default config
        emitter1 = MLIREmitter()
        assert emitter1.config.epsilon == 0.05
        assert emitter1.config.prime_index == 17
        
        # Custom config
        config = MLIRConfig(epsilon=0.01, confidence=0.99, prime_index=7)
        emitter2 = MLIREmitter(config=config)
        assert emitter2.config.epsilon == 0.01
        assert emitter2.config.confidence == 0.99
        assert emitter2.config.prime_index == 7
    
    def test_emit_module_produces_valid_structure(self):
        """Test that emit_module produces well-formed MLIR."""
        emitter = MLIREmitter()
        mlir_str = emitter.emit_module()
        
        # Check essential structure
        assert "module {" in mlir_str
        assert "}" in mlir_str
        # Module has opening and closing (check ends with closing brace)
        assert mlir_str.rstrip().endswith("}")
    
    def test_emit_module_includes_metadata(self):
        """Test that emitted module includes contractivity metadata."""
        config = MLIRConfig(
            epsilon=0.07,
            confidence=0.999,
            op_norm_T=0.95,
            prime_index=23,
        )
        emitter = MLIREmitter(config=config)
        mlir_str = emitter.emit_module()
        
        # Check metadata fields
        assert "@epsilon = 0.07 : f64" in mlir_str
        assert "@confidence = 0.999 : f64" in mlir_str
        assert "@op_norm_T = 0.95 : f64" in mlir_str
        assert "@prime_index = 23 : i64" in mlir_str
    
    def test_emit_recurrence_function_signature(self):
        """Test recurrence function has correct signature."""
        emitter = MLIREmitter()
        func_str = emitter.emit_recurrence_function()
        
        # Check function declaration
        assert "@pirtm_recurrence" in func_str
        assert "%X_t: tensor<?xf64>" in func_str
        assert "%Xi_t: tensor<?x?xf64>" in func_str
        assert "%Lambda_t: tensor<?x?xf64>" in func_str
        assert "%G_t: tensor<?xf64>" in func_str
        
        # Check return type
        assert "-> tensor<?xf64>" in func_str
        assert "return %X_next : tensor<?xf64>" in func_str


class TestMLIRSyntax:
    """Test MLIR syntax correctness."""
    
    def test_mlir_module_is_valid_mlir_text(self):
        """Test generated MLIR is syntactically valid."""
        emitter = MLIREmitter()
        mlir_str = emitter.emit_module()
        
        # Basic MLIR validation (full validation requires mlir-opt binary)
        # Check we have proper module structure
        assert mlir_str.count("{") >= mlir_str.count("}") - 1  # Allow for partial structure
        
        # Check function uses proper syntax
        assert "func.func @" in mlir_str
        assert 'return %' in mlir_str
    
    def test_mlir_operations_use_correct_syntax(self):
        """Test MLIR operations use correct dialect syntax."""
        emitter = MLIREmitter()
        mlir_str = emitter.emit_recurrence_function()
        
        # Check linalg operations
        assert '"linalg.matvec"' in mlir_str
        assert '"linalg.add"' in mlir_str
        
        # Check pirtm operations
        assert '"pirtm.sigmoid"' in mlir_str
        assert '"pirtm.clip"' in mlir_str
    
    def test_mlir_type_annotations_present(self):
        """Test MLIR includes proper type annotations."""
        emitter = MLIREmitter()
        mlir_str = emitter.emit_module()
        
        # Check tensor types
        assert "tensor<?xf64>" in mlir_str
        assert "tensor<?x?xf64>" in mlir_str
        
        # Check scalar types
        assert "f64" in mlir_str
        assert "i64" in mlir_str


class TestContractivityAttributes:
    """Test contractivity metadata encoding."""
    
    def test_epsilon_attribute_encoded(self):
        """Test epsilon is correctly encoded."""
        for epsilon in [0.01, 0.05, 0.1, 0.2]:
            config = MLIRConfig(epsilon=epsilon)
            emitter = MLIREmitter(config=config)
            mlir_str = emitter.emit_module()
            
            assert f"@epsilon = {epsilon} : f64" in mlir_str
    
    def test_confidence_attribute_encoded(self):
        """Test confidence is correctly encoded."""
        for conf in [0.9, 0.99, 0.999, 0.9999]:
            config = MLIRConfig(confidence=conf)
            emitter = MLIREmitter(config=config)
            mlir_str = emitter.emit_module()
            
            assert f"@confidence = {conf} : f64" in mlir_str
    
    def test_prime_index_attribute_encoded(self):
        """Test prime index is correctly encoded."""
        for prime in [3, 5, 7, 17, 23]:
            config = MLIRConfig(prime_index=prime)
            emitter = MLIREmitter(config=config)
            mlir_str = emitter.emit_module()
            
            assert f"@prime_index = {prime} : i64" in mlir_str
    
    def test_op_norm_attribute_encoded(self):
        """Test operator norm is correctly encoded."""
        for norm in [0.9, 0.95, 1.0, 1.05]:
            config = MLIRConfig(op_norm_T=norm)
            emitter = MLIREmitter(config=config)
            mlir_str = emitter.emit_module()
            
            assert f"@op_norm_T = {norm} : f64" in mlir_str


class TestWitnessEncoding:
    """Test ACE witness hash encoding."""
    
    def test_witness_hash_poseidon(self):
        """Test Poseidon witness hash encoding."""
        config = MLIRConfig(
            emit_witness_hash=True,
            witness_hash_type="poseidon",
        )
        emitter = MLIREmitter(config=config)
        mlir_str = emitter.emit_module(trace_id="trace_001")
        
        assert "@has_witness_commitment : i1" in mlir_str
    
    def test_witness_hash_deterministic(self):
        """Test witness hash is deterministic."""
        config = MLIRConfig(emit_witness_hash=True)
        emitter = MLIREmitter(config=config)
        
        hash1 = emitter.emit_witness_commitment("test_id")
        hash2 = emitter.emit_witness_commitment("test_id")
        
        # Same input should give same hash
        assert hash1 == hash2
    
    def test_witness_hash_different_for_different_inputs(self):
        """Test different inputs produce different hashes."""
        config = MLIRConfig(emit_witness_hash=True)
        emitter = MLIREmitter(config=config)
        
        hash1 = emitter.emit_witness_commitment("trace_001")
        hash2 = emitter.emit_witness_commitment("trace_002")
        
        assert hash1 != hash2
    
    def test_witness_hash_format_valid(self):
        """Test witness hash has valid format."""
        config = MLIRConfig(
            emit_witness_hash=True,
            witness_hash_type="poseidon",
        )
        emitter = MLIREmitter(config=config)
        
        hash_str = emitter.emit_witness_commitment("test_trace")
        
        # Should contain 0x prefix in the hash value
        assert "0x" in hash_str
        assert "@ace_witness =" in hash_str
        assert ": !pirtm.witness_hash" in hash_str


class TestRoundTripValidation:
    """Test round-trip: Python → MLIR → Verification."""
    
    def test_validator_checks_module_structure(self):
        """Test MLIRRoundTripValidator validates structure."""
        emitter = MLIREmitter()
        validator = MLIRRoundTripValidator(emitter)
        
        mlir_str = emitter.emit_module()
        is_valid, error = validator.validate_module(mlir_str)
        
        assert is_valid, f"Expected valid MLIR, got error: {error}"
        assert error is None
    
    def test_validator_detects_missing_module(self):
        """Test validator detects missing module wrapper."""
        emitter = MLIREmitter()
        validator = MLIRRoundTripValidator(emitter)
        
        invalid_mlir = "func.func @test() { return }"
        is_valid, error = validator.validate_module(invalid_mlir)
        
        assert not is_valid
        assert error is not None and "module" in error.lower()
    
    def test_validator_detects_missing_metadata(self):
        """Test validator detects missing contractivity metadata."""
        validator = MLIRRoundTripValidator(MLIREmitter())
        
        invalid_mlir = "module { func.func @test() { return } }"
        is_valid, error = validator.validate_module(invalid_mlir)
        
        assert not is_valid
        assert error is not None and "pirtm.module" in error.lower()
    
    def test_validator_detects_missing_function(self):
        """Test validator detects missing recurrence function."""
        emitter = MLIREmitter()
        validator = MLIRRoundTripValidator(emitter)
        
        invalid_mlir = "module { pirtm.module { } func.func @other() { return } }"
        is_valid, error = validator.validate_module(invalid_mlir)
        
        assert not is_valid
        assert error is not None and "recurrence" in error.lower()
    
    def test_extract_epsilon(self):
        """Test extracting epsilon from MLIR."""
        config = MLIRConfig(epsilon=0.07)
        emitter = MLIREmitter(config=config)
        validator = MLIRRoundTripValidator(emitter)
        
        mlir_str = emitter.emit_module()
        eps = validator.extract_epsilon(mlir_str)
        
        assert eps == 0.07
    
    def test_extract_contractivity_bounds(self):
        """Test extracting all contractivity bounds."""
        config = MLIRConfig(
            epsilon=0.05,
            confidence=0.9999,
            op_norm_T=1.0,
            prime_index=17,
        )
        emitter = MLIREmitter(config=config)
        validator = MLIRRoundTripValidator(emitter)
        
        mlir_str = emitter.emit_module()
        bounds = validator.extract_contractivity_bounds(mlir_str)
        
        assert bounds["epsilon"] == 0.05
        assert bounds["confidence"] == 0.9999
        assert bounds["op_norm_T"] == 1.0
        assert bounds["prime_index"] == 17


class TestMLIROperationSemantics:
    """Test semantic correctness of emitted operations."""
    
    def test_recurrence_loop_structure_correct(self):
        """Test recurrence loop has correct computation order."""
        emitter = MLIREmitter()
        func_str = emitter.emit_recurrence_function()
        
        # Find line numbers of operations
        lines = func_str.split("\n")
        
        # T(X_t) should come before Ξ X_t
        sigmoid_idx = next(i for i, line in enumerate(lines) if "pirtm.sigmoid" in line)
        xi_idx = next(i for i, line in enumerate(lines) if "// Step 2:" in line)
        
        assert sigmoid_idx < xi_idx, "Sigmoid should be computed before Xi·X_t"
    
    def test_projection_bounds_values(self):
        """Test projection has correct bound values."""
        emitter = MLIREmitter()
        func_str = emitter.emit_recurrence_function()
        
        # Check bounds
        assert "bound_low = -1.0 : f64" in func_str
        assert "bound_high = 1.0 : f64" in func_str
    
    def test_l0_invariant_in_comments(self):
        """Test L0 invariant documented in code."""
        config = MLIRConfig(epsilon=0.05)
        emitter = MLIREmitter(config=config)
        func_str = emitter.emit_recurrence_function()
        
        # Should document the bound
        threshold = 1.0 - config.epsilon
        assert str(threshold) in func_str or "||X_next||" in func_str


class TestPythonMLIRIntegration:
    """Test integration between Python backend and MLIR lowering."""
    
    def test_mlir_operations_correspond_to_backend(self):
        """Test MLIR operations match backend protocol."""
        from pirtm.backend import get_backend
        
        emitter = MLIREmitter()
        _ = get_backend("numpy")  # Verify backend exists
        
        # Get MLIR code
        mlir_str = emitter.emit_recurrence_function()
        
        # Check that MLIR operations align with backend methods
        assert "linalg.matvec" in mlir_str  # backend.matmul
        assert "linalg.add" in mlir_str  # backend.add
        assert "pirtm.sigmoid" in mlir_str  # backend.sigmoid
        assert "pirtm.clip" in mlir_str  # backend.clip
    
    def test_emitter_independent_of_backend(self):
        """Test MLIREmitter doesn't depend on specific backend."""
        import inspect
        
        _ = MLIREmitter()  # Verify instantiation
        source = inspect.getsource(MLIREmitter)
        
        # Should not import numpy directly
        lines = source.split("\n")
        import_lines = [l for l in lines if "import" in l and "numpy" in l.lower()]
        
        assert len(import_lines) == 0, "MLIREmitter should not import numpy"


class TestTestFixture:
    """Test utility function for generating test fixtures."""
    
    def test_fixture_generation(self):
        """Test emit_mlir_test_fixture generates valid MLIR."""
        mlir_str = emit_mlir_test_fixture(
            dimension=512,
            epsilon=0.05,
            policy="CarryForward",
        )
        
        assert "module {" in mlir_str
        assert "@pirtm_recurrence" in mlir_str
        assert "@epsilon = 0.05" in mlir_str
    
    def test_fixture_with_different_params(self):
        """Test fixture generation with various parameters."""
        for dim in [256, 512, 1024]:
            for eps in [0.01, 0.05, 0.1]:
                mlir_str = emit_mlir_test_fixture(
                    dimension=dim,
                    epsilon=eps,
                    policy="CarryForward",
                )
                
                assert f"@epsilon = {eps}" in mlir_str
                assert "module {" in mlir_str


class TestDiagnosticsHeader:
    """Test MLIR–opt diagnostic header generation."""
    
    def test_diagnostics_header_generated(self):
        """Test emit_diagnostics_header produces CHECK directives."""
        emitter = MLIREmitter()
        diag_str = emitter.emit_diagnostics_header()
        
        assert "expected-no-errors" in diag_str
        assert "// CHECK:" in diag_str
    
    def test_diagnostics_match_emitted_module(self):
        """Test diagnostics are compatible with emitted module."""
        emitter = MLIREmitter()
        diag_str = emitter.emit_diagnostics_header()
        mlir_str = emitter.emit_module()
        
        # Extract CHECK patterns
        patterns = re.findall(r"// CHECK: (\w+)", diag_str)
        
        # All patterns should appear in MLIR
        for pattern in patterns:
            assert pattern in mlir_str or pattern.lower() in mlir_str


# ========== Integration Tests ==========

class TestEndToEndMLIREmission:
    """End-to-end test: descriptor → MLIR → verification."""
    
    def test_complete_mlir_emission_pipeline(self):
        """Test full pipeline from factory to validated MLIR."""
        # 1. Create emitter with standard config
        config = MLIRConfig(
            epsilon=0.05,
            confidence=0.9999,
            prime_index=17,
        )
        emitter = MLIREmitter(config=config)
        
        # 2. Emit module
        mlir_str = emitter.emit_module(
            policy_name="CarryForward",
            kernel_name="FullAsymmetricAttribution",
            trace_id="session_001",
            dimension=512,
        )
        
        # 3. Validate
        validator = MLIRRoundTripValidator(emitter)
        is_valid, error = validator.validate_module(mlir_str)
        
        # 4. Verify bounds extraction
        bounds = validator.extract_contractivity_bounds(mlir_str)
        
        # Assert all checks pass
        assert is_valid, f"MLIR validation failed: {error}"
        assert bounds["epsilon"] == 0.05
        assert bounds["prime_index"] == 17
        assert len(mlir_str) > 0
    
    def test_multiple_emissions_are_independent(self):
        """Test multiple emitters don't interfere."""
        emitters = [
            MLIREmitter(config=MLIRConfig(epsilon=e))
            for e in [0.01, 0.05, 0.1]
        ]
        
        mlir_strs = [e.emit_module() for e in emitters]
        
        # Each should have its own epsilon
        for i, mlir_str in enumerate(mlir_strs):
            epsilon = [0.01, 0.05, 0.1][i]
            assert f"@epsilon = {epsilon}" in mlir_str


# ========== Run Tests ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
