import csv
import logging
from dataclasses import dataclass
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger()

@dataclass
class PaxosLogEntry:
    round: int
    timestamp: datetime
    from_node_id: int
    from_node_role: str
    from_node_state: str
    to_node_id: int
    to_node_role: str
    to_node_state: str
    action: str
    action_value: str
    consensus_value: str
    consensus_reached: bool

class PaxosLogger:
    def __init__(self, round, filename="paxosresult.csv"):
        self._round = round
        self.filename = filename
        self.entries = []
    
    @property
    def round(self):
        return self._round

    @round.setter
    def round(self, value):
        if isinstance(value, int) and value >= 0:
            self._round = value
        else:
            raise ValueError("Consensus round must be non-negative number")

    def record_log(self, from_node_id, from_node_role, from_node_state, to_node_id, to_node_role, to_node_state, action, action_value, consensus_value, consensus_reached):
        entry = PaxosLogEntry(
            round=self.round,
            timestamp=datetime.now(),
            from_node_id=from_node_id,
            from_node_role=from_node_role,
            from_node_state=from_node_state,
            to_node_id=to_node_id,
            to_node_role=to_node_role,
            to_node_state=to_node_state,
            action=action,
            action_value=str(action_value),
            consensus_value=str(consensus_value),
            consensus_reached=consensus_reached
        )
        self.entries.append(entry)
        
    def save_to_csv(self):
        with open(self.filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(['Round', 'Timestamp', 'From Node ID', 'From Node Role', 'From Node State', 'To Node ID', 'To Node Role', 'To Node State', 'Action', 'Action Value', 'Consensus Value', 'Consensus Reached'])
            for entry in self.entries:
                writer.writerow([
                    entry.round,
                    entry.timestamp.strftime("%Y-%m-%d %H:%M:%S"),  # Ensuring timestamp is formatted properly
                    entry.from_node_id, entry.from_node_role, entry.from_node_state,
                    entry.to_node_id, entry.to_node_role, entry.to_node_state, entry.action, entry.action_value,
                    entry.consensus_value, entry.consensus_reached
                ])
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.save_to_csv()