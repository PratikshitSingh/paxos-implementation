import csv
from enum import Enum
from dataclasses import dataclass
import logging
from datetime import datetime

# Enum to represent the possible states of a node within the Paxos consensus process.
class NodeState(Enum):
    UP = "Up"
    DOWN = "Down"
    BLOCKED = "Blocked"

# Enum to define the roles that nodes can assume in the Paxos algorithm (either Leader or Acceptor).
class NodeRole(Enum):
    LEADER = "Leader"
    ACCEPTOR = "Acceptor"

# Class to act as collection of all nodes in the ring.
class Nodes:
    def __init__(self, logger):
        self.nodes = {}
        self.logger = logger

    def add_node(self, node_id, number_of_nodes, role=NodeRole.ACCEPTOR):
        pass

# Dataclass to encapsulate the information for messages exchanged between nodes in the Paxos protocol.
@dataclass
class Message:
    sender_id: int
    receiver_id: int
    content: str

# Dataclass to represent a proposal made by a node in the Paxos consensus process, including its unique identifier and proposed value.
@dataclass
class Proposal:
    node_id: int
    proposal_number: int
    value: str  # Assuming proposals carry a value that's being agreed upon

# Abstract the consensus value in its own class
class ConsensusValue:
    def __init__(self, data) -> None:
        self.data = data
    
    def __str__(self) -> str:
        #return f"ConsensusValue({self.data})"
        return f"({self.data})"