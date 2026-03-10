"""
Test suite for Phase 3 Mirror: MLIR-Level Contractivity Verification Pass

Tests the verification logic matching the C++ specification in verify_contractivity_spec.cc
and the Python implementation in verification_pass.py.

Related: ADR-008-contractivity-types.md
"""

import pytest
from pirtm.mlir.verification_pass import (
    ContractivityType,
    ContractivityVerifier,
    ProjectionRule,
    SpectralRule,
    verify_mlir_contractivity,
)


class TestContractivityTypeValidity:
    """Test ContractivityType creation and validation."""
    
    def test_valid_type_creation(self):
        """Create valid contractivity type."""
        t = ContractivityType(epsilon=0.05, confidence=0.9999)
        assert t.epsilon == 0.05
        assert t.confidence == 0.9999
        assert t.is_valid()
    
    def test_type_string_representation(self):
        """String representation for diagnostics."""
        t = ContractivityType(epsilon=0.05, confidence=0.9999)
        s = str(t)
        assert "0.05" in s
        assert "0.9999" in s
        assert "contractivity" in s
    
    def test_invalid_epsilon_negative(self):
        """Epsilon must be non-negative."""
        t = ContractivityType(epsilon=-0.1, confidence=0.9999)
        assert not t.is_valid()
    
    def test_invalid_epsilon_one_or_greater(self):
        """Epsilon must be less than 1.0."""
        t = ContractivityType(epsilon=1.0, confidence=0.9999)
        assert not t.is_valid()
    
    def test_invalid_confidence_zero(self):
        """Confidence must be strictly positive."""
        t = ContractivityType(epsilon=0.05, confidence=0.0)
        assert not t.is_valid()
    
    def test_invalid_confidence_greater_than_one(self):
        """Confidence must be at most 1.0."""
        t = ContractivityType(epsilon=0.05, confidence=1.1)
        assert not t.is_valid()
    
    def test_valid_confidence_one(self):
        """Confidence = 1.0 is valid (maximum certainty)."""
        t = ContractivityType(epsilon=0.05, confidence=1.0)
        assert t.is_valid()
    
    def test_boundary_epsilon_zero(self):
        """Epsilon = 0.0 is valid (maximum contractivity)."""
        t = ContractivityType(epsilon=0.0, confidence=0.5)
        assert t.is_valid()


class TestCompositionRule:
    """Test the composition rule: ε' = min(ε₁, ε₂), δ' = δ₁ * δ₂"""
    
    def test_composition_epsilon_minimum(self):
        """Composition takes minimum epsilon."""
        t1 = ContractivityType(epsilon=0.05, confidence=0.9)
        t2 = ContractivityType(epsilon=0.10, confidence=0.95)
        
        result = t1.compose(t2)
        
        # ε' = min(0.05, 0.10) = 0.05
        assert result.epsilon == 0.05
    
    def test_composition_confidence_multiplication(self):
        """Composition multiplies confidence."""
        t1 = ContractivityType(epsilon=0.05, confidence=0.9)
        t2 = ContractivityType(epsilon=0.10, confidence=0.95)
        
        result = t1.compose(t2)
        
        # δ' = 0.9 * 0.95 = 0.855
        assert result.confidence == pytest.approx(0.855)
    
    def test_composition_monotonicity_confidence(self):
        """Composition weakens confidence monotonically."""
        t1 = ContractivityType(epsilon=0.05, confidence=0.9999)
        t2 = ContractivityType(epsilon=0.01, confidence=0.99)
        
        result = t1.compose(t2)
        
        # δ' ≤ min(δ₁, δ₂)
        assert result.confidence <= min(t1.confidence, t2.confidence)
    
    def test_composition_chain(self):
        """Composition chains correctly."""
        t1 = ContractivityType(epsilon=0.05, confidence=0.9999)
        t2 = ContractivityType(epsilon=0.10, confidence=0.99)
        t3 = ContractivityType(epsilon=0.02, confidence=0.95)
        
        # Chain: (T₁ ∘ T₂) ∘ T₃
        result = t1.compose(t2).compose(t3)
        
        # ε' = min(0.05, 0.10, 0.02) = 0.02
        # δ' = 0.9999 * 0.99 * 0.95 ≈ 0.9407
        assert result.epsilon == 0.02
        assert result.confidence == pytest.approx(0.9999 * 0.99 * 0.95)


class TestProjectionRule:
    """Test the projection rule: clip → contractivity<0.0, 1.0>"""
    
    def test_projection_rule_matches_clip(self):
        """ProjectionRule matches pirtm.clip operations."""
        assert ProjectionRule.matches("pirtm.clip", {})
    
    def test_projection_rule_no_match_other_ops(self):
        """ProjectionRule doesn't match other operations."""
        assert not ProjectionRule.matches("pirtm.sigmoid", {})
        assert not ProjectionRule.matches("linalg.matmul", {})
    
    def test_projection_maximum_contractivity(self):
        """Projection produces maximum contractivity."""
        result = ProjectionRule.infer("pirtm.clip", {}, {})
        
        assert result is not None
        assert result.epsilon == 0.0
        assert result.confidence == 1.0
    
    def test_projection_idempotence(self):
        """Projecting twice doesn't strengthen the type."""
        t1 = ProjectionRule.infer("pirtm.clip", {}, {})
        t2 = ProjectionRule.infer("pirtm.clip", {}, {})
        
        assert t1 is not None and t2 is not None
        # Both should have same type
        assert t1.epsilon == t2.epsilon
        assert t1.confidence == t2.confidence


