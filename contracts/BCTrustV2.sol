pragma solidity ^0.8.13;


contract BCTrustV2 {

    // a mapping of address to groupID
	mapping (address => uint8) public membersGrpId;
	// a mapping of groupID to the address of the master node
	mapping (uint8 => address) public grpIdMasters  ; 
	// a mapping of nodeID to its address
	mapping (uint8 => address) public nodeIdMember ;
	// a mapping of nodeID to the new message of that node
	mapping (uint8 => string) public messages ;
	
	
    // check if both sender and receiver are not null and of the same group
	modifier ControlOf(uint8 senderID, uint8 receiverID) {
		address addrSender   = nodeIdMember[senderID] ;
		address addrReceiver = nodeIdMember[receiverID] ;

		require (addrSender != address(0));
		require (addrReceiver != address(0));
		require (membersGrpId[addrSender] == membersGrpId[addrReceiver]);
		
		// required for modifier
	    _ ;
	
	}

    // make sure only the sender can make changes to its own data
	modifier OnlyConcernedObject (uint8 nodeID) {
		require (nodeIdMember[nodeID] == msg.sender);
	    _ ;
	}


	function BCTrustV2_AddNode (uint8 _category, uint8 _grpId, uint8 _id, uint256 masterSignature) public
	{
	    // the sender must not be assigned to any groupID
		assert (membersGrpId[msg.sender] == 0);
		// the sender must not be assigned to any nodeID
		assert (nodeIdMember[_id] == address(0));
		
        // if the new node is a master
		if (_category == 0) {
			require (grpIdMasters[_grpId] == address(0));
			// assign the master node for the group _grpId
            grpIdMasters[_grpId] = msg.sender ;
		} else {
		    // the group must already exist
		    require (grpIdMasters[_grpId] != address(0));
		    // check message signature
			uint inputData = uint(keccak256(abi.encodePacked(_grpId, _id, msg.sender)));
			uint masterKey = uint(keccak256(abi.encodePacked(grpIdMasters[_grpId])));
			uint recomputedSignature = inputData ^ masterKey;
			assert (recomputedSignature == masterSignature);
		    // assert (BCTrustV2_Verify (inputData, bytes32(_r), bytes32(_s), grpIdMasters[_grpId]) == true);
		}
		
		// assign the nodeID to the node address
		nodeIdMember [_id] = msg.sender;
		// assign the groupID to the node address
		membersGrpId[msg.sender] = _grpId;
	}


    // check the message signature
	function BCTrustV2_Verify (bytes memory inputData, bytes32 _r, bytes32 _s, address masterAddr) internal pure returns (bool)
    {
        bytes32 hash = keccak256(inputData) ;
        uint8   v    = 27 ;
        
    	if ((ecrecover(hash, v, _r, _s) == masterAddr) || (ecrecover(hash, v + 1, _r, _s) == masterAddr)) 
        	return true ;
        else
            return false ;
	}

    // convert address to bytes
	function BCTrustV2_FromAddressToBytes(address a) internal pure returns (bytes memory b) {
    	assembly {
    		let m := mload(0x40)
    		mstore(add(m, 20), xor(0x140000000000000000000000000000000000000000, a))
    		mstore(0x40, add(m, 52))
    		b := m
     	}
    }
    
    
	function BCTrustV2_FromBytesToBytes32(bytes memory src) internal pure returns (bytes32 res) {
    	assembly {
        		res := mload(add(src, 32))
    	}
	}

	
	function BCTrustV2_Send (uint8 sender, uint8 receiver, string memory message) ControlOf(sender, receiver) public
	{
		messages[receiver] = message ;
    }	

  
	function BCTrustV2_ReadMSG (uint8 addr) OnlyConcernedObject(addr) public returns (string memory) 
	{
		return messages[addr] ;
	}
}