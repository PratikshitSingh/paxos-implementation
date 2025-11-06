from main import NodeState, NodeRole

class PaxosNode:
    def __init__(self, node_id, role, logger, node_count):
        self.node_id = node_id
        self.totalnodecount = node_count
        self.state = NodeState.UP
        self.role = NodeRole.ACCEPTOR
        self.last_consensus = None
        self.consensus_reached = False # Set when a new consensus is reached and immediately reset after that.
        self.received_promises = set()
        self.logger = logger # This should be instance of custom class PaxosLogger and not python in built logger.
        self.acceptance_counts = {} # Track acceptance counts for each proposal.

    def set_consensus(self, value):
        if self.last_consensus != value:
            self.last_consensus = value
            self.consensus_reached = True
            self.log_state_change()
            # Schedule the reset of the consensus reached flag
            self.reset_consensus_reached()
    
    def reset_consensus_reached(self):
        # Reset the flag in the next cycle or event
        self.consensus_reached = False
        self.log_state_change()
         
    def log_state_change(self):
        # Log the change of state
        self.logger.record_log(
            from_node_id=self.node_id,
            from_node_role=self.role.value,
            from_node_state=self.state.value,
            to_node_id=self.node_id,
            to_node_role=self.role.value,
            to_node_state=self.state.value,
            action="ConsensusStateUpdate",
            action_value=str(self.last_consensus),
            consensus_value=str(self.last_consensus),
            consensus_reached=self.consensus_reached
        )
           
    def send_prepare(self, nodes, proposal):
        if self.state == NodeState.UP:
            for node in nodes.values():
                if node.state == NodeState.UP:
                    node.receive_prepare(proposal)
                    self.logger.record_log(
                        from_node_id=self.node_id,
                        from_node_role=self.role.value,
                        from_node_state=self.state.value,
                        to_node_id=node.node_id,
                        to_node_role=node.role.value,
                        to_node_state=node.state.value,
                        action="PrepareSend",
                        action_value=str(proposal.proposal_number),
                        consensus_value=str(self.last_consensus) if self.last_consensus else "None",
                        consensus_reached=False
                    )
                else:
                    # Log that the message is not sent because the destination node is down
                    self.logger.record_log(
                        from_node_id=self.node_id,
                        from_node_role=self.role.value,
                        from_node_state=self.state.value,
                        to_node_id=node.node_id,
                        to_node_role=node.role.value,
                        to_node_state="DOWN",
                        action="PrepareNotSent",
                        action_value=str(proposal.proposal_number),
                        consensus_value=str(self.last_consensus) if self.last_consensus else "None",
                        consensus_reached=False
                    )
        else:
            # Log that no messages are sent because the source node is down
            self.logger.record_log(
                from_node_id=self.node_id,
                from_node_role=self.role.value,
                from_node_state="DOWN",
                to_node_id="N/A",
                to_node_role="N/A",
                to_node_state="N/A",
                action="PrepareNotSent",
                action_value="N/A",
                consensus_value="N/A",
                consensus_reached=False
            )
            print(f"Node {self.node_id} is DOWN. No prepare messages sent.")


    def receive_prepare(self, proposal):
        if self.state == NodeState.UP:
            # Log receiving a prepare request
            self.logger.record_log(
                from_node_id=proposal.node_id,
                from_node_role=self.role.value,  # Assuming you may not know the role here unless you maintain more state or look it up
                from_node_state=self.state.value,  # Same as role, adjust if you have access to this info
                to_node_id=self.node_id,
                to_node_role=self.role.value,  # Assuming roles are stored as enum and logging their string representation
                to_node_state=self.state.value,
                action="PrepareReceive",
                action_value="None",  # Adjust if there's specific value related to prepare you want to log
                consensus_value=str(self.last_consensus) if self.last_consensus else "None",
                consensus_reached=False
            )
            print(f"Node {self.node_id} received prepare from {proposal.node_id}")
            
            # Log decision to send a promise based on state
            if self.last_consensus is not None:
                self.send_promise(proposal)
                # Optionally log that we are sending a promise with an existing consensus value
                self.logger.record_log(
                    from_node_id=self.node_id,
                    from_node_role=self.role.value,
                    from_node_state=self.state.value,
                    to_node_id=proposal.node_id,
                    to_node_role=self.role.value,  # Adjust based on actual knowledge
                    to_node_state=self.state.value,
                    action="PromiseSend",
                    action_value="ExistingConsensus",  # Indicate this promise is based on existing consensus
                    consensus_value=str(self.last_consensus),
                    consensus_reached=False
                )
            else:
                self.send_promise(proposal)
                # Optionally log that we are sending a standard promise
                self.logger.record_log(
                    from_node_id=self.node_id,
                    from_node_role=self.role.value,
                    from_node_state=self.state.value,
                    to_node_id=proposal.node_id,
                    to_node_role='Unknown',
                    to_node_state='Unknown',
                    action="PromiseSend",
                    action_value="NewPromise",  # Indicate this is a new promise without existing consensus
                    consensus_value="None",
                    consensus_reached=False
                )

    def send_promise(self, proposal):
        if self.state == NodeState.UP:
            # Add the proposal number to the set of received promises
            self.received_promises.add(proposal.proposal_number)

            # Check if there was a consensus in the current or a previous round
            consensus_achieved = self.last_consensus is not None
            consensus_value = self.last_consensus if consensus_achieved else "None"

            # Log sending a promise
            self.logger.record_log(
                from_node_id=self.node_id,
                from_node_role=self.role.value,  # Assuming role is stored as an enum
                from_node_state=self.state.value,
                to_node_id=proposal.node_id,
                to_node_role='Unknown',  # This could be enhanced if you have a way to look up the role
                to_node_state='Unknown',  # This could also be enhanced if you have node state information available
                action="PromiseSend",
                action_value=str(proposal.proposal_number),
                consensus_value=str(consensus_value),
                consensus_reached=consensus_achieved
            )

            # Respond to the leader with the promise and the last known consensus if it exists
            # This could be sent back via a network message or other means depending on system architecture
            return {
                'proposal_number': proposal.proposal_number,
                'node_id': self.node_id,
                'last_consensus': consensus_value,
                'consensus_achieved': consensus_achieved
            }


    def receive_promise(self, proposal):
        # Track promises received
        self.received_promises.add(proposal.proposal_number)

        # Log the reception of a promise
        self.logger.record_log(
            from_node_id=proposal.node_id,
            from_node_role=self.role.value,  # Role might not be known; update if possible
            from_node_state=self.state.value,  # State might not be known; update if possible
            to_node_id=self.node_id,
            to_node_role=self.role.value,
            to_node_state=self.state.value,
            action="PromiseReceive",
            action_value=str(proposal.proposal_number),
            consensus_value=str(proposal.value if proposal.value else "None"),
            consensus_reached=False
        )
        print(f"Node {self.node_id} received promise from {proposal.node_id} with proposal number {proposal.proposal_number} and value {proposal.value if proposal.value else 'None'}")

        # Decide on the action based on promises received
        self.decide_on_promises_received(proposal)

    def decide_on_promises_received(self, proposal):
        # Placeholder for how to decide after receiving promises
        # This method should handle the aggregation and evaluation of received promises
        # Check if the majority of promises indicate a previous consensus
        majority_needed = self.totalnodecount // 2 + 1
        consensus_count = {}
        for received_proposal in self.received_promises:
            value = received_proposal
            if value not in consensus_count:
                consensus_count[value] = 0
            consensus_count[value] += 1
            if consensus_count[value] >= majority_needed:
                self.logger.record_log(
                    from_node_id=self.node_id,
                    from_node_role=self.role.value,
                    from_node_state=self.state.value,
                    to_node_id=self.node_id,
                    to_node_role=self.role.value,
                    to_node_state=self.state.value,
                    action="ConsensusAchieved",
                    action_value=str(value),
                    consensus_value=str(value),
                    consensus_reached=True
                )
                print(f"Consensus previously reached on value {value}, re-adopting this consensus.")
                # Optionally, re-broadcast this consensus or take further actions
                return
        print("No consensus reached previously, proceeding with current proposals.")




    def send_accept(self, nodes, proposal):
        if self.state == NodeState.UP:
            for node in nodes.values():
                if node.state == NodeState.UP:
                    # Log before sending accept to each node
                    self.logger.record_log(
                        from_node_id=self.node_id,
                        from_node_role=self.role.value,  # Assuming role is stored as an enum
                        from_node_state=self.state.value,
                        to_node_id=node.node_id,
                        to_node_role=node.role.value,  # Assuming you have access to node's role
                        to_node_state=node.state.value,
                        action="AcceptSend",
                        action_value=str(proposal.proposal_number),
                        consensus_value=str(proposal.value),
                        consensus_reached=False  # This might be updated only after all acceptances
                    )
                    node.receive_accept(proposal)




    def receive_accept(self, proposal):
        if self.state == NodeState.UP:
            key = (proposal.proposal_number, proposal.value)  # Key by both proposal number and value

            # Increment the acceptance count for the given proposal and value
            if key in self.acceptance_counts:
                self.acceptance_counts[key] += 1
            else:
                self.acceptance_counts[key] = 1

            # Determine majority
            majority = self.totalnodecount // 2 + 1  # Assuming 'nodes' is accessible and contains all node objects
            consensus_reached = self.acceptance_counts[key] >= majority

            # Log the reception of an accept message
            self.logger.record_log(
                from_node_id=proposal.node_id,
                from_node_role=self.role.value,  # Placeholder until role information is available or derived
                from_node_state=self.state.value,  # Placeholder until state information can be obtained
                to_node_id=self.node_id,
                to_node_role=self.role.value,
                to_node_state=self.state.value,
                action="AcceptReceive",
                action_value=str(proposal.value),
                consensus_value=str(proposal.value),
                consensus_reached=consensus_reached
            )
            print(f"Node {self.node_id} received accept from {proposal.node_id} with proposal {proposal.proposal_number} and value {proposal.value}, consensus reached: {consensus_reached}")

            # Update last consensus if majority is reached
            if consensus_reached:
                self.last_consensus = proposal.value
                self.reset_consensus_reached()  # Reset the consensus reached flag after updating



    def receive_broadcast(self, proposal):
        if self.state == NodeState.UP:
            # This is the point when we assume that consensus has been achieved.
            self.set_consensus(proposal.value)
            
            # Log the reception of a broadcast message
            self.logger.record_log(
                from_node_id=proposal.node_id,
                from_node_role=self.role.value,  # Role might not be known; adjust if more information is available
                from_node_state=self.state.value,  # State might not be known; adjust similarly
                to_node_id=self.node_id,
                to_node_role=self.role.value,
                to_node_state=self.state.value,
                action="BroadcastReceive",
                action_value=str(proposal.value),
                consensus_value=str(proposal.value),
                consensus_reached=True  # Assuming broadcast implies consensus reached
            )
            print(f"Node {self.node_id} received broadcast from {proposal.node_id} with proposal {proposal.proposal_number} and value {proposal.value}")
            self.last_consensus = proposal.value

    def go_down(self):
        pass