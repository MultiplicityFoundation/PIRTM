/**
 * libpirtm_runtime.cpp
 * 
 * C Runtime Library for PIRTM Phase 4 Standalone Execution
 * 
 * Implements state management, recurrence iteration, and witness validation.
 * Designed for Python ctypes integration with zero-copy state access.
 * 
 * Related: ADR-009-llvm-compilation.md, pirtm_runtime_bindings.py
 */

#include <cstring>
#include <cmath>
#include <cstdlib>
#include <cstdint>
#include <algorithm>
#include <stdexcept>

/* ============================================================================
 * C API Header (embedded for clarity)
 * ============================================================================
 */

extern "C" {

/* Opaque state handle */
typedef void* pirtm_state_t;

/* State creation/destruction */
pirtm_state_t pirtm_state_new(
    int32_t state_dim,
    double epsilon,
    const double* gain_matrix_data,
    int32_t gain_matrix_size
);

void pirtm_state_free(pirtm_state_t state);

/* State access */
int pirtm_get_state(pirtm_state_t state, double* output_vec, int32_t output_size);
int pirtm_set_state(pirtm_state_t state, const double* input_vec, int32_t input_size);

/* Execution */
double pirtm_step(pirtm_state_t state);
int pirtm_run(pirtm_state_t state, int32_t num_steps);

/* Witness validation */
int pirtm_verify_witness(pirtm_state_t state, const char* expected_hash);

/* Metadata access */
int32_t pirtm_get_dimension(pirtm_state_t state);
double pirtm_get_epsilon(pirtm_state_t state);

} // extern "C"

/* ============================================================================
 * Internal State Structure
 * ============================================================================
 */

namespace pirtm {
namespace runtime {

/**
 * PirtmState: Core execution state
 * 
 * Layout:
 * - state_vec: Current state vector (dimension elements)
 * - gain_matrix: Gain matrix for coupling (dimension × dimension)
 * - dimension: State dimensionality
 * - epsilon: Contractivity margin
 * - step_count: Total steps executed
 * - state_hash: Commitment hash for witness validation
 */
class PirtmState {
public:
    int32_t dimension;
    double epsilon;
    double* state_vec;      // dimension elements
    double* gain_matrix;    // dimension × dimension elements
    int64_t step_count;
    uint64_t state_hash;
    
    /**
     * Create uninitialized state.
     * Must call init() before use.
     */
    PirtmState()
        : dimension(0), epsilon(0.0), state_vec(nullptr), gain_matrix(nullptr),
          step_count(0), state_hash(0) {}
    
    /**
     * Initialize state with given parameters.
     * Allocates vectors and matrices.
     */
    bool init(int32_t dim, double eps, const double* gain_data, int32_t gain_size) {
        if (dim <= 0 || eps < 0.0 || eps >= 1.0) {
            return false;
        }
        
        dimension = dim;
        epsilon = eps;
        step_count = 0;
        state_hash = 0;
        
        // Allocate state vector
        state_vec = new double[dimension];
        if (!state_vec) return false;
        std::fill(state_vec, state_vec + dimension, 0.0);
        
        // Allocate and initialize gain matrix
        gain_matrix = new double[dimension * dimension];
        if (!gain_matrix) {
            delete[] state_vec;
            state_vec = nullptr;
            return false;
        }
        
        // Copy gain matrix (or zero if not provided)
        if (gain_data && gain_size == dimension * dimension) {
            std::copy(gain_data, gain_data + gain_size, gain_matrix);
        } else {
            // Default: identity matrix * 0.9 (stable contraction)
            std::fill(gain_matrix, gain_matrix + dimension * dimension, 0.0);
            for (int i = 0; i < dimension; i++) {
                gain_matrix[i * dimension + i] = 0.9;
            }
        }
        
        return true;
    }
    
    /**
     * Single iteration of recurrence: x_{k+1} = G * x_k
     * 
     * Returns: || x_{k+1} ||_2
     */
    double step() {
        if (!state_vec || !gain_matrix) {
            return 0.0;
        }
        
        // Allocate temporary for matrix-vector product
        double* temp = new double[dimension];
        if (!temp) return -1.0;
        
        // Compute temp = gain_matrix * state_vec
        for (int i = 0; i < dimension; i++) {
            temp[i] = 0.0;
            for (int j = 0; j < dimension; j++) {
                temp[i] += gain_matrix[i * dimension + j] * state_vec[j];
            }
        }
        
        // Copy back to state_vec
        std::copy(temp, temp + dimension, state_vec);
        delete[] temp;
        
        // Compute and return norm
        double norm_sq = 0.0;
        for (int i = 0; i < dimension; i++) {
            norm_sq += state_vec[i] * state_vec[i];
        }
        
        step_count++;
        update_hash();
        
        return std::sqrt(norm_sq);
    }
    
    /**
     * Run num_steps iterations.
     * Returns: 0 on success, non-zero on error
     */
    int run(int32_t num_steps) {
        if (num_steps < 0) return -1;
        if (!state_vec || !gain_matrix) return -1;
        
        for (int32_t i = 0; i < num_steps; i++) {
            double norm = step();
            if (std::isnan(norm) || std::isinf(norm)) {
                return -1;
            }
        }
        
        return 0;
    }
    
    /**
     * Get current state vector.
     * Copies state_vec into output buffer (zero-copy safe).
     */
    int get_state(double* output_vec, int32_t output_size) {
        if (!state_vec || output_size != dimension) {
            return -1;
        }
        std::copy(state_vec, state_vec + dimension, output_vec);
        return 0;
    }
    
