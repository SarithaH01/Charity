// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Track {
    

    struct TrackAmount {
        
        
        string bname;
        string date;
        string account;
        string amount;
 
    }

   
    TrackAmount[] public TrackDetails;
     
   
    function getTrackingDetails() public view returns (TrackAmount[] memory){
        return TrackDetails; 
    }

    function addTrackRecord(string memory _bname ,string memory _date,string memory _account,string memory _amount) public {
        TrackDetails.push(TrackAmount(_bname, _date,_account,_amount)); //append to  Contact[] array
       
    }


    
}



