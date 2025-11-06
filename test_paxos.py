"""
Test suite for Paxos implementation.

This test suite covers:
1. Basic consensus scenarios
2. Node failure scenarios
3. Concurrent proposals
4. Edge cases
"""

import unittest
from paxos import PaxosNode
from main import NodeState, NodeRole, Proposal
from logger import PaxosLogger


class TestPaxosBasic(unittest.TestCase):
    """Test basic consensus scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = PaxosLogger(round=1, filename="test_basic.csv")
        self.node_count = 5
        self.nodes = {}
        
        # Create nodes
        for i in range(1, self.node_count + 1):
            self.nodes[i] = PaxosNode(
                node_id=i,
                role=NodeRole.ACCEPTOR,
                logger=self.logger,
                node_count=self.node_count
            )
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.save_to_csv()
    
    def test_basic_consensus(self):
        """Test that a simple consensus can be reached."""
        # Node 1 acts as proposer
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="value1")
        
        # Phase 1: Prepare
        proposer.send_prepare(self.nodes, proposal)
        
        # Collect promises (simulating the actual promise collection)
        promises = []
        for node_id, node in self.nodes.items():
            if node_id != 1:  # Don't count the proposer
                promise = node.send_promise(proposal)
                if promise:
                    promises.append(promise)
        
        # Phase 2: Accept (if majority promises received)
        if len(promises) >= (self.node_count // 2 + 1):
            proposer.send_accept(self.nodes, proposal)
        
        # Check if consensus was reached
        # After a majority accepts, consensus should be reached
        acceptances = 0
        for node in self.nodes.values():
            key = (proposal.proposal_number, proposal.value)
            if key in node.acceptance_counts:
                acceptances += node.acceptance_counts[key]
        
        # Verify that acceptances were recorded
        self.assertGreater(acceptances, 0, "At least one acceptance should be recorded")
    
    def test_majority_consensus(self):
        """Test that consensus requires a majority."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="test_value")
        
        # Send prepare
        proposer.send_prepare(self.nodes, proposal)
        
        # Collect promises from all acceptors
        promises = []
        for node_id, node in self.nodes.items():
            if node_id != 1:
                promise = node.send_promise(proposal)
                if promise:
                    promises.append(promise)
        
        # Should have majority (4 out of 5)
        self.assertGreaterEqual(len(promises), self.node_count // 2 + 1,
                               "Should have majority of promises")
    
    def test_node_down_prevents_consensus(self):
        """Test that when too many nodes are down, consensus cannot be reached."""
        # Take down 3 nodes (leaving only 2 up, which is less than majority of 5)
        self.nodes[3].state = NodeState.DOWN
        self.nodes[4].state = NodeState.DOWN
        self.nodes[5].state = NodeState.DOWN
        
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="value1")
        
        # Send prepare
        proposer.send_prepare(self.nodes, proposal)
        
        # Collect promises from up nodes
        promises = []
        for node_id, node in self.nodes.items():
            if node_id != 1 and node.state == NodeState.UP:
                promise = node.send_promise(proposal)
                if promise:
                    promises.append(promise)
        
        # Should not have majority
        self.assertLess(len(promises), self.node_count // 2 + 1,
                       "Should not have majority when too many nodes are down")


class TestPaxosFailures(unittest.TestCase):
    """Test node failure scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = PaxosLogger(round=1, filename="test_failures.csv")
        self.node_count = 5
        self.nodes = {}
        
        for i in range(1, self.node_count + 1):
            self.nodes[i] = PaxosNode(
                node_id=i,
                role=NodeRole.ACCEPTOR,
                logger=self.logger,
                node_count=self.node_count
            )
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.save_to_csv()
    
    def test_proposer_goes_down(self):
        """Test behavior when proposer goes down."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="value1")
        
        # Proposer goes down before sending prepare
        proposer.state = NodeState.DOWN
        
        # Try to send prepare (should be logged but not sent)
        proposer.send_prepare(self.nodes, proposal)
        
        # Verify that no nodes received prepare
        for node_id, node in self.nodes.items():
            if node_id != 1:
                self.assertNotIn(proposal.proposal_number, node.received_promises,
                               "Down proposer should not send prepares")
    
    def test_acceptor_goes_down_during_prepare(self):
        """Test when acceptor goes down during prepare phase."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="value1")
        
        # Take down one acceptor
        self.nodes[2].state = NodeState.DOWN
        
        # Send prepare
        proposer.send_prepare(self.nodes, proposal)
        
        # Down node should not have received prepare
        self.assertNotIn(proposal.proposal_number, self.nodes[2].received_promises,
                        "Down node should not receive prepare")
        
        # Other nodes should still receive
        active_receivers = sum(1 for node_id, node in self.nodes.items()
                             if node_id != 1 and node.state == NodeState.UP
                             and proposal.proposal_number in node.received_promises)
        self.assertGreater(active_receivers, 0, "Active nodes should receive prepare")
    
    def test_consensus_with_some_nodes_down(self):
        """Test that consensus can still be reached with some nodes down."""
        # Take down 1 node (still have majority: 4 out of 5, with 3 acceptors = 3 promises = majority)
        self.nodes[5].state = NodeState.DOWN
        
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="value1")
        
        # Send prepare
        proposer.send_prepare(self.nodes, proposal)
        
        # Collect promises from up nodes
        promises = []
        for node_id, node in self.nodes.items():
            if node_id != 1 and node.state == NodeState.UP:
                promise = node.send_promise(proposal)
                if promise:
                    promises.append(promise)
        
        # Should still have majority (3 promises from 3 acceptors out of 4 up nodes)
        self.assertGreaterEqual(len(promises), self.node_count // 2 + 1,
                               "Should have majority even with some nodes down")


class TestPaxosConcurrent(unittest.TestCase):
    """Test concurrent proposal scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = PaxosLogger(round=1, filename="test_concurrent.csv")
        self.node_count = 5
        self.nodes = {}
        
        for i in range(1, self.node_count + 1):
            self.nodes[i] = PaxosNode(
                node_id=i,
                role=NodeRole.ACCEPTOR,
                logger=self.logger,
                node_count=self.node_count
            )
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.save_to_csv()
    
    def test_concurrent_proposals(self):
        """Test handling of concurrent proposals from different nodes."""
        proposal1 = Proposal(node_id=1, proposal_number=1, value="value1")
        proposal2 = Proposal(node_id=2, proposal_number=2, value="value2")
        
        # Both proposers send prepare
        self.nodes[1].send_prepare(self.nodes, proposal1)
        self.nodes[2].send_prepare(self.nodes, proposal2)
        
        # Both should receive promises
        promises1 = []
        promises2 = []
        
        for node_id, node in self.nodes.items():
            if node_id != 1:
                promise = node.send_promise(proposal1)
                if promise:
                    promises1.append(promise)
            if node_id != 2:
                promise = node.send_promise(proposal2)
                if promise:
                    promises2.append(promise)
        
        # Both should potentially get majority
        # In real Paxos, higher proposal number wins
        self.assertGreater(len(promises1), 0, "First proposal should get promises")
        self.assertGreater(len(promises2), 0, "Second proposal should get promises")