    /**
     * Set current state vector.
     * Copies input buffer into state_vec.
     */
    int set_state(const double* input_vec, int32_t input_size) {
        if (!state_vec || input_size != dimension) {
            return -1;
        }
        
        // Validate: no NaN or Inf
        for (int i = 0; i < input_size; i++) {
            if (!std::isfinite(input_vec[i])) {
                return -1;
            }
        }
        
        std::copy(input_vec, input_vec + dimension, state_vec);
        update_hash();
        return 0;
    }
    
    /**
     * Verify witness (ACE commitment hash).
     * 
     * Simple implementation: Compare expected_hash with current state_hash.
     * Expected format: "0x" followed by 16 hex digits.
     */
    int verify_witness(const char* expected_hash) {
        if (!expected_hash || std::strlen(expected_hash) < 3) {
            return -1;  // Invalid hash format
        }
        
        // Parse expected hash (simple hex parsing)
        uint64_t expected = 0;
        int result = std::sscanf(expected_hash, "0x%lx", &expected);
        if (result != 1) {
            return -1;  // Parse error
        }
        
        // Compare with current state hash
        return (state_hash == expected) ? 0 : -1;
    }
    
    /**
     * Cleanup: deallocate vectors and matrices.
     */
    void cleanup() {
        if (state_vec) {
            delete[] state_vec;
            state_vec = nullptr;
        }
        if (gain_matrix) {
            delete[] gain_matrix;
            gain_matrix = nullptr;
        }
        dimension = 0;
    }
    
    /**
     * Virtual destructor (for safety).
     */
    virtual ~PirtmState() {
        cleanup();
    }

private:
    /**
     * Update state commitment hash.
     * Simple hash: XOR of all state elements (as uint64_t bits).
     */
    void update_hash() {
        state_hash = 0;
        for (int i = 0; i < dimension; i++) {
            uint64_t bits;
            std::memcpy(&bits, &state_vec[i], sizeof(double));
            state_hash ^= bits;
        }
    }
};

} // namespace runtime
} // namespace pirtm

/* ============================================================================
 * C API Implementation
 * ============================================================================
 */

using namespace pirtm::runtime;

/**
 * pirtm_state_new: Create new state.
 * 
 * Parameters:
 *   state_dim: State dimensionality (must be > 0)
 *   epsilon: Contractivity margin [0, 1)
 *   gain_matrix_data: Optional gain matrix (can be NULL for identity)
 *   gain_matrix_size: Size of gain_matrix_data (must be state_dim^2 if non-NULL)
 * 
 * Returns: Opaque handle, or NULL on error
 */
extern "C"
pirtm_state_t pirtm_state_new(
    int32_t state_dim,
    double epsilon,
    const double* gain_matrix_data,
    int32_t gain_matrix_size)
{
    if (state_dim <= 0 || epsilon < 0.0 || epsilon >= 1.0) {
        return nullptr;
    }
    
    if (gain_matrix_data && gain_matrix_size != state_dim * state_dim) {
        return nullptr;
    }
    
    PirtmState* state = new PirtmState();
    if (!state) return nullptr;
    
    if (!state->init(state_dim, epsilon, gain_matrix_data, gain_matrix_size)) {
        delete state;
        return nullptr;
    }
    
    return static_cast<pirtm_state_t>(state);
}

/**
 * pirtm_state_free: Destroy state and free resources.
 */
extern "C"
void pirtm_state_free(pirtm_state_t state)
{
    if (!state) return;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    delete s;
}

/**
 * pirtm_step: Execute single iteration.
 * 
 * Returns: State norm (>= 0), or negative value on error
 */
extern "C"
double pirtm_step(pirtm_state_t state)
{
    if (!state) return -1.0;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    return s->step();
}

/**
 * pirtm_run: Execute num_steps iterations.
 * 
 * Returns: 0 on success, non-zero on error
 */
extern "C"
int pirtm_run(pirtm_state_t state, int32_t num_steps)
{
    if (!state || num_steps < 0) return -1;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    return s->run(num_steps);
}

/**
 * pirtm_get_state: Read current state vector.
 * 
 * Copies state into output_vec (must be pre-allocated).
 * 
 * Returns: 0 on success, non-zero on error
 */
extern "C"
int pirtm_get_state(pirtm_state_t state, double* output_vec, int32_t output_size)
{
    if (!state || !output_vec) return -1;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    return s->get_state(output_vec, output_size);
}

/**
 * pirtm_set_state: Write state vector.
 * 
 * Copies input_vec into state.
 * Validates that all elements are finite (no NaN/Inf).
 * 
 * Returns: 0 on success, non-zero on error
 */
extern "C"
int pirtm_set_state(pirtm_state_t state, const double* input_vec, int32_t input_size)
{
    if (!state || !input_vec) return -1;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    return s->set_state(input_vec, input_size);
}

/**
 * pirtm_verify_witness: Validate ACE witness commitment.
 * 
 * Compares state hash against expected_hash in format "0x[hex]".
 * 
 * Returns: 0 if match, non-zero if mismatch or error
 */
extern "C"
int pirtm_verify_witness(pirtm_state_t state, const char* expected_hash)
{
    if (!state || !expected_hash) return -1;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    return s->verify_witness(expected_hash);
}

/**
 * pirtm_get_dimension: Query state dimension.
 * 
 * Returns: Dimension, or -1 on error
 */
extern "C"
int32_t pirtm_get_dimension(pirtm_state_t state)
{
    if (!state) return -1;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    return s->dimension;
}

/**
 * pirtm_get_epsilon: Query contractivity margin.
 * 
 * Returns: Epsilon value (0 if error)
 */
extern "C"
double pirtm_get_epsilon(pirtm_state_t state)
{
    if (!state) return 0.0;
    
    PirtmState* s = static_cast<PirtmState*>(state);
    return s->epsilon;
}

/* ============================================================================
 * End libpirtm_runtime.cpp
 * ============================================================================
 */
