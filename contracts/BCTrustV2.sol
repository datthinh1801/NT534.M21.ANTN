pragma solidity ^0.8.13;

contract BCTrustV2 {
    // a mapping of address to groupID
    mapping(address => uint8) public membersGrpId;
    mapping(address => uint8) public membersId;
    // a mapping of groupID to the address of the master node
    mapping(uint8 => address) public grpIdMasters;
    // a mapping of nodeID to its address
    mapping(uint8 => address) public nodeIdMember;
    // a mapping of nodeID to the new message of that node
    mapping(uint8 => string) public messages;

    // check if both sender and receiver are not null and of the same group
    modifier ControlOf(uint8 senderID, uint8 receiverID) {
        address addrSender = nodeIdMember[senderID];
        address addrReceiver = nodeIdMember[receiverID];

        require(addrSender != address(0));
        require(addrReceiver != address(0));
        require(membersGrpId[addrSender] == membersGrpId[addrReceiver]);

        // required for modifier
        _;
    }

    // make sure only the sender can make changes to its own data
    modifier OnlyConcernedObject(uint8 nodeID) {
        require(nodeIdMember[nodeID] == msg.sender);
        _;
    }

    function BCTrustV2_AddNode(
        uint8 _category,
        uint8 _grpId,
        uint8 _id,
        uint256 _r,
        uint256 _s
    ) public {
        // the sender must not be assigned to any groupID
        assert(membersGrpId[msg.sender] == 0);
        // the sender must not be assigned to any nodeID
        assert(nodeIdMember[_id] == address(0));

        // if the new node is a master
        if (_category == 0) {
            require(grpIdMasters[_grpId] == address(0));
            // assign the master node for the group _grpId
            grpIdMasters[_grpId] = msg.sender;
        } else {
            // the group must already exist
            require(grpIdMasters[_grpId] != address(0));
            // check message signature
            bytes32 input_byte = keccak256(
                abi.encodePacked(_grpId, _id, msg.sender)
            );
            assert(
                (ecrecover(input_byte, 27, bytes32(_r), bytes32(_s)) ==
                    grpIdMasters[_grpId]) ||
                    (ecrecover(input_byte, 28, bytes32(_r), bytes32(_s)) ==
                        grpIdMasters[_grpId])
            );
        }

        // assign the nodeID to the node address
        nodeIdMember[_id] = msg.sender;
        // assign the groupID to the node address
        membersGrpId[msg.sender] = _grpId;
        membersId[msg.sender] = _id;
    }

    function BCTrustV2_Send(
        uint8 sender,
        uint8 receiver,
        string memory message
    ) public ControlOf(sender, receiver) OnlyConcernedObject(sender) {
        messages[receiver] = message;
    }

    function BCTrustV2_ClearMSG(uint8 _id) public OnlyConcernedObject(_id) {
        messages[_id] = "";
    }
}
