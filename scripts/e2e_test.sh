#!/usr/bin/env bash

# End-to-End Test Script for DSPy Prompt Optimizer
# Tests all CLI subcommands to ensure functionality works as expected

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Test data
TEST_DIR=$(mktemp -d)
TEST_PROMPT_FILE="$TEST_DIR/test_prompt.txt"
EXAMPLES_FILE="$TEST_DIR/examples.json"
OUTPUT_FILE="$TEST_DIR/output.txt"

# Sample test prompt
TEST_PROMPT="Analyze the given text and provide a summary of the main points."

echo -e "${BLUE}=== DSPy Prompt Optimizer E2E Test Suite ===${NC}"
echo "Test directory: $TEST_DIR"
echo

# Function to log test results
log_test() {
  local test_name="$1"
  local status="$2"
  local details="${3:-}"

  TOTAL_TESTS=$((TOTAL_TESTS + 1))

  if [[ "$status" == "PASS" ]]; then
    echo -e "${GREEN}✓ PASS${NC}: $test_name"
    PASSED_TESTS=$((PASSED_TESTS + 1))
  elif [[ "$status" == "FAIL" ]]; then
    echo -e "${RED}✗ FAIL${NC}: $test_name"
    [[ -n "$details" ]] && echo -e "  ${RED}Error:${NC} $details"
    FAILED_TESTS=$((FAILED_TESTS + 1))
  elif [[ "$status" == "SKIP" ]]; then
    echo -e "${YELLOW}⚠ SKIP${NC}: $test_name"
    [[ -n "$details" ]] && echo -e "  ${YELLOW}Reason:${NC} $details"
  fi
}

# Function to check if API key is available
check_api_key() {
  if [[ -z "${ANTHROPIC_API_KEY:-}" ]]; then
    echo -e "${RED}ERROR: ANTHROPIC_API_KEY environment variable is not set${NC}"
    echo "Please set your Anthropic API key:"
    echo "  export ANTHROPIC_API_KEY='your-api-key-here'"
    exit 1
  fi
}

# Function to create test prompt file
setup_test_data() {
  echo "$TEST_PROMPT" >"$TEST_PROMPT_FILE"
}

# Function to run a CLI command and capture output
run_cli_test() {
  local test_name="$1"
  local cmd="$2"
  local expected_pattern="${3:-}"
  local should_succeed="${4:-true}"

  echo -e "${BLUE}Running:${NC} $cmd"

  if timeout 60s bash -c "$cmd" >"$OUTPUT_FILE" 2>&1; then
    if [[ "$should_succeed" == "true" ]]; then
      if [[ -n "$expected_pattern" ]]; then
        if grep -q "$expected_pattern" "$OUTPUT_FILE"; then
          log_test "$test_name" "PASS"
        else
          log_test "$test_name" "FAIL" "Output doesn't contain expected pattern: $expected_pattern"
          echo "=== Command Output ==="
          cat "$OUTPUT_FILE"
          echo "===================="
        fi
      else
        log_test "$test_name" "PASS"
      fi
    else
      log_test "$test_name" "FAIL" "Command should have failed but succeeded"
    fi
  else
    if [[ "$should_succeed" == "false" ]]; then
      log_test "$test_name" "PASS"
    else
      log_test "$test_name" "FAIL" "Command failed unexpectedly"
      echo "=== Command Output ==="
      cat "$OUTPUT_FILE" || echo "(no output file)"
      echo "===================="
    fi
  fi
  echo
}

# Function to cleanup
cleanup() {
  echo -e "${BLUE}Cleaning up test directory: $TEST_DIR${NC}"
  rm -rf "$TEST_DIR"
}

# Trap to ensure cleanup happens
trap cleanup EXIT

