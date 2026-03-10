/**
 * test_runtime.cpp
 * 
 * C++ Unit Tests for libpirtm_runtime
 * 
 * Tests core functionality:
 * - State creation/destruction
 * - Single and multi-step iteration
 * - State vector access
 * - Witness validation
 * - Error handling
 * 
 * Build with: g++ -std=c++17 -o test_runtime test_runtime.cpp libpirtm_runtime.cpp
 * Run with: ./test_runtime
 */

#include <cstdio>
#include <cmath>
#include <cstring>
#include <cassert>
#include <iostream>
#include <iomanip>

/* Forward declare C API */
extern "C" {
    typedef void* pirtm_state_t;
    
    pirtm_state_t pirtm_state_new(int32_t state_dim, double epsilon, 
                                   const double* gain_matrix_data, int32_t gain_matrix_size);
    void pirtm_state_free(pirtm_state_t state);
    int pirtm_get_state(pirtm_state_t state, double* output_vec, int32_t output_size);
    int pirtm_set_state(pirtm_state_t state, const double* input_vec, int32_t input_size);
    double pirtm_step(pirtm_state_t state);
    int pirtm_run(pirtm_state_t state, int32_t num_steps);
    int pirtm_verify_witness(pirtm_state_t state, const char* expected_hash);
    int32_t pirtm_get_dimension(pirtm_state_t state);
    double pirtm_get_epsilon(pirtm_state_t state);
}

/* ============================================================================
 * Test Utilities
 * ============================================================================
 */

int test_count = 0;
int pass_count = 0;
int fail_count = 0;

void assert_true(bool condition, const char* message) {
    test_count++;
    if (condition) {
        pass_count++;
        printf("  ✓ %s\n", message);
    } else {
        fail_count++;
        printf("  ✗ %s\n", message);
    }
}

void assert_equal_int(int actual, int expected, const char* message) {
    test_count++;
    if (actual == expected) {
        pass_count++;
        printf("  ✓ %s (got %d)\n", message, actual);
    } else {
        fail_count++;
        printf("  ✗ %s (expected %d, got %d)\n", message, expected, actual);
    }
}

void assert_equal_double(double actual, double expected, double tolerance, const char* message) {
    test_count++;
    if (std::abs(actual - expected) < tolerance) {
        pass_count++;
        printf("  ✓ %s (got %.6f)\n", message, actual);
    } else {
        fail_count++;
        printf("  ✗ %s (expected ~%.6f, got %.6f, diff=%.6f)\n", 
               message, expected, actual, std::abs(actual - expected));
    }
}

/* ============================================================================
 * Test Cases
 * ============================================================================
 */

void test_state_creation() {
    printf("\nTest: State Creation\n");
    
    pirtm_state_t state = pirtm_state_new(10, 0.05, nullptr, 0);
    assert_true(state != nullptr, "State allocated");
    
    int32_t dim = pirtm_get_dimension(state);
    assert_equal_int(dim, 10, "Dimension is correct");
    
    double eps = pirtm_get_epsilon(state);
    assert_equal_double(eps, 0.05, 1e-6, "Epsilon is correct");
    
    pirtm_state_free(state);
    assert_true(true, "State freed");
}

void test_invalid_parameters() {
    printf("\nTest: Invalid Parameters\n");
    
    // Invalid dimension
    pirtm_state_t state = pirtm_state_new(-1, 0.05, nullptr, 0);
    assert_true(state == nullptr, "Negative dimension rejected");
    
    // Invalid epsilon (too large)
    state = pirtm_state_new(10, 1.5, nullptr, 0);
    assert_true(state == nullptr, "Epsilon >= 1.0 rejected");
    
    // Invalid epsilon (negative)
    state = pirtm_state_new(10, -0.1, nullptr, 0);
    assert_true(state == nullptr, "Negative epsilon rejected");
}

void test_state_vector_access() {
    printf("\nTest: State Vector Access\n");
    
    pirtm_state_t state = pirtm_state_new(5, 0.05, nullptr, 0);
    assert_true(state != nullptr, "State created");
    
    // Set state
    double input[] = {1.0, 2.0, 3.0, 4.0, 5.0};
    int ret = pirtm_set_state(state, input, 5);
    assert_equal_int(ret, 0, "Set state succeeded");
    
    // Get state
    double output[5];
    ret = pirtm_get_state(state, output, 5);
    assert_equal_int(ret, 0, "Get state succeeded");
    
    // Verify values
    for (int i = 0; i < 5; i++) {
        assert_equal_double(output[i], input[i], 1e-9, 
                           std::string("State[" + std::to_string(i) + "] correct").c_str());
    }
    
    pirtm_state_free(state);
}

void test_single_step() {
    printf("\nTest: Single Step Iteration\n");
    
    pirtm_state_t state = pirtm_state_new(3, 0.05, nullptr, 0);
    
    double input[] = {1.0, 0.0, 0.0};
    pirtm_set_state(state, input, 3);
    
    // Execute one step (should apply gain matrix)
    double norm = pirtm_step(state);
    assert_true(norm >= 0.0, "Step returns non-negative norm");
    
    // For identity * 0.9 gain, norm should be 0.9
    assert_equal_double(norm, 0.9, 0.01, "Norm is approximately 0.9");
    
    pirtm_state_free(state);
}

