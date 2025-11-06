# Testing Guide for Paxos Implementation

This guide explains how to test the Paxos consensus algorithm implementation.

## Running Tests

### Using unittest (built-in)

Run all tests:
```bash
python test_paxos.py
```

Run with verbose output:
```bash
python test_paxos.py -v
```

### Using pytest (recommended)

First install pytest:
```bash
pip install pytest
```

Then run tests:
```bash
pytest test_paxos.py -v
```

Run specific test class:
```bash
pytest test_paxos.py::TestPaxosBasic -v
```

Run specific test:
```bash
pytest test_paxos.py::TestPaxosBasic::test_basic_consensus -v
```

## Test Suites

The test suite is organized into several test classes:

### 1. `TestPaxosBasic`
Tests basic consensus scenarios:
- `test_basic_consensus`: Tests that a simple consensus can be reached
- `test_majority_consensus`: Tests that consensus requires a majority
- `test_node_down_prevents_consensus`: Tests that too many down nodes prevent consensus

### 2. `TestPaxosFailures`
Tests node failure scenarios:
- `test_proposer_goes_down`: Tests behavior when proposer goes down
- `test_acceptor_goes_down_during_prepare`: Tests acceptor failure during prepare phase
- `test_consensus_with_some_nodes_down`: Tests that consensus can still be reached with some nodes down

### 3. `TestPaxosConcurrent`
Tests concurrent proposal scenarios:
- `test_concurrent_proposals`: Tests handling of concurrent proposals from different nodes

### 4. `TestPaxosEdgeCases`
Tests edge cases:
- `test_single_node_consensus`: Tests consensus with minimal nodes (3 nodes)
- `test_consensus_value_persistence`: Tests that consensus value persists across nodes
- `test_broadcast_reception`: Tests that nodes can receive broadcast messages
- `test_consensus_flag_reset`: Tests that consensus_reached flag is properly reset

### 5. `TestPaxosIntegration`
Integration tests:
- `test_full_paxos_round`: Tests a complete Paxos round from prepare to accept

## Manual Testing

You can also test the implementation manually using the example script:

```bash
python example_usage.py
```

This script demonstrates:
- Creating nodes
- Running a complete Paxos round
- Handling node failures
- Examining consensus results

## Test Output

Each test generates a CSV log file:
- `test_basic.csv`: Basic consensus tests
- `test_failures.csv`: Failure scenario tests
- `test_concurrent.csv`: Concurrent proposal tests
- `test_edge.csv`: Edge case tests
- `test_integration.csv`: Integration tests

These CSV files contain detailed logs of all Paxos messages and state changes during the tests.

## Understanding Test Results

### Successful Test Output
```
test_basic_consensus (__main__.TestPaxosBasic) ... ok
test_majority_consensus (__main__.TestPaxosBasic) ... ok
```

### Failed Test Output
```
test_basic_consensus (__main__.TestPaxosBasic) ... FAIL
AssertionError: At least one acceptance should be recorded
```

Check the CSV log files to understand what happened during failed tests.

## Adding New Tests

To add new tests:

1. Create a new test method in an existing test class, or create a new test class
2. Follow the pattern:
   ```python
   def test_your_scenario(self):
       """Test description."""
       # Setup
       # Execute
       # Assert
   ```
3. Use assertions to verify expected behavior:
   - `self.assertEqual(expected, actual)`
   - `self.assertGreater(value, threshold)`
   - `self.assertTrue(condition)`
   - etc.

## Common Test Scenarios to Add

Consider adding tests for:
- Network partition scenarios
- Message loss simulation
- Byzantine failures (if supported)
- Performance under load
- Consensus recovery after failures
- Multiple consecutive consensus rounds