# Main test execution
main() {
  echo -e "${BLUE}=== Pre-flight Checks ===${NC}"

  # Check API key
  check_api_key
  echo -e "${GREEN}✓${NC} ANTHROPIC_API_KEY is set"

  # Setup test data
  setup_test_data
  echo -e "${GREEN}✓${NC} Test data created"

  # Check if we can run the CLI
  if poetry run dspy-prompt-optimizer -- --help >/dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} CLI is accessible via poetry"
  else
    echo -e "${RED}✗${NC} Cannot access CLI via poetry"
    exit 1
  fi
  echo

  echo -e "${BLUE}=== Testing CLI Help and Version ===${NC}"

  # Test main help
  run_cli_test "Main help command" \
    "poetry run dspy-prompt-optimizer -- --help" \
    "DSPy Prompt Optimizer"

  # Test subcommand help
  run_cli_test "Self-refinement help" \
    "poetry run dspy-prompt-optimizer -- self --help" \
    "self-refinement approach"

  run_cli_test "Example-based help" \
    "poetry run dspy-prompt-optimizer -- example --help" \
    "example-based approach"

  # Test that new flags are documented in help
  run_cli_test "Example-based help (new flags)" \
    "poetry run dspy-prompt-optimizer -- example --help" \
    "example-generator-max-tokens"

  run_cli_test "Metric-based help" \
    "poetry run dspy-prompt-optimizer -- metric --help" \
    "metric-based approach"

  run_cli_test "Generate-examples help" \
    "poetry run dspy-prompt-optimizer -- generate-examples --help" \
    "Generate examples for prompt optimization"

  echo -e "${BLUE}=== Testing Error Handling ===${NC}"

  # Test missing API key
  run_cli_test "Missing API key error" \
    "ANTHROPIC_API_KEY= poetry run dspy-prompt-optimizer -- self < '$TEST_PROMPT_FILE'" \
    "Anthropic API key is required" \
    false

  # Test invalid file input
  run_cli_test "Invalid input file" \
    "poetry run dspy-prompt-optimizer -- self /nonexistent/file.txt" \
    "" \
    false

  echo -e "${BLUE}=== Testing Core Functionality ===${NC}"

  # Test self-refinement optimizer
  run_cli_test "Self-refinement optimization" \
    "poetry run dspy-prompt-optimizer -- self --verbose < '$TEST_PROMPT_FILE'" \
    "Optimizing prompt using self-refinement approach"

  # Test metric-based optimizer
  run_cli_test "Metric-based optimization" \
    "poetry run dspy-prompt-optimizer -- metric --verbose --max-iterations 2 < '$TEST_PROMPT_FILE'" \
    "Optimizing prompt using metric-based approach"

  echo -e "${BLUE}=== Testing Example Generation and Usage ===${NC}"

  # Test example generation
  run_cli_test "Example generation" \
    "poetry run dspy-prompt-optimizer -- generate-examples --verbose --num-examples 2 --max-tokens 4000 '$EXAMPLES_FILE'" \
    "Examples saved to"

  # Test if examples file was created and has content
  if [[ -f "$EXAMPLES_FILE" && -s "$EXAMPLES_FILE" ]]; then
    log_test "Examples file creation" "PASS"

    # Test example-based optimization with generated examples
    run_cli_test "Example-based optimization (with file)" \
      "poetry run dspy-prompt-optimizer -- example --verbose --examples-file '$EXAMPLES_FILE' < '$TEST_PROMPT_FILE'" \
      "Optimizing prompt using example-based approach"
  else
    log_test "Examples file creation" "FAIL" "Examples file not created or empty"
    log_test "Example-based optimization (with file)" "SKIP" "No examples file available"
  fi

  # Test example-based optimization without pre-generated examples (one-phase)
  run_cli_test "Example-based optimization (one-phase)" \
    "poetry run dspy-prompt-optimizer -- example --verbose --num-examples 2 < '$TEST_PROMPT_FILE'" \
    "Optimizing prompt using example-based approach"

  # Test example-based optimization with separate max-tokens for generator and optimizer
  run_cli_test "Example-based optimization (separate max-tokens)" \
    "poetry run dspy-prompt-optimizer -- example --verbose --max-tokens 4000 --example-generator-max-tokens 2000 --num-examples 2 < '$TEST_PROMPT_FILE'" \
    "example_generator_max_tokens=2000"

  echo -e "${BLUE}=== Testing Output Options ===${NC}"

  # Test output to file
  local output_test_file="$TEST_DIR/output_test.txt"
  run_cli_test "Output to file" \
    "poetry run dspy-prompt-optimizer -- self --output '$output_test_file' < '$TEST_PROMPT_FILE'"

  if [[ -f "$output_test_file" && -s "$output_test_file" ]]; then
    log_test "Output file creation" "PASS"
  else
    log_test "Output file creation" "FAIL" "Output file not created or empty"
  fi

  echo -e "${BLUE}=== Testing Model and Token Options ===${NC}"

  # Test different model
  run_cli_test "Different model option" \
    "poetry run dspy-prompt-optimizer -- self --model claude-3-5-haiku-latest --verbose < '$TEST_PROMPT_FILE'" \
    "claude-3-5-haiku-latest"

  # Test custom max tokens
  run_cli_test "Custom max tokens" \
    "poetry run dspy-prompt-optimizer -- self --max-tokens 1000 --verbose < '$TEST_PROMPT_FILE'" \
    "max_tokens=1000"

  echo -e "${BLUE}=== Test Summary ===${NC}"
  echo "Total tests: $TOTAL_TESTS"
  echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}"
  echo -e "Failed: ${RED}$FAILED_TESTS${NC}"
  echo

  if [[ $FAILED_TESTS -eq 0 ]]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    exit 0
  else
    echo -e "${RED}❌ Some tests failed.${NC}"
    exit 1
  fi
}

# Run main function
main "$@"
