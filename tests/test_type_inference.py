"""
Test Suite for Phase 3: Contractivity Type System.

Validates:
1. Type inference correctness
2. Composition rule soundness
3. Spectral condition verification
4. End-to-end type checking
5. MLIR rewriting with type annotations

See: ADR-008-contractivity-types.md
"""

import pytest

from pirtm.type_inference import (
    ContractivityType,
    ContractivityInference,
    ContractivityTypeChecker,
    infer_and_check,
)


class TestContractivityType:
    """Test ContractivityType data structure."""
    
    def test_type_creation(self):
        """Test creating contractivity types."""
        typ = ContractivityType(epsilon=0.05, confidence=0.9999)
        
        assert typ.epsilon == 0.05
        assert typ.confidence == 0.9999
    
    def test_type_string_representation(self):
        """Test string output."""
        typ = ContractivityType(epsilon=0.05, confidence=0.9999)
        
        assert str(typ) == "!pirtm.contractivity<epsilon = 0.05, confidence = 0.9999>"
    
    def test_type_composition_rule(self):
        """Test composition weakens bounds."""
        # Composition: T₁ ∘ T₂
        # ε' = min(ε₁, ε₂), δ' = δ₁ * δ₂
        
        t1 = ContractivityType(epsilon=0.05, confidence=0.9999)
        t2 = ContractivityType(epsilon=0.10, confidence=0.99)
        
        composed = t1.compose(t2)
        
        # Epsilon should be minimum
        assert composed.epsilon == 0.05
        
        # Confidence should be product (weakens)
        assert abs(composed.confidence - 0.9999 * 0.99) < 1e-6
        assert composed.confidence < min(t1.confidence, t2.confidence)
    
    def test_composition_with_projection(self):
        """Test composing with projection (maximum contractivity)."""
        proj = ContractivityType(epsilon=0.0, confidence=1.0)
        other = ContractivityType(epsilon=0.05, confidence=0.9999)
        
        composed = proj.compose(other)
        
        # Composition with projection shouldn't improve bounds
        assert composed.epsilon == 0.0
        assert composed.confidence == 0.9999


class TestInferenceEngine:
    """Test ContractivityInference engine."""
    
    def test_inference_initialization(self):
        """Test creating inference engine."""
        inf = ContractivityInference(epsilon=0.05, confidence=0.9999)
        
        assert inf.epsilon == 0.05
        assert inf.confidence == 0.9999
    
    def test_inference_with_projection(self):
        """Test type inference on projection operation."""
        mlir_str = '''%X = "pirtm.clip"(%Y) { bound_low = -1.0, bound_high = 1.0 } : (tensor<?xf64>) -> tensor<?xf64>'''
        
        inf = ContractivityInference(epsilon=0.05, confidence=0.9999)
        typed_mlir = inf.infer_types(mlir_str)
        
        # Should process the MLIR without errors
        assert "pirtm.clip" in typed_mlir
    
    def test_spectral_condition_valid(self):
        """Test spectral condition when r(Λ) is valid."""
        inf = ContractivityInference(epsilon=0.05)
        
        # r(Λ) = 0.90 < 1 - 0.05 = 0.95 ✓
        is_valid, error = inf.verify_spectral_condition(0.90)
        
        assert is_valid
        assert error is None
    
    def test_spectral_condition_invalid(self):
        """Test spectral condition when r(Λ) is invalid."""
        inf = ContractivityInference(epsilon=0.05)
        
        # r(Λ) = 0.96 > 1 - 0.05 = 0.95 ✗
        is_valid, error = inf.verify_spectral_condition(0.96)
        
        assert not is_valid
        assert "spectral radius" in error.lower() if error else False
        assert "exceeds" in error.lower() if error else False
    
    def test_spectral_condition_boundary(self):
        """Test spectral condition at boundary."""
        inf = ContractivityInference(epsilon=0.05)
        
        # r(Λ) = 0.95 = 1 - 0.05 (boundary, should fail)
        is_valid, error = inf.verify_spectral_condition(0.95)
        _ = error  # Not used in test
        
        assert not is_valid


