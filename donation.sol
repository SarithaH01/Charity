// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Donations {
    
    
    struct Donation {
        
        
        string pk;
        string amount;
        string name;
        string accAddress;
       
    }

    Donation[] public DonationDetails; 
     
    function retrieve() public view returns (Donation[] memory){
        return DonationDetails; 
    }
    
    function addDonation(string memory _pk,string memory _amount,string memory _name,string memory _accAddress) public {
        DonationDetails.push(Donation(_pk,_amount,_name,_accAddress)); //append to  Contact[] array
        // nameToPhoneNumber[_name] = _phoneNumber; //use name to get phone number
    }
    
}



