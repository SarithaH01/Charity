from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import userProfile,Event,Donation,Account,Blog,Track,Product,Blood
from web3 import Web3

from django.core.files.storage import FileSystemStorage

ganache_url = "HTTP://127.0.0.1:7545"

from solcx import compile_standard, install_solc
install_solc('0.8.0')
import json

accounts_list = [{"address":"0x5Ce706b63fb84b93F076c9333d6BE73Ab39e20c8","private_key":"0xc9cfb7f337ea194a7dca7b4f02017d3b6af897b57fd1f45c598bd28acc1af584"},{"address":"0xC606BFEB496E26C3554Be0B92cFa66C29f6F7689","private_key":"0xb93d102fbce92d33f328f6afa6835277dfe7ab6c08c9905e9260ea70c8f4a3fc"},{"address":"0xf4C425a4592e88f9ABc2b780F1379dcd50188aBE","private_key":"0xbe323aeed2bb680e6c868bec281d9f2ffc217aabb5c54c5c5a3e880b784b5245"}]
accounts_list_charity = [{"address":"0xd64bbc438BdDE4F22e7415dF37f0dC7d5416916A","private_key":"0x04995ee2c5d31dfbaff48916ceb85f7155c0efa6718f77ae156171cc6b703a82"},{"address":"0x02152bce649784d67BDb3c1ec8C5fc2e8462142D","private_key":"0x4f4ee6669d8a6360f4519c8e81e9e383f85fd73dae083f9cf05219aa1314eb96"},{"address":"0x6d56e48386E1C035407E416292D9ae471B973f5B","private_key":"0xbbbd2b98c7b12ebc5fe6231901ab0cc034c0996d0453bd3951368bf40ad927ab"}]

with open("donation.sol", "r") as file:
    contact_list_file = file.read()

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)
# print(compiled_sol)
with open("donation_code.json", "w") as file:
    json.dump(compiled_sol, file)
address = "0x59512AC008Dfa083A21A2ebeeF5aadc41eD12fE7"
private_key = "0xff6ce83c23154d1fe3fe4a65202d284963a7937a120646c01f70a019b35bd77a"
# print(accounts_list)

def homepage(request):
    
    if request.user.is_authenticated:
        profile = userProfile.objects.filter(user = request.user).first()

    else:
        profile = ''
    blog = Blog.objects.all().order_by('-date')
    return render(request,'index.html',context = {'profile':profile,"blogs":blog[:2]})


message = 0
reg_error = 0

import random


def register(request):
    if request.method == 'POST':
        user = User.objects.create(username = request.POST.get('username'),email=request.POST.get('email'))
        user.set_password(request.POST.get('password'))
        user.save()

        file = request.FILES.get('file')
        fss = FileSystemStorage()
        filename = fss.save(file.name,file)
        url = fss.url(filename)
   
        user = User.objects.filter(username=request.POST.get('username')).first()
        
        profile = userProfile.objects.create(user=user)
        random_account = random.choice(accounts_list)
        print(random_account)
        profile.account_address = random_account['address']
        profile.private_key = random_account['private_key']
        profile.phone = request.POST.get('phone')
        profile.address = request.POST.get('address')
        profile.image = url
        profile.account_type = "Normal user"
        profile.save()


    return HttpResponseRedirect(reverse('homepage'))


def registercharity(request):
    if request.method == 'POST':
        user = User.objects.create(username = request.POST.get('username'),email=request.POST.get('email'))
        user.set_password(request.POST.get('password'))
        user.save()

        file = request.FILES.get('file')
        fss = FileSystemStorage()
        filename = fss.save(file.name,file)
        url = fss.url(filename)
   
        user = User.objects.filter(username=request.POST.get('username')).first()
        
        profile = userProfile.objects.create(user=user)
        random_account = random.choice(accounts_list_charity)
        print(random_account)
        profile.account_address = random_account['address']
        profile.private_key = random_account['private_key']
        profile.organization_name = request.POST.get('username')
        profile.organization_phone = request.POST.get('phone')
        profile.organization_address = request.POST.get('address')
        profile.image = url
        profile.account_type = "Organization account"
        profile.save()


    return HttpResponseRedirect(reverse('homepage'))


