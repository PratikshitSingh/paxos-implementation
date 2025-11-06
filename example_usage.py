"""
Example script demonstrating how to use the Paxos implementation.

This script shows:
1. Creating a cluster of Paxos nodes
2. Running a complete Paxos round
3. Handling node failures
4. Examining consensus results
"""

from paxos import PaxosNode
from main import NodeState, NodeRole, Proposal
from logger import PaxosLogger


def example_basic_consensus():
    """Example: Basic consensus scenario."""
    print("=" * 60)
    print("Example 1: Basic Consensus")
    print("=" * 60)
    
    # Create logger
    logger = PaxosLogger(round=1, filename="example_basic.csv")
    
    # Create 5 nodes
    node_count = 5
    nodes = {}
    
    for i in range(1, node_count + 1):
        nodes[i] = PaxosNode(
            node_id=i,
            role=NodeRole.ACCEPTOR,
            logger=logger,
            node_count=node_count
        )
        print(f"Created node {i}")
    
    # Node 1 acts as proposer
    proposer = nodes[1]
    proposal = Proposal(node_id=1, proposal_number=1, value="example_value")
    
    print(f"\nNode {proposer.node_id} proposing value: {proposal.value}")
    
    # Phase 1: Prepare
    print("\nPhase 1: Prepare")
    proposer.send_prepare(nodes, proposal)
    
    # Collect promises (in real implementation, this would be async)
    print("\nCollecting promises...")
    promises = []
    for node_id, node in nodes.items():
        if node_id != proposer.node_id:
            promise = node.send_promise(proposal)
            if promise:
                promises.append(promise)
                print(f"  Node {node_id} sent promise")
    
    print(f"\nReceived {len(promises)} promises (need {node_count // 2 + 1} for majority)")
    
    # Phase 2: Accept (if we have majority)
    if len(promises) >= (node_count // 2 + 1):
        print("\nPhase 2: Accept")
        proposer.send_accept(nodes, proposal)
        
        # Check acceptances
        total_acceptances = 0
        for node in nodes.values():
            key = (proposal.proposal_number, proposal.value)
            if key in node.acceptance_counts:
                total_acceptances += node.acceptance_counts[key]
        
        print(f"Total acceptances: {total_acceptances}")
        
        if total_acceptances >= (node_count // 2 + 1):
            print(f"\n✓ Consensus reached on value: {proposal.value}")
            
            # Broadcast consensus
            print("\nBroadcasting consensus...")
            for node in nodes.values():
                if node.node_id != proposer.node_id:
                    node.receive_broadcast(proposal)
                    print(f"  Node {node.node_id} received broadcast")
        else:
            print("\n✗ Consensus not reached (not enough acceptances)")
    else:
        print("\n✗ Cannot proceed to accept phase (not enough promises)")
    
    # Save logs
    logger.save_to_csv()
    print(f"\nLogs saved to {logger.filename}")
    print()


def example_node_failure():
    """Example: Consensus with node failures."""
    print("=" * 60)
    print("Example 2: Consensus with Node Failures")
    print("=" * 60)
    
    logger = PaxosLogger(round=1, filename="example_failure.csv")
    node_count = 5
    nodes = {}
    
    for i in range(1, node_count + 1):
        nodes[i] = PaxosNode(
            node_id=i,
            role=NodeRole.ACCEPTOR,
            logger=logger,
            node_count=node_count
        )
    
    # Take down 2 nodes (still have majority: 3 out of 5)
    print("Taking down nodes 4 and 5...")
    nodes[4].state = NodeState.DOWN
    nodes[5].state = NodeState.DOWN
    print(f"Node 4 state: {nodes[4].state.value}")
    print(f"Node 5 state: {nodes[5].state.value}")
    
    # Node 1 acts as proposer
    proposer = nodes[1]
    proposal = Proposal(node_id=1, proposal_number=1, value="survive_failure")
    
    print(f"\nNode {proposer.node_id} proposing value: {proposal.value}")
    
    # Phase 1: Prepare
    print("\nPhase 1: Prepare")
    proposer.send_prepare(nodes, proposal)
    
    # Collect promises from UP nodes only
    print("\nCollecting promises from UP nodes...")
    promises = []
    for node_id, node in nodes.items():
        if node_id != proposer.node_id and node.state == NodeState.UP:
            promise = node.send_promise(proposal)
            if promise:
                promises.append(promise)
                print(f"  Node {node_id} (UP) sent promise")
    
    print(f"\nReceived {len(promises)} promises from UP nodes")
    print(f"Need {node_count // 2 + 1} for majority (out of {node_count} total nodes)")
    
    # Check if we still have majority
    if len(promises) >= (node_count // 2 + 1):
        print("\n✓ Still have majority despite failures!")
        
        # Phase 2: Accept
        print("\nPhase 2: Accept")
        proposer.send_accept(nodes, proposal)
        
        # Check acceptances
        total_acceptances = 0
        for node in nodes.values():
            if node.state == NodeState.UP:
                key = (proposal.proposal_number, proposal.value)
                if key in node.acceptance_counts:
                    total_acceptances += node.acceptance_counts[key]
        
        print(f"Total acceptances from UP nodes: {total_acceptances}")
        
        if total_acceptances >= (node_count // 2 + 1):
            print(f"\n✓ Consensus reached despite node failures!")
    else:
        print("\n✗ Cannot reach consensus (not enough promises)")
    
    logger.save_to_csv()
    print(f"\nLogs saved to {logger.filename}")
    print()


def example_concurrent_proposals():
    """Example: Handling concurrent proposals."""
    print("=" * 60)
    print("Example 3: Concurrent Proposals")
    print("=" * 60)
    
    logger = PaxosLogger(round=1, filename="example_concurrent.csv")
    node_count = 5
    nodes = {}
    
    for i in range(1, node_count + 1):
        nodes[i] = PaxosNode(
            node_id=i,
            role=NodeRole.ACCEPTOR,
            logger=logger,
            node_count=node_count
        )
    
    # Two nodes propose concurrently
    proposal1 = Proposal(node_id=1, proposal_number=1, value="value1")
    proposal2 = Proposal(node_id=2, proposal_number=2, value="value2")
    
    print(f"Node 1 proposing: {proposal1.value} (proposal #1)")
    print(f"Node 2 proposing: {proposal2.value} (proposal #2)")
    
    # Both send prepare
    print("\nBoth nodes sending prepare...")
    nodes[1].send_prepare(nodes, proposal1)
    nodes[2].send_prepare(nodes, proposal2)
    
    # Collect promises for both
    print("\nCollecting promises...")
    promises1 = []
    promises2 = []
    
    for node_id, node in nodes.items():
        if node_id != 1:
            promise = node.send_promise(proposal1)
            if promise:
                promises1.append(promise)
        if node_id != 2:
            promise = node.send_promise(proposal2)
            if promise:
                promises2.append(promise)
    
    print(f"Proposal 1 received {len(promises1)} promises")
    print(f"Proposal 2 received {len(promises2)} promises")
    
    # In real Paxos, higher proposal number wins
    # Here we just demonstrate that both can get promises
    print("\nNote: In real Paxos, the proposal with higher number typically wins")
    
    logger.save_to_csv()
    print(f"\nLogs saved to {logger.filename}")
    print()


if __name__ == "__main__":
    print("\nPaxos Implementation Examples")
    print("=" * 60)
    print()
    
    # Run examples
    example_basic_consensus()
    example_node_failure()
    example_concurrent_proposals()
    
    print("=" * 60)
    print("All examples completed!")
    print("=" * 60)


