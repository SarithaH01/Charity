#to store all donation details

// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Donations {                                             #Defines a Solidity contract named Donations.
    
    
    struct Donation {                                            #Defines a structure named Donation
        
        
        string pk;
        string amount;
        string name;
        string accAddress;
       
    }

    Donation[] public DonationDetails;                           #Declares a public array named DonationDetails to store instances of the Donation structure.
     
    function retrieve() public view returns (Donation[] memory){              #Defines a function named retrieve that returns the entire array of donation records. The function is view, meaning it does not modify the contract's state.
        return DonationDetails; 
    }
    
    function addDonation(string memory _pk,string memory _amount,string memory _name,string memory _accAddress) public {                         #Defines a function named addDonation to add a new donation record to the DonationDetails array. The function appends a new Donation structure with these parameters to the array.
        DonationDetails.push(Donation(_pk,_amount,_name,_accAddress)); //append to  Contact[] array
        // nameToPhoneNumber[_name] = _phoneNumber; //use name to get phone number
    }
    
}