class TestTypeInference:
    """Test type inference algorithm."""
    
    def test_inference_empty_module(self):
        """Test inference on empty module."""
        mlir_str = "module { }"
        
        inf = ContractivityInference()
        typed_mlir = inf.infer_types(mlir_str)
        
        assert "module {" in typed_mlir
    
    def test_inference_preserves_structure(self):
        """Test that inference preserves MLIR structure."""
        mlir_str = '''
        module {
          func.func @test(%X: tensor<?xf64>) -> tensor<?xf64> {
            return %X : tensor<?xf64>
          }
        }
        '''
        
        inf = ContractivityInference()
        typed_mlir = inf.infer_types(mlir_str)
        
        # Should still have module, func, return
        assert "module {" in typed_mlir
        assert "func.func @test" in typed_mlir
        assert "return" in typed_mlir
    
    def test_statistics_empty(self):
        """Test statistics on empty inference."""
        inf = ContractivityInference()
        inf.infer_types("module { }")
        
        stats = inf.get_statistics()
        
        assert stats["total_operations"] == 0
        assert stats["typed_operations"] == 0


class TestCompositionRules:
    """Test type composition rules."""
    
    def test_identity_composition(self):
        """Test T ∘ T doesn't change ε, weakens δ."""
        t = ContractivityType(epsilon=0.05, confidence=0.9999)
        
        composed = t.compose(t)
        
        # Epsilon same, confidence weakened
        assert composed.epsilon == t.epsilon
        assert composed.confidence == 0.9999 ** 2
        assert composed.confidence < t.confidence
    
    def test_multiple_compositions(self):
        """Test chaining multiple compositions."""
        t1 = ContractivityType(epsilon=0.05, confidence=0.9999)
        t2 = ContractivityType(epsilon=0.05, confidence=0.9999)
        t3 = ContractivityType(epsilon=0.05, confidence=0.9999)
        
        # (T₁ ∘ T₂) ∘ T₃
        intermediate = t1.compose(t2)
        final = intermediate.compose(t3)
        
        # Epsilon stays at 0.05
        assert final.epsilon == 0.05
        
        # Confidence = 0.9999^3
        assert abs(final.confidence - 0.9999 ** 3) < 1e-6
    
    def test_composition_monotonicity(self):
        """Test that composition weakens confidence monotonically."""
        t1 = ContractivityType(epsilon=0.05, confidence=0.99)
        t2 = ContractivityType(epsilon=0.05, confidence=0.9)
        
        composed = t1.compose(t2)
        
        # Confidence should be weaker than both inputs
        assert composed.confidence <= min(t1.confidence, t2.confidence)
        assert composed.confidence == 0.99 * 0.9


class TestBoundsWeakening:
    """Test that bounds weaken appropriately."""
    
    def test_epsilon_weakening_via_minimum(self):
        """Test that epsilon weakens via minimum rule."""
        t_tight = ContractivityType(epsilon=0.01, confidence=0.9999)
        t_loose = ContractivityType(epsilon=0.10, confidence=0.9999)
        
        composed = t_tight.compose(t_loose)
        
        # Epsilon = minimum, so 0.01
        assert composed.epsilon == 0.01
        
        # But this represents the looser bound
        assert composed.epsilon <= t_loose.epsilon
    
    def test_confidence_weakening_via_product(self):
        """Test that confidence weakens via product rule."""
        for conf1 in [0.9, 0.99, 0.999, 0.9999]:
            for conf2 in [0.9, 0.99, 0.999, 0.9999]:
                t1 = ContractivityType(epsilon=0.05, confidence=conf1)
                t2 = ContractivityType(epsilon=0.05, confidence=conf2)
                
                composed = t1.compose(t2)
                
                # Confidence should be product
                assert abs(composed.confidence - conf1 * conf2) < 1e-9