def checkLogin(request):
    
    username = request.POST.get('username')
    password = request.POST.get('password')

    user = authenticate(username = username,password = password)
    if user:
        print(username)
        return JsonResponse({"message":0})
            
    else:
        print("No user found")
        return JsonResponse({"message":1})

message = 0
reg_error = 0

def checkSignup(request):
    
    username = request.POST.get('username')
    password = request.POST.get('password')

    
    u = User.objects.filter(username = username).first()
    
    if u == None:
        message = 0
    else:
        message = 1
    
    return JsonResponse({"message":message})   

def user_login(request):
   
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(username = username,password = password)
        if user:

            if user.is_active:
                login(request, user)
                print("login success!!!")
                return HttpResponseRedirect(reverse('homepage'))
        else:
            
            print("No such user")


    return HttpResponseRedirect(reverse('homepage'))
    
@login_required
def user_logout(request):

    logout(request)


    return HttpResponseRedirect(reverse('homepage'))


def donations(request):
    events = Event.objects.filter(approved = True)
    
    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)
# print(compiled_sol)
    with open("donation_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    events_all =[]
    
    print("[+] Events : ",events)
    for event in events:
        # remaining =0
        sumAmt = 0
        donations = Donation.objects.filter(event = event)
        if donations:
            for donation in donations:
            
                test = w3.eth.contract(address= donation.transaction_address, abi=abi)
                print(test.functions.getDonationDetails().call())

                result = test.functions.getDonationDetails().call()
                print("result ===================",result)
                
                sumAmt += int(result[0][4])
                print("[+] Sum amount : ",sumAmt)
                toGo = event.goal - sumAmt
                if toGo <= 0:
                    remaining = 0
                else:
                    remaining = toGo
        else:
            remaining = event.goal - sumAmt
        
        eve = {'title':event.title,"description":event.description,"user":event.user,"date":event.date,'raised':sumAmt,"goal":event.goal,"pk":event.pk,"image":event.image,"toGo":remaining,"hashtag":event.hashtag}
        events_all.append(eve)
    profile = userProfile.objects.filter(user = request.user).first()

    # print(events_all)
    profile = userProfile.objects.filter(user = request.user).first()
    return render(request,'donation.html',{"events":events_all,"profile":profile})


def createEvent(request):
    user = User.objects.filter(username = request.user.username).first()
    print(user)
    
    event = Event.objects.create(title = request.POST.get('title'),description = request.POST.get('description'),image = request.FILES['image'],phone = request.POST.get('phone'),address = request.POST.get('address'),user = user, goal = request.POST.get('goal'),hashtag = request.POST.get('hashtag'))
    
    

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Event"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Event"]["metadata"])["output"]["abi"]

    from web3 import Web3

    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337
 # leaving the private key like this is very insecure if you are working on real world project
    # Create the contract in Python
    ContactList = w3.eth.contract(abi=abi, bytecode=bytecode)
    # Get the number of latest transaction
    nonce = w3.eth.getTransactionCount(address)

    transaction = ContactList.constructor().buildTransaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": address,
            "nonce": nonce,
        }
    )
    # Sign the transaction
    sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying Contract!")
    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    print("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"[+] Done! Contract deployed to {transaction_receipt.contractAddress}")
    block = Account.objects.create(username = request.POST.get('beneficiary'),transaction_address = str(transaction_receipt.contractAddress),event = event,charityName = request.user.username)
    eventHost = userProfile.objects.filter(user = event.user).first()
    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    
    import datetime
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y at %I:%M %p")

    print("Current date and time:", formatted_time)
    store_contact = contact_list.functions.addEventDetails(
        request.POST.get('beneficiary'),str(formatted_time),request.POST.get('accAddress'),request.POST.get('goal'),str(eventHost.account_address)
    ).buildTransaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})

    # Sign the transaction
    sign_store_contact = w3.eth.account.sign_transaction(
        store_contact, private_key=private_key
    )
    # Send the transaction
    send_store_contact = w3.eth.send_raw_transaction(sign_store_contact.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(send_store_contact)
    # test = w3.eth.contract(address= str(transaction_receipt.contractAddress), abi=abi)
    # print("[+] Details : ",test.functions.retrieve().call())
    return HttpResponseRedirect(reverse('homepage'))


def eventView(request,pk):
    event = Event.objects.filter(pk = pk).first()
    donations = Donation.objects.filter(event = event)
    donation = Donation.objects.filter(event = event).first()
    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)