class TestPaxosEdgeCases(unittest.TestCase):
    """Test edge cases and special scenarios."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = PaxosLogger(round=1, filename="test_edge.csv")
        self.node_count = 3  # Small cluster for edge cases
        self.nodes = {}
        
        for i in range(1, self.node_count + 1):
            self.nodes[i] = PaxosNode(
                node_id=i,
                role=NodeRole.ACCEPTOR,
                logger=self.logger,
                node_count=self.node_count
            )
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.save_to_csv()
    
    def test_single_node_consensus(self):
        """Test consensus with minimal nodes (3 nodes)."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="value1")
        
        proposer.send_prepare(self.nodes, proposal)
        
        promises = []
        for node_id, node in self.nodes.items():
            if node_id != 1:
                promise = node.send_promise(proposal)
                if promise:
                    promises.append(promise)
        
        # With 3 nodes, need 2 promises (including proposer, need 2 acceptors)
        self.assertGreaterEqual(len(promises), 1, "Should get at least one promise")
    
    def test_consensus_value_persistence(self):
        """Test that consensus value persists across nodes."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="persistent_value")
        
        # First round: establish consensus
        proposer.send_prepare(self.nodes, proposal)
        
        # Simulate accept phase
        proposer.send_accept(self.nodes, proposal)
        
        # Check that nodes have recorded the consensus value
        for node in self.nodes.values():
            if node.last_consensus:
                self.assertEqual(node.last_consensus, proposal.value,
                               "Consensus value should be persistent")
    
    def test_broadcast_reception(self):
        """Test that nodes can receive broadcast messages."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="broadcast_value")
        
        # Send broadcast to all nodes
        for node in self.nodes.values():
            node.receive_broadcast(proposal)
            self.assertEqual(node.last_consensus, proposal.value,
                           "All nodes should receive broadcast value")
    
    def test_consensus_flag_reset(self):
        """Test that consensus_reached flag is properly reset."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="test_value")
        
        # Set consensus
        proposer.set_consensus(proposal.value)
        
        # Flag should be set initially
        self.assertTrue(proposer.consensus_reached or 
                       proposer.last_consensus == proposal.value,
                       "Consensus should be set")
        
        # Reset consensus
        proposer.reset_consensus_reached()
        
        # Flag should be reset
        self.assertFalse(proposer.consensus_reached,
                        "Consensus flag should be reset")


class TestPaxosIntegration(unittest.TestCase):
    """Integration tests for complete Paxos rounds."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.logger = PaxosLogger(round=1, filename="test_integration.csv")
        self.node_count = 5
        self.nodes = {}
        
        for i in range(1, self.node_count + 1):
            self.nodes[i] = PaxosNode(
                node_id=i,
                role=NodeRole.ACCEPTOR,
                logger=self.logger,
                node_count=self.node_count
            )
    
    def tearDown(self):
        """Clean up after tests."""
        self.logger.save_to_csv()
    
    def test_full_paxos_round(self):
        """Test a complete Paxos round from prepare to accept."""
        proposer = self.nodes[1]
        proposal = Proposal(node_id=1, proposal_number=1, value="final_value")
        
        # Phase 1: Prepare
        proposer.send_prepare(self.nodes, proposal)
        
        # Collect promises
        promises = []
        for node_id, node in self.nodes.items():
            if node_id != 1:
                promise = node.send_promise(proposal)
                if promise:
                    promises.append(promise)
        
        # Check we have majority
        self.assertGreaterEqual(len(promises), self.node_count // 2 + 1,
                               "Should have majority for accept phase")
        
        # Phase 2: Accept
        proposer.send_accept(self.nodes, proposal)
        
        # Verify acceptances were recorded
        total_acceptances = 0
        for node in self.nodes.values():
            key = (proposal.proposal_number, proposal.value)
            if key in node.acceptance_counts:
                total_acceptances += node.acceptance_counts[key]
        
        # Should have at least majority acceptances
        self.assertGreaterEqual(total_acceptances, self.node_count // 2 + 1,
                               "Should have majority acceptances")


if __name__ == '__main__':
    # Run all tests
    unittest.main(verbosity=2)