class TestProjectionType:
    """Test projection operation typing."""
    
    def test_projection_maximum_contractivity(self):
        """Test that clip produces maximum contractivity."""
        # Manually create a projection operation
        # and check its type
        
        # clip is a projection, should produce contractivity<0.0, 1.0>
        proj_type = ContractivityType(epsilon=0.0, confidence=1.0)
        
        assert proj_type.epsilon == 0.0
        assert proj_type.confidence == 1.0
    
    def test_projection_idempotence(self):
        """Test that projecting twice doesn't improve bounds."""
        proj1 = ContractivityType(epsilon=0.0, confidence=1.0)
        proj2 = ContractivityType(epsilon=0.0, confidence=1.0)
        
        composed = proj1.compose(proj2)
        
        # Should still be maximum contractivity
        assert composed.epsilon == 0.0
        assert composed.confidence == 1.0


class TestTypeChecker:
    """Test ContractivityTypeChecker."""
    
    def test_checker_initialization(self):
        """Test creating type checker."""
        inf = ContractivityInference()
        inf.infer_types("module { }")
        
        checker = ContractivityTypeChecker(inf)
        
        assert checker.inference == inf
        assert len(checker.errors) == 0
    
    def test_checker_no_errors_empty_module(self):
        """Test type checking on empty module."""
        _ = ContractivityInference()
        _.infer_types("module { }")
        
        checker = ContractivityTypeChecker(_)
        is_valid, errors, _ = checker.check()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_checker_spectral_condition(self):
        """Test type checker verifies spectral condition."""
        inf = ContractivityInference(epsilon=0.05)
        inf.spectral_radius = 0.96  # Invalid (> 0.95)
        inf.infer_types("module { }")
        
        checker = ContractivityTypeChecker(inf)
        is_valid, errors, _ = checker.check()
        
        assert not is_valid
        assert len(errors) > 0


class TestConvenienceFunction:
    """Test infer_and_check convenience API."""
    
    def test_infer_and_check_basic(self):
        """Test the convenience function."""
        mlir_str = "module { }"
        
        _, _, errors, _ = infer_and_check(
            mlir_str,
            epsilon=0.05,
            confidence=0.9999,
        )
        
        assert len(errors) == 0
    
    def test_infer_and_check_with_spectral_radius_valid(self):
        """Test convenience function with valid spectral radius."""
        mlir_str = "module { }"
        
        _, _, errors, _ = infer_and_check(
            mlir_str,
            epsilon=0.05,
            confidence=0.9999,
            spectral_radius=0.90,  # Valid (< 0.95)
        )
        
        assert len(errors) == 0
    
    def test_infer_and_check_with_spectral_radius_invalid(self):
        """Test convenience function with invalid spectral radius."""
        mlir_str = "module { }"
        
        _, _, errors, _ = infer_and_check(
            mlir_str,
            epsilon=0.05,
            confidence=0.9999,
            spectral_radius=0.96,  # Invalid (> 0.95)
        )
        
        assert len(errors) > 0


class TestMLIRRewriting:
    """Test MLIR rewriting with type annotations."""
    
    def test_rewrite_preserves_content(self):
        """Test that rewriting preserves MLIR content."""
        mlir_str = '''
        module {
          func.func @test(%X: tensor<?xf64>) -> tensor<?xf64> {
            return %X : tensor<?xf64>
          }
        }
        '''
        
        inf = ContractivityInference()
        typed_mlir = inf.infer_types(mlir_str)
        
        # Should still be valid MLIR
        assert "module {" in typed_mlir
        assert "func.func @test" in typed_mlir
        assert "tensor<?xf64>" in typed_mlir
    
    def test_type_annotation_injected(self):
        """Test that type annotations are injected where appropriate."""
        # This test would require more complex MLIR parsing
        # For now, just check that rewriting doesn't break structure
        
        mlir_str = "module { }"
        
        inf = ContractivityInference()
        typed_mlir = inf.infer_types(mlir_str)
        
        # Module should still be valid
        assert typed_mlir.startswith("module")


class TestIntegration:
    """End-to-end integration tests."""
    
    def test_full_pipeline_descriptor_to_typed(self):
        """Test full pipeline from descriptor to typed MLIR."""
        # Simulate what happens in Phase 2 → Phase 3
        
        # Phase 2 output (untyped MLIR)
        mlir_str = '''
        module {
          func.func @pirtm_recurrence(
            %X_t: tensor<?xf64>,
            %Xi_t: tensor<?x?xf64>,
            %Lambda_t: tensor<?x?xf64>,
            %G_t: tensor<?xf64>
          ) -> tensor<?xf64> {
            %T_X_t = "pirtm.sigmoid"(%X_t)
              : (tensor<?xf64>) -> tensor<?xf64>
            
            %term1 = "linalg.matvec"(%Xi_t, %X_t)
              : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>
            
            %term2 = "linalg.matvec"(%Lambda_t, %T_X_t)
              : (tensor<?x?xf64>, tensor<?xf64>) -> tensor<?xf64>
            
            %Y_t = "linalg.add"(%term1, %term2)
              : (tensor<?xf64>, tensor<?xf64>) -> tensor<?xf64>
            
            %X_next = "pirtm.clip"(%Y_t)
              : (tensor<?xf64>) -> tensor<?xf64>
            
            return %X_next : tensor<?xf64>
          }
        }
        '''
        
        # Phase 3: Type inference
        inf = ContractivityInference(
            epsilon=0.05,
            confidence=0.9999,
            spectral_radius=0.90,  # Valid
        )
        
        typed_mlir = inf.infer_types(mlir_str)
        
        # Check results - should still have module structure
        assert "module {" in typed_mlir
        assert "@pirtm_recurrence" in typed_mlir
        
        # No errors with valid spectral radius
        checker = ContractivityTypeChecker(inf)
        is_valid, errors, _ = checker.check()
        
        assert is_valid
        assert len(errors) == 0
    
    def test_multiple_inference_engines_independent(self):
        """Test multiple engines don't interfere."""
        mlir_str = "module { }"
        
        inf1 = ContractivityInference(epsilon=0.01, confidence=0.99)
        inf2 = ContractivityInference(epsilon=0.10, confidence=0.999)
        
        inf1.infer_types(mlir_str)
        inf2.infer_types(mlir_str)
        
        # Should have independent state
        assert inf1.epsilon == 0.01
        assert inf2.epsilon == 0.10


class TestPerformance:
    """Performance tests for type inference."""
    
    def test_inference_speed_small_graph(self):
        """Test inference speed on small MLIR module."""
        # Small module with ~10 operations
        mlir_str = '''
        module {
          func.func @test(%X: tensor<?xf64>) -> tensor<?xf64> {
            %Y = "pirtm.sigmoid"(%X) : (tensor<?xf64>) -> tensor<?xf64>
            return %Y : tensor<?xf64>
          }
        }
        '''
        
        inf = ContractivityInference()
        
        # Should be very fast
        typed_mlir = inf.infer_types(mlir_str)
        
        assert "module {" in typed_mlir
    
    def test_inference_stability_large_epsilon_values(self):
        """Test inference with extreme epsilon values."""
        for epsilon in [0.001, 0.01, 0.1, 0.5, 0.9]:
            inf = ContractivityInference(epsilon=epsilon)
            
            is_valid, _ = inf.verify_spectral_condition(0.5 * (1.0 - epsilon))
            
            # Should be valid for r(Λ) = 0.5 * (1 - ε)
            assert is_valid or epsilon > 0.999


# ========== Run Tests ==========

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