class TestSpectralRule:
    """Test the spectral rule: r(Λ) < 1 - ε → contractivity<ε, conf>"""
    
    def test_spectral_rule_matches_recurrence(self):
        """SpectralRule matches pirtm.recurrence operations."""
        assert SpectralRule.matches("pirtm.recurrence", {})
    
    def test_spectral_rule_no_match_other_ops(self):
        """SpectralRule doesn't match other operations."""
        assert not SpectralRule.matches("pirtm.clip", {})
        assert not SpectralRule.matches("linalg.matmul", {})
    
    def test_spectral_condition_valid(self):
        """Valid spectral radius passes condition."""
        epsilon = 0.05
        spectral_radius = 0.90
        
        # r(Λ) = 0.90 < 1 - 0.05 = 0.95 ✓
        assert SpectralRule.verify(spectral_radius, epsilon)
    
    def test_spectral_condition_invalid(self):
        """Invalid spectral radius fails condition."""
        epsilon = 0.05
        spectral_radius = 0.96
        
        # r(Λ) = 0.96 > 1 - 0.05 = 0.95 ✗
        assert not SpectralRule.verify(spectral_radius, epsilon)
    
    def test_spectral_condition_boundary(self):
        """Boundary case r(Λ) = 1 - ε fails."""
        epsilon = 0.05
        spectral_radius = 0.95  # Exactly at threshold
        
        # r(Λ) = 0.95 NOT < 1 - 0.05 = 0.95
        assert not SpectralRule.verify(spectral_radius, epsilon)
    
    def test_spectral_rule_infer(self):
        """SpectralRule infers type from attributes."""
        attributes = {
            'epsilon': 0.05,
            'confidence': 0.9999,
        }
        result = SpectralRule.infer("pirtm.recurrence", attributes, {})
        
        assert result is not None
        assert result.epsilon == 0.05
        assert result.confidence == 0.9999


class TestContractivityVerifier:
    """Test the contractivity verifier engine."""
    
    def test_verifier_initialization(self):
        """Verifier initializes with MLIR text."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
        }
        """
        verifier = ContractivityVerifier(mlir)
        assert verifier.type_map == {}
        assert verifier.errors == []
    
    def test_verifier_empty_module(self):
        """Empty module passes verification."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
        }
        """
        verifier = ContractivityVerifier(mlir)
        assert verifier.verify()
    
    def test_verifier_forward_pass_projection(self):
        """Forward pass infers projection type."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
        }
        %X = "pirtm.clip"(%Y) : (tensor<?xf64>) -> tensor<?xf64>
        """
        verifier = ContractivityVerifier(mlir)
        types = verifier.forward_pass()
        
        # X should have projection type
        assert 'X' in types
        assert types['X'].epsilon == 0.0
        assert types['X'].confidence == 1.0
    
    def test_verifier_error_invalid_type(self):
        """Verifier detects invalid contractivity types."""
        t = ContractivityType(epsilon=-0.1, confidence=0.9999)
        verifier = ContractivityVerifier("")
        verifier.type_map['op1'] = t
        
        assert not verifier.backward_pass()
        assert len(verifier.errors) > 0
    
    def test_verifier_spectral_condition_check(self):
        """Verifier verifies spectral conditions."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
          @spectral_radius = 0.96 : f64
        }
        """
        verifier = ContractivityVerifier(mlir)
        
        # Should fail: r(Λ) = 0.96 >= 1 - 0.05 = 0.95
        assert not verifier.verify()
    
    def test_verifier_error_messages(self):
        """Verifier emits clear error messages."""
        verifier = ContractivityVerifier("")
        verifier.emit_error("op1", "Test error message")
        
        errors = verifier.get_errors()
        assert len(errors) == 1
        assert "op1" in errors[0][0]
        assert "Test error message" in errors[0][1]
    
    def test_verifier_warning_messages(self):
        """Verifier emits warnings (don't fail verification)."""
        verifier = ContractivityVerifier("")
        verifier.emit_warning("op2", "Test warning")
        
        warnings = verifier.get_warnings()
        assert len(warnings) == 1
        assert "Test warning" in warnings[0][1]