# print(compiled_sol)
    with open("donation_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0

    for donation in donations:
        
        test = w3.eth.contract(address= donation.transaction_address, abi=abi)
        print(test.functions.getDonationDetails().call())

        result = test.functions.getDonationDetails().call()
        print("[+] Amount result : ",result[0][4])
        
        sumAmt += int(result[0][4])
    toGo = event.goal - sumAmt
    if toGo <= 0:
        remaining = 0
    else:
        remaining = toGo
    eve = {'title':event.title,"description":event.description,"user":event.user,"date":event.date,'raised':sumAmt,"goal":event.goal,"pk":event.pk,"image":event.image,"toGo":remaining,"hashtag":event.hashtag}

    if(request.user.username ==  event.user.username):
        selfPost = 1
    else:
        selfPost = 0
    return render(request,'eventView.html',{"event":eve,"donation":donation,"selfPost":selfPost})


#for donation
web3 = Web3(Web3.HTTPProvider(ganache_url))

import requests

def convert_to_ether(amount_in_rupees):
    
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=inr"
    response = requests.get(url)
    data = response.json()
    ethereum_inr_price = data["ethereum"]["inr"]
    ethereum_amount = amount_in_rupees / ethereum_inr_price
    return ethereum_amount

# amount_in_rupees = float(input("Enter amount in Rupees: "))
ethereum_amount = convert_to_ether(25000)
print("Amount in Ethereum: ", ethereum_amount)



def donate(request):
    user = User.objects.filter(username=request.user.username).first()
    post = Event.objects.filter(pk=request.POST.get('pk')).first()
    acc = Account.objects.filter(event=post).first()

    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Event"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Event"]["metadata"])["output"]["abi"]

    test = w3.eth.contract(address=acc.transaction_address, abi=abi)
    result = test.functions.getEventDetails().call()

    profile = userProfile.objects.filter(user=user).first()
    to_user = User.objects.filter(username=request.POST.get('username')).first()
    to_user_profile = userProfile.objects.filter(user=post.user).first()

    account_1 = profile.account_address
    account_2 = to_user_profile.account_address

    private_key = profile.private_key 

    nonce  = w3.eth.getTransactionCount(account_1)
    ethereum_amount = convert_to_ether(int(request.POST.get('amount')))

    tx = {
        'nonce': nonce,
        'to': result[0][4],
        'value': w3.toWei(ethereum_amount, 'ether'),
        'gas': 2000000, 
        'gasPrice': w3.toWei(50, 'gwei')
    }

    # Additional data to send
    additional_data = {
        "donor_username": request.user.username,
        "host_username": post.user.username,
        "formatted_time": formatted_time,
        "host_account_address": eventHost.account_address,
        "donation_amount": request.POST.get('amount')
    }

    # Convert additional data to bytes
    additional_data_bytes = json.dumps(additional_data).encode('utf-8')

    # Add data to transaction
    tx['data'] = additional_data_bytes

    # Sign and send transaction
    signed_tx = w3.eth.account.signTransaction(tx, private_key)
    tx_hash = w3.eth.sendRawTransaction(signed_tx.rawTransaction)

    # Obtain transaction receipt
    transaction_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y at %I:%M %p")

    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    store_contact = contact_list.functions.addDonationDetails().buildTransaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})

    # Sign the transaction
    sign_store_contact = w3.eth.account.sign_transaction(store_contact, private_key=private_key)

    # Send the transaction
    send_store_contact = w3.eth.send_raw_transaction(sign_store_contact.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(send_store_contact)

    print("[+] Donation details : ", contact_list.functions.getDonationDetails().call())
    
    # Create Donation object
    block = Donation.objects.create(user=user, transaction_address=str(transaction_receipt.contractAddress), event=post, to_user=result[0][0])

    return JsonResponse({"success": 1})

def tracking(request,pk):
    event = Event.objects.filter(pk=pk).first()
    donations = Donation.objects.filter(event = event,user = request.user)

    

    account = Account.objects.filter(event = event).first()

   

    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)
