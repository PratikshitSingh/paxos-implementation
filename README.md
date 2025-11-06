# Paxos Consensus Algorithm Implementation

This is an implementation of the Paxos consensus algorithm in Python.

## Files

- `paxos.py`: Core Paxos algorithm implementation (`PaxosNode` class)
- `main.py`: Supporting classes and enums (`NodeState`, `NodeRole`, `Proposal`, etc.)
- `logger.py`: Logging functionality (`PaxosLogger` class)
- `test_paxos.py`: Comprehensive test suite
- `example_usage.py`: Example scripts demonstrating Paxos usage
- `TESTING_GUIDE.md`: Detailed testing guide

## Quick Start

### Running Tests

Run all tests:
```bash
python test_paxos.py
```

Run with verbose output:
```bash
python test_paxos.py -v
```

### Running Examples

See examples of Paxos in action:
```bash
python example_usage.py
```

## Testing

The test suite includes:
- **Basic consensus scenarios**: Simple consensus, majority requirements
- **Failure scenarios**: Node failures, proposer/acceptor failures
- **Concurrent proposals**: Handling multiple proposals
- **Edge cases**: Minimal nodes, value persistence, broadcasts
- **Integration tests**: Complete Paxos rounds

See `TESTING_GUIDE.md` for detailed testing information.

## Test Results

All tests should pass. The test suite generates CSV log files for each test category:
- `test_basic.csv`
- `test_failures.csv`
- `test_concurrent.csv`
- `test_edge.csv`
- `test_integration.csv`

## Usage Example

```python
from paxos import PaxosNode
from main import NodeState, NodeRole, Proposal
from logger import PaxosLogger

# Create logger
logger = PaxosLogger(round=1, filename="paxosresult.csv")

# Create nodes
node_count = 5
nodes = {}
for i in range(1, node_count + 1):
    nodes[i] = PaxosNode(
        node_id=i,
        role=NodeRole.ACCEPTOR,
        logger=logger,
        node_count=node_count
    )

# Node 1 proposes
proposer = nodes[1]
proposal = Proposal(node_id=1, proposal_number=1, value="my_value")

# Phase 1: Prepare
proposer.send_prepare(nodes, proposal)

# Collect promises
promises = []
for node_id, node in nodes.items():
    if node_id != proposer.node_id:
        promise = node.send_promise(proposal)
        if promise:
            promises.append(promise)

# Phase 2: Accept (if majority)
if len(promises) >= (node_count // 2 + 1):
    proposer.send_accept(nodes, proposal)

# Save logs
logger.save_to_csv()
```

## Features

- Complete Paxos implementation with prepare, promise, accept phases
- Node failure handling
- Detailed logging of all Paxos messages
- Comprehensive test coverage
- Example scripts for learning

## Requirements

Python 3.6+ (uses standard library only)