class TestIntegration:
    """Integration tests: full verification pipeline."""
    
    def test_full_pipeline_simple_projection(self):
        """Full pipeline: simple projection."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
        }
        %X = "pirtm.clip"(%Y) : (tensor<?xf64>) -> tensor<?xf64>
        """
        is_valid, _, _, _ = verify_mlir_contractivity(mlir)
        
        assert is_valid
    
    def test_full_pipeline_recurrence_valid(self):
        """Full pipeline: valid recurrence."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
          @spectral_radius = 0.90 : f64
        }
        %X_next = "pirtm.recurrence"(%X_t, %Lambda_t)
          : (tensor<?xf64>, tensor<?x?xf64>) -> tensor<?xf64>
        """
        is_valid, _, _, _ = verify_mlir_contractivity(mlir)
        
        # r(Λ) = 0.90 < 1 - 0.05 = 0.95, so should pass
        assert is_valid
        # error count is checked implicitly by is_valid
    
    def test_full_pipeline_recurrence_invalid_spectral(self):
        """Full pipeline: invalid spectral radius."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
          @spectral_radius = 0.96 : f64
        }
        %X_next = "pirtm.recurrence"(%X_t, %Lambda_t)
          : (tensor<?xf64>, tensor<?x?xf64>) -> tensor<?xf64>
        """
        is_valid, _, _, _ = verify_mlir_contractivity(mlir)
        
        # r(Λ) = 0.96 >= 1 - 0.05 = 0.95, should fail
        assert not is_valid
    
    def test_full_pipeline_composition(self):
        """Full pipeline: composition of operations."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
        }
        %X = "pirtm.clip"(%Y) : (tensor<?xf64>) -> tensor<?xf64>
        %A_mat = "linalg.eye"() : () -> tensor<?x?xf64>
        %result = "linalg.matmul"(%A_mat, %X)
          : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>
        """
        _, types, _, _ = verify_mlir_contractivity(mlir)
        
        # Should infer types for X and result
        assert 'X' in types
        # result should have composed type if linalg.matmul is recognized
    
    def test_multiple_verifiers_independent(self):
        """Multiple verifiers operate independently."""
        mlir1 = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
        }
        """
        mlir2 = """
        pirtm.module {
          @epsilon = 0.10 : f64
          @confidence = 0.99 : f64
        }
        """
        
        verifier1 = ContractivityVerifier(mlir1)
        verifier2 = ContractivityVerifier(mlir2)
        
        _ = verifier1.forward_pass()
        _ = verifier2.forward_pass()
        
        # Verifiers should not interfere
        assert verifier1.type_map is not verifier2.type_map


class TestErrorDiagnostics:
    """Test error message quality."""
    
    def test_spectral_failure_diagnostic(self):
        """Spectral failure includes actual values."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
          @spectral_radius = 0.96 : f64
        }
        """
        is_valid, _, errors, _ = verify_mlir_contractivity(mlir)
        
        assert not is_valid
        assert len(errors) > 0
        error_msg = errors[0]
        assert "0.96" in error_msg  # Actual r(Λ)
        assert "0.95" in error_msg  # Threshold 1 - ε


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_zero_epsilon(self):
        """Zero epsilon (maximum contractivity) is valid."""
        t = ContractivityType(epsilon=0.0, confidence=0.5)
        assert t.is_valid()
    
    def test_very_small_confidence(self):
        """Very small confidence is valid."""
        t = ContractivityType(epsilon=0.5, confidence=0.001)
        assert t.is_valid()
    
    def test_composition_with_zero_epsilon(self):
        """Composition with zero epsilon preserves minimum."""
        t1 = ContractivityType(epsilon=0.0, confidence=0.9)
        t2 = ContractivityType(epsilon=0.1, confidence=0.9)
        
        result = t1.compose(t2)
        
        # ε' = min(0.0, 0.1) = 0.0
        assert result.epsilon == 0.0
    
    def test_composition_confidence_accumulation(self):
        """Long composition degrades confidence significantly."""
        # Start with high confidence
        t = ContractivityType(epsilon=0.05, confidence=0.99)
        
        # Compose 50 times
        for _ in range(50):
            t = t.compose(ContractivityType(epsilon=0.05, confidence=0.99))
        
        # Confidence should be much lower than initial
        # 0.99 ** 51 ≈ 0.599
        assert t.confidence < 0.7  # Much less than starting 0.99
        assert t.confidence > 0.5   # But not down to zero


class TestPerformance:
    """Test performance characteristics."""
    
    def test_verification_speed_small_module(self):
        """Verification is fast for small modules."""
        mlir = """
        pirtm.module {
          @epsilon = 0.05 : f64
          @confidence = 0.9999 : f64
        }
        %X1 = "pirtm.clip"(%Y1) : (tensor<?xf64>) -> tensor<?xf64>
        %X2 = "pirtm.clip"(%Y2) : (tensor<?xf64>) -> tensor<?xf64>
        %X3 = "pirtm.clip"(%Y3) : (tensor<?xf64>) -> tensor<?xf64>
        """
        
        import time
        start = time.time()
        _, _, _, _ = verify_mlir_contractivity(mlir)
        elapsed = time.time() - start
        
        # Should be very fast (< 10 ms even on slow machines)
        assert elapsed < 0.01
    
    def test_composition_stability_extreme_values(self):
        """Composition is numerically stable with extreme values."""
        t1 = ContractivityType(epsilon=0.00001, confidence=0.9999999)
        t2 = ContractivityType(epsilon=0.99999, confidence=0.0000001)
        
        result = t1.compose(t2)
        
        # Should not overflow/underflow
        assert 0.0 <= result.epsilon < 1.0
        assert 0.0 < result.confidence <= 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