# print(compiled_sol)
    with open("donation_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0

    for donation in donations:
        
        amt_list = []
        
        abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]
        test = w3.eth.contract(address= donation.transaction_address, abi=abi)
        print(test.functions.getDonationDetails().call())

        result = test.functions.getDonationDetails().call()
        print("result [+]",result)
        tracking = Track.objects.filter(donation = donation).first()
        
        bytecode = compiled_sol["contracts"]["ContactList.sol"]["DonationTracking"]["evm"]["bytecode"]["object"]
        abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["DonationTracking"]["metadata"])["output"]["abi"]
        try:
            test = w3.eth.contract(address= tracking.transaction_address, abi=abi)
            print("[+][+][+][+]",test.functions.getTrackingDetails().call())
            userpro = userProfile.objects.filter(user = event.user).first()
            result1 = test.functions.getTrackingDetails().call()
        
            donation_1 = {'from_user':result[0][0],"to_user":result[0][1],"amount":int(result[0][4]),"address":result[0][3],"date":donation.date,"image":userpro.image.url}
            donation_2 = {'from_user':result1[0][1],"to_user":result1[0][0],"address":result1[0][4],"date":result1[0][3],"amount":result[0][4]}
            amt_list.append(donation_1)
            amt_list.append(donation_2)
            amounts.append(amt_list)
        except:
            userpro = userProfile.objects.filter(user = event.user).first()
            donation_1 = {'from_user':result[0][0],"to_user":result[0][1],"amount":int(result[0][4]),"address":result[0][3],"date":donation.date,"image":userpro.image.url}
            # donation_2 = {'from_user':result1[0][1],"to_user":result1[0][0],"address":result1[0][4],"date":result1[0][3],"amount":result[0][4]}
            amt_list.append(donation_1)
            
            amounts.append(amt_list)

    print(amounts)
    
    return render(request,'tracking.html',{"amounts":amounts})


def blog(request):
    b = Blog.objects.all().order_by('-date')
    profile = userProfile.objects.filter(user = request.user).first()
    blogs = []
    for blog in b:
        user = userProfile.objects.filter(user = blog.username).first()
        bl = {"username":blog.username.username,"image":blog.image.url, "date":blog.date,"desc":blog.description,"profile":user.image.url,"title":blog.title}
        blogs.append(bl)
    return render(request,'blog.html',{"blogs":blogs,"profile":profile})



def charityDonation(request,pk):
    event = Event.objects.filter(pk=pk).first()
    donations = Donation.objects.filter(event = event)

    account = Account.objects.filter(event = event).first()

    

    bytecode1 = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi1 = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    for donation in donations:
        
        test = w3.eth.contract(address= donation.transaction_address, abi=abi1)
        print(test.functions.getDonationDetails().call())

        result = test.functions.getDonationDetails().call()
        print("result",result[0][1])
        pic = userProfile.objects.filter(user = donation.user).first()
        amt = {'username':donation.user.username,"amount":int(result[0][4]),"address":result[0][1],"date":donation.date,"pk":donation.pk,"image":pic.image.url,"eventPk":event.pk,"sent":donation.sent}
        amounts.append(amt)
    print("[+] Amounts : ",amounts)
    return render(request,'charity.html',{"amounts":amounts})


