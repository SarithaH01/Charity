// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Account {
    
    
    struct Acc {
        
        
        string pk;
        string accAddress;
        string name;
        
        string charityAddress;
    }

    Acc[] public DonationDetails; 
     
    function retrieve() public view returns (Acc[] memory){
        return DonationDetails; 
    }
    
    function addAccount(string memory _pk,string memory _accAddress,string memory _name,string memory _charityAddress) public {
        DonationDetails.push(Acc(_pk,_accAddress,_name,_charityAddress)); //append to  Contact[] array
        // nameToPhoneNumber[_name] = _phoneNumber; //use name to get phone number
    }
    
}