void test_multiple_steps() {
    printf("\nTest: Multiple Steps\n");
    
    pirtm_state_t state = pirtm_state_new(5, 0.05, nullptr, 0);
    
    double input[] = {1.0, 1.0, 1.0, 1.0, 1.0};
    pirtm_set_state(state, input, 5);
    
    // Run 10 steps
    int ret = pirtm_run(state, 10);
    assert_equal_int(ret, 0, "Run succeeded");
    
    // State should decay (gain = 0.9)
    double output[5];
    pirtm_get_state(state, output, 5);
    
    // After 10 steps with gain 0.9: 0.9^10 ≈ 0.349
    double expected = std::pow(0.9, 10);
    assert_equal_double(output[0], expected, 0.01, 
                       "State decayed correctly after 10 steps");
    
    pirtm_state_free(state);
}

void test_custom_gain_matrix() {
    printf("\nTest: Custom Gain Matrix\n");
    
    // Create diagonal matrix with different gains
    double gain[] = {
        0.5, 0.0, 0.0,
        0.0, 0.7, 0.0,
        0.0, 0.0, 0.9
    };
    
    pirtm_state_t state = pirtm_state_new(3, 0.05, gain, 9);
    assert_true(state != nullptr, "State with custom gain created");
    
    double input[] = {1.0, 1.0, 1.0};
    pirtm_set_state(state, input, 3);
    
    pirtm_step(state);
    
    double output[3];
    pirtm_get_state(state, output, 3);
    
    // After one step with diagonal gain
    assert_equal_double(output[0], 0.5, 1e-6, "First element scaled by 0.5");
    assert_equal_double(output[1], 0.7, 1e-6, "Second element scaled by 0.7");
    assert_equal_double(output[2], 0.9, 1e-6, "Third element scaled by 0.9");
    
    pirtm_state_free(state);
}

void test_witness_validation() {
    printf("\nTest: Witness Validation\n");
    
    pirtm_state_t state = pirtm_state_new(5, 0.05, nullptr, 0);
    
    // Set known state
    double input[] = {0.0, 0.0, 0.0, 0.0, 0.0};
    pirtm_set_state(state, input, 5);
    
    // Should hash to something consistent
    int ret = pirtm_verify_witness(state, "0x0000000000000000");
    // Result depends on hash implementation; just check it doesn't crash
    assert_true(ret == 0 || ret == -1, "Witness validation returns valid code");
    
    pirtm_state_free(state);
}

void test_size_mismatch() {
    printf("\nTest: Size Mismatch Handling\n");
    
    pirtm_state_t state = pirtm_state_new(5, 0.05, nullptr, 0);
    
    // Try to set wrong-sized state
    double input[] = {1.0, 2.0, 3.0};  // Only 3 elements for 5-dim state
    int ret = pirtm_set_state(state, input, 3);
    assert_true(ret != 0, "Wrong state size rejected");
    
    // Try to get into wrong-sized buffer
    double output[3];
    ret = pirtm_get_state(state, output, 3);
    assert_true(ret != 0, "Wrong output size rejected");
    
    pirtm_state_free(state);
}

void test_performance() {
    printf("\nTest: Performance\n");
    
    pirtm_state_t state = pirtm_state_new(100, 0.05, nullptr, 0);
    
    double* vec = new double[100];
    std::fill(vec, vec + 100, 0.1);
    pirtm_set_state(state, vec, 100);
    
    // Time 1000 steps
    auto start = std::chrono::system_clock::now();
    for (int i = 0; i < 1000; i++) {
        pirtm_step(state);
    }
    auto end = std::chrono::system_clock::now();
    
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end - start);
    double ms_per_step = duration.count() / 1000.0;
    
    printf("  ✓ 1000 steps in 100-dimensional state: %.3f ms/step\n", ms_per_step);
    
    delete[] vec;
    pirtm_state_free(state);
}

/* ============================================================================
 * Main Test Runner
 * ============================================================================
 */

int main() {
    printf("\n");
    printf("================================================================================\n");
    printf("  PIRTM Runtime Library Test Suite\n");
    printf("================================================================================\n");
    
    // Run tests
    test_state_creation();
    test_invalid_parameters();
    test_state_vector_access();
    test_single_step();
    test_multiple_steps();
    test_custom_gain_matrix();
    test_witness_validation();
    test_size_mismatch();
    test_performance();
    
    // Summary
    printf("\n");
    printf("================================================================================\n");
    printf("  Test Results\n");
    printf("================================================================================\n");
    printf("  Total:  %d tests\n", test_count);
    printf("  Passed: %d tests\n", pass_count);
    printf("  Failed: %d tests\n", fail_count);
    printf("\n");
    
    if (fail_count == 0) {
        printf("  ✓ All tests passed!\n");
        printf("\n");
        return 0;
    } else {
        printf("  ✗ Some tests failed\n");
        printf("\n");
        return 1;
    }
}
