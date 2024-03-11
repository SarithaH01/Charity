#to store all event details

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;                         #specifies the version of the Solidity compiler

contract Account {                              #definition of the Solidity contract named Account
    
    
    struct Acc {                                #defines a new structure named Acc. Structures in Solidity are used to define custom data types.
         
        
        string pk;
        string accAddress;
        string name;
        
        string charityAddress;
    }

    Acc[] public DonationDetails;               #declares a public array named DonationDetails of type Acc[]
     
    function retrieve() public view returns (Acc[] memory){                   #view keyword indicates that this function does not modify the contract's state.
        return DonationDetails; 
    }
    
    function addAccount(string memory _pk,string memory _accAddress,string memory _name,string memory _charityAddress) public {
        DonationDetails.push(Acc(_pk,_accAddress,_name,_charityAddress)); //append to  Contact[] array           #adds a new Acc structure to the DonationDetails array. It creates a new instance of the Acc structure with the provided parameters and appends it to the array.
        // nameToPhoneNumber[_name] = _phoneNumber; //use name to get phone number
    }
    
}