def getDonationDetails(address):
    with open("donation.sol", "r") as file:
            contact_list_file = file.read()

    compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"ContactList.sol": {"content": contact_list_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.bytecode.sourceMap"] # output needed to interact with and deploy contract 
                }
            }
        },
    },
    solc_version="0.8.0",
)
# print(compiled_sol)
    with open("donation_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    
        
    test = w3.eth.contract(address= address, abi=abi)
    result = test.functions.getDonationDetails().call()

    return result


def sendDonation(request):
    

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["DonationTracking"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["DonationTracking"]["metadata"])["output"]["abi"]

    from web3 import Web3


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337

    ContactList = w3.eth.contract(abi=abi, bytecode=bytecode)
    address = "0x59512AC008Dfa083A21A2ebeeF5aadc41eD12fE7"
    private_key = "0xff6ce83c23154d1fe3fe4a65202d284963a7937a120646c01f70a019b35bd77a"
    nonce = w3.eth.getTransactionCount(address)

    transaction = ContactList.constructor().buildTransaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": address,
            "nonce": nonce,
        }
    )
    # Sign the transaction
    sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying Contract!")
    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    print("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")
    donation = Donation.objects.filter(pk = request.POST.get('pk')).first()
    
    bytecode1 = compiled_sol["contracts"]["ContactList.sol"]["Event"]["evm"]["bytecode"]["object"]
    abi1 = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Event"]["metadata"])["output"]["abi"]
    
    event = Event.objects.filter(pk = request.POST.get("event-pk")).first()
    acc = Account.objects.filter(event = event).first()

    test1 = w3.eth.contract(address=acc.transaction_address, abi=abi1)
    print(test1.functions.getEventDetails().call())

    result2 = test1.functions.getEventDetails().call()

    print("[+] PK : ",donation)
    details = getDonationDetails(donation.transaction_address)
    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    track = Track.objects.create(from_user = request.user.username,to_user = details[0][1],transaction_address = str(transaction_receipt.contractAddress),donation = donation)
    import datetime
    current_time = datetime.datetime.now()
    formatted_time = current_time.strftime("%d/%m/%Y at %I:%M %p")

    store_contact = contact_list.functions.addTrackingDetails(
        donation.to_user,request.user.username,details[0][1],str(formatted_time),result2[0][2]
    ).buildTransaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})

    donation.sent = True 
    donation.save()
    # Sign the transaction
    sign_store_contact = w3.eth.account.sign_transaction(
        store_contact, private_key=private_key
    )
    # Send the transaction
    send_store_contact = w3.eth.send_raw_transaction(sign_store_contact.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(send_store_contact)

    print(contact_list.functions.getTrackingDetails().call())

   #--------------For donating amount -----------------------


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Event"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Event"]["metadata"])["output"]["abi"]
    
    event = Event.objects.filter(pk = request.POST.get("event-pk")).first()
    acc = Account.objects.filter(event = event).first()

    test = w3.eth.contract(address=acc.transaction_address, abi=abi)
    print(test.functions.getEventDetails().call())

    result = test.functions.getEventDetails().call()
    print("result of account ::::::::::: ",result[0][4])
    user = User.objects.filter(username = request.user.username).first()
    profile = userProfile.objects.filter(user = user).first()
    

    account_1 = profile.account_address
   

    private_key = profile.private_key #private key srored in user profile

    nonce  = web3.eth.getTransactionCount(account_1)
    ethereum_amount = convert_to_ether(int(request.POST.get('amount')))
    print("Amount in Ethereum: ", ethereum_amount)

    tx = {
        'nonce':nonce,
        'to':result[0][2],
        'value':web3.toWei(ethereum_amount,'ether'),
        'gas':2000000, 
        'gasPrice':web3.toWei(50,'gwei')
    }


    print(web3.fromWei(web3.eth.get_balance(account_1),'ether'))

    signed_tx = web3.eth.account.signTransaction(tx,private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print("Transaction hash :::::::: ",tx_hash)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["EventDonation"]["metadata"])["output"]["abi"]


    chain_id = 1337
    address = "0x59512AC008Dfa083A21A2ebeeF5aadc41eD12fE7"
    private_key = "0xff6ce83c23154d1fe3fe4a65202d284963a7937a120646c01f70a019b35bd77a" # leaving the private key like this is very insecure if you are working on real world project
    # Create the contract in Python
    ContactList = w3.eth.contract(abi=abi, bytecode=bytecode)
    # Get the number of latest transaction
    nonce = w3.eth.getTransactionCount(address)

    transaction = ContactList.constructor().buildTransaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": address,
            "nonce": nonce,
        }
    )
    # Sign the transaction
    sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying Contract!")
    # Send the transaction
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    # Wait for the transaction to be mined, and get the transaction receipt
    print("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"Done! Contract deployed to {transaction_receipt.contractAddress}")


    return JsonResponse({"result":1})

def createBlog(request):

    blog = Blog.objects.create(title = request.POST.get('title'),description = request.POST.get('desc'),username = request.user,category = request.POST.get('category'),image = request.FILES['image'])

    return HttpResponseRedirect(reverse('blog'))


def shop(request):
    b = Product.objects.all().order_by('-date')
    profile = userProfile.objects.filter(user = request.user).first()
    products = []
    for product in b:
        user = userProfile.objects.filter(user = product.user).first()
        bl = {"username":product.user.username,"image":product.image.url, "date":product.date,"desc":product.description,"profile":user.image.url,"name":product.name,"price":product.price,"category":product.category,"added":product.added_by_organization}
        products.append(bl)
    return render(request,'shop.html',{"products":products,"profile":profile})

def addProduct(request):
    title = request.POST.get("title")
    desc = request.POST.get("desc")
    category = request.POST.get("category")
    
    profile = userProfile.objects.filter(user = request.user).first()
    
    if not profile.is_an_organization:
        product = Product.objects.create(name=title, description=desc, category=category, price=10,image = request.FILES['image'],user = request.user,address = request.POST.get('address'))
    else:
        product = Product.objects.create(name=title, description=desc, category=category, price=request.POST.get("price"),image = request.FILES['image'],user = request.user,address = "",added_by_organization = True)

    
    return HttpResponseRedirect(reverse('shop'))

def blood(request):
    b = Blood.objects.all().order_by('-date')
    profile = userProfile.objects.filter(user = request.user).first()
    products = []
    for blood in b:
        user = userProfile.objects.filter(user = blood.user).first()
        bl = {"username":blood.user.username, "date":blood.date,"profile":user.image.url,"firstname":blood.firstname,"lastname":blood.lasname,"type":blood.type,"address":blood.address,"pk":blood.pk}
        products.append(bl)
    bl = Blood.objects.filter(user = request.user).first()
    return render(request,'blood.html',{"bloods":products,"profile":profile,"blood":bl})

def addBlood(request):
    firstname = request.POST.get("first")
    lastname = request.POST.get("last")
    type = request.POST.get("type")
    
    blood = Blood.objects.create(firstname=firstname, lasname=lastname, type=type, user = request.user,age = request.POST.get('age'),gender = request.POST.get('gender'),address = request.POST.get('address'))
    
    return HttpResponseRedirect(reverse('blood'))

def bloodView(request,pk):
    b = Blood.objects.all().order_by('-date')
    profile = userProfile.objects.filter(user = request.user).first()
    products = []
    for blood in b:
        user = userProfile.objects.filter(user = blood.user).first()
        bl = {"username":blood.user.username, "date":blood.date,"profile":user.image.url,"firstname":blood.firstname,"lastname":blood.lasname,"type":blood.type,"address":blood.address,"pk":blood.pk}
        products.append(bl)
    bloodView1 =Blood.objects.filter(pk = pk).first()
    return render(request,'bloodView.html',{"bloods":products,"profile":profile,"blood":bloodView1})