// MLIR Verification Pass for PIRTM Contractivity Type System
// Phase 3 Mirror: Formal C++ Interface Specification
// 
// This file defines the MLIR pass interface for contractivity verification.
// Implementation against LLVM/MLIR library targets LLVM 17+.
//
// Status: SPECIFICATION (implementation pending LLVM/MLIR build system setup)
// Related: ADR-008-contractivity-types.md

#ifndef PIRTM_MLIR_PASSES_VERIFY_CONTRACTIVITY_H
#define PIRTM_MLIR_PASSES_VERIFY_CONTRACTIVITY_H

#include "mlir/Pass/Pass.h"
#include "mlir/IR/Dialect.h"
#include "mlir/IR/PatternMatch.h"
#include <memory>
#include <string>
#include <optional>

namespace mlir::pirtm {

/// Forward declarations
class ContractivityType;
class ContractivityVerifier;

/// ============================================================================
/// ContractivityType: First-class type representation
/// ============================================================================

/// Represents !pirtm.contractivity<epsilon, confidence>
class ContractivityType {
public:
  /// Epsilon margin for spectral radius: r(Λ) < 1 - epsilon
  double epsilon;
  
  /// Confidence level (0.0 to 1.0): probability guarantee
  double confidence;
  
  /// Constructor
  ContractivityType(double eps = 0.0, double conf = 1.0)
    : epsilon(eps), confidence(conf) {}
  
  /// Compose two contractivity types
  /// Result: eps' = min(eps1, eps2), conf' = conf1 * conf2
  static ContractivityType compose(const ContractivityType& t1,
                                    const ContractivityType& t2) {
    return ContractivityType(
      std::min(t1.epsilon, t2.epsilon),
      t1.confidence * t2.confidence
    );
  }
  
  /// Check if both components are in valid ranges
  bool isValid() const {
    return epsilon >= 0.0 && epsilon < 1.0 &&
           confidence > 0.0 && confidence <= 1.0;
  }
  
  /// String representation for diagnostics
  std::string str() const;
};

/// ============================================================================
/// Type Inference Rules
/// ============================================================================

/// Rule 1: Projection (clipping) produces maximum contractivity
/// 
/// Judgment: clip(Y) → X
///   X : contractivity<epsilon = 0.0, confidence = 1.0>
///
/// Rationale: Clipping to [-1, 1] guarantees ||X|| ≤ 1
class ProjectionRule {
public:
  /// Check if operation is a projection (pirtm.clip with bounds [-1, 1])
  static bool matches(Operation* op);
  
  /// Infer type: always contractivity<0.0, 1.0>
  static ContractivityType infer(Operation* op) {
    return ContractivityType(0.0, 1.0);
  }
};

/// Rule 2: Composition weakens bounds
///
/// Judgment: T₁ : contractivity<ε₁, δ₁>, T₂ : contractivity<ε₂, δ₂>
///   T₁ ∘ T₂ : contractivity<min(ε₁, ε₂), δ₁ * δ₂>
///
/// Rationale: Confidence multiplies; epsilon takes minimum
class CompositionRule {
public:
  /// Check if operation is a composition of two contractivity-typed values
  static bool matches(Operation* op,
                      const ContractivityType& t1,
                      const ContractivityType& t2);
  
  /// Infer type via composition rule
  static ContractivityType infer(const ContractivityType& t1,
                                 const ContractivityType& t2) {
    return ContractivityType::compose(t1, t2);
  }
};

/// Rule 3: Spectral condition verifies recurrence contractivity
///
/// Judgment: gain matrix Λ, r(Λ) < 1 - ε
///   recurrence(Λ, ...) : contractivity<ε, 0.9999>
///
/// Rationale: Spectral radius bounds ensure fixed-point contraction
class SpectralRule {
public:
  /// Check if operation is pirtm.recurrence with spectral radius attribute
  static bool matches(Operation* op);
  
  /// Extract epsilon from module or operation metadata
  static std::optional<double> extractEpsilon(Operation* op, Operation* module);
  
  /// Extract spectral radius from gain matrix
  // Signature: double spectralRadius(ArrayRef<ArrayRef<double>> gainMatrix)
  // Implementation: Eigenvalue computation via power iteration or Gershgorin
  
  /// Verify spectral condition: r(Λ) < 1 - epsilon
  static bool verify(double spectralRadius, double epsilon) {
    return spectralRadius < (1.0 - epsilon);
  }
};

/// ============================================================================
/// Contractivity Verifier: Main verification engine
/// ============================================================================

class ContractivityVerifier {
private:
  Operation* module;
  std::map<Value, ContractivityType> typeMap;
  std::vector<std::string> errors;
  std::vector<std::string> warnings;
  
public:
  /// Constructor
  explicit ContractivityVerifier(Operation* mod) : module(mod) {}
  
  /// Run forward pass: assigns types bottom-up
  void forwardPass();
  
  /// Run backward pass: verifies spectral conditions
  void backwardPass();
  
  /// Get inferred type for a value
  std::optional<ContractivityType> getType(Value v) const;
  
  /// Check if value is contractivity-typed
  bool isContractivityTyped(Value v) const;
  
  /// Verify composition rule holds for operation
  bool verifyComposition(Operation* op);
  
  /// Verify spectral condition holds for recurrence
  bool verifySpectralCondition(Operation* op);
  
  /// Emit verification error with source location
  void emitError(Operation* op, const std::string& msg);
  
  /// Emit warning (doesn't fail verification)
  void emitWarning(Operation* op, const std::string& msg);
  
  /// Run full verification
  bool verify();
  
  /// Get error messages (if verification failed)
  const std::vector<std::string>& getErrors() const { return errors; }
  
  /// Get warning messages
  const std::vector<std::string>& getWarnings() const { return warnings; }
};

/// ============================================================================
/// VerifyContractivityPass: MLIR Pass wrapper
/// ============================================================================

class VerifyContractivityPass : public PassWrapper<VerifyContractivityPass,
                                                    OperationPass<ModuleOp>> {
public:
  MLIR_DEFINE_EXPLICIT_INTERNAL_INLINE_TYPE_ID(VerifyContractivityPass)
  
  StringRef getArgument() const final {
    return "verify-pirtm-contractivity";
  }
  
  StringRef getDescription() const final {
    return "Verify PIRTM contractivity type system constraints";
  }
  
  /// Main pass entry point
  void runOnOperation() override {
    ModuleOp module = getOperation();
    
    ContractivityVerifier verifier(module.getOperation());
    
    // Forward pass: type inference
    verifier.forwardPass();
    
    // Backward pass: verification
    verifier.backwardPass();
    
    // Emit diagnostics
    if (!verifier.verify()) {
      signalPassFailure();
      for (const auto& err : verifier.getErrors()) {
        emitError(module.getLoc(), err);
      }
    }
    
    // Emit warnings (don't fail)
    for (const auto& warn : verifier.getWarnings()) {
      emitWarning(module.getLoc(), warn);
    }
  }
};

/// Register the contractivity verification pass
std::unique_ptr<Pass> createVerifyContractivityPass();

} // namespace mlir::pirtm

#endif // PIRTM_MLIR_PASSES_VERIFY_CONTRACTIVITY_H
