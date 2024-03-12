from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db.models import Q
from django.contrib.auth.models import User
from .models import userProfile,Event,Donation,Account,Blog
from web3 import Web3

from django.core.files.storage import FileSystemStorage

ganache_url = "HTTP://127.0.0.1:7545"


accounts_list = [{"address":"0x9427D625b67E74F4Bd8DFB297507F49b7718777f","private_key":"9f8b43a8e16dca8f6ada734e6709e4613ee5ea8474ccd28621cd37daf2795b25"},{"address":"0x6fc6799BDF2cd05F97c3E25e2B5b14fD5C5A6691","private_key":"0153ba07a1fc8e859619ae09be74e585bc3b2f2951235d98ad9c92a5b21cf1e8"},{"address":"0x8E6C22e5a29FA4f3f5B5bC1f6C48b0bcF60d2E2a","private_key":"22da6c21ca966aa4294814d83f56da586f739c7a95b3d036c8a8c971d56da16f"}]

# print(accounts_list)

def homepage(request):
    
    if request.user.is_authenticated:
        profile = userProfile.objects.filter(user = request.user).first()

    else:
        profile = ''
    blog = Blog.objects.all()
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
    # donations = Donation.objects.filter(event = event)
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

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Donations"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Donations"]["metadata"])["output"]["abi"]


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
                print(test.functions.retrieve().call())

                result = test.functions.retrieve().call()
                print("result",result[0][1])
                
                sumAmt += int(result[0][1])
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
    return render(request,'donation.html',{"events":events_all,"profile":profile})


def createEvent(request):
    user = User.objects.filter(username = request.user.username).first()
    print(user)
    event = Event.objects.create(title = request.POST.get('title'),description = request.POST.get('description'),image = request.FILES['image'],phone = request.POST.get('phone'),address = request.POST.get('address'),user = user, goal = request.POST.get('goal'),hashtag = request.POST.get('hashtag'))
    
    with open("account.sol", "r") as file:
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
    with open("account_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Account"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Account"]["metadata"])["output"]["abi"]

    from web3 import Web3

    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337
    address = "0x800A3BF5d9C6e42fFe4A57c7968618DdE81fd7cA"
    private_key = "e0a9f2f78b2dca326b4116744b422d2ba1ba5c15392492c3c45a2e3fbe9021b0" # leaving the private key like this is very insecure if you are working on real world project
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
    block = Account.objects.create(username = request.POST.get('beneficiary'),transaction_address = str(transaction_receipt.contractAddress),event = event)
    eventHost = userProfile.objects.filter(user = event.user).first()
    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    store_contact = contact_list.functions.addAccount(
        str(event.pk),request.POST.get('accAddress'),request.POST.get('beneficiary'),str(eventHost.account_address)
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

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Donations"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Donations"]["metadata"])["output"]["abi"]


    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    for donation in donations:
        
        test = w3.eth.contract(address= donation.transaction_address, abi=abi)
        print(test.functions.retrieve().call())

        result = test.functions.retrieve().call()
        print("result",result[0][1])
        
        sumAmt += int(result[0][1])
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

from solcx import compile_standard, install_solc
install_solc('0.8.0')
import json

def donate(request):
    user = User.objects.filter(username = request.user.username).first()
    print(user)
    post = Event.objects.filter(pk = request.POST.get('pk')).first()
    acc = Account.objects.filter(event = post).first()
    print("acc ::::::::: ",acc)
    #for getting account address


    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    with open("account.sol", "r") as file:
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
    with open("account_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Account"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Account"]["metadata"])["output"]["abi"]

    test = w3.eth.contract(address=acc.transaction_address, abi=abi)
    print(test.functions.retrieve().call())

    result = test.functions.retrieve().call()
    print("result of account ::::::::::: ",result[0][0])

    profile = userProfile.objects.filter(user = user).first()
    to_user = User.objects.filter(username = request.POST.get('username')).first()
    to_user_profile = userProfile.objects.filter(user = post.user).first()

    account_1 = profile.account_address
    account_2 = to_user_profile.account_address

    private_key = profile.private_key

    nonce  = web3.eth.getTransactionCount(account_1)
    ethereum_amount = convert_to_ether(int(request.POST.get('amount')))
    print("Amount in Ethereum: ", ethereum_amount)

    tx = {
        'nonce':nonce,
        'to':account_2,
        'value':web3.toWei(ethereum_amount,'ether'),
        'gas':2000000, 
        'gasPrice':web3.toWei(50,'gwei')
    }


    print(web3.fromWei(web3.eth.get_balance(account_1),'ether'))

    signed_tx = web3.eth.account.signTransaction(tx,private_key)
    tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
    print("Transaction hash :::::::: ",tx_hash)

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

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Donations"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Donations"]["metadata"])["output"]["abi"]


    chain_id = 1337
    address = "0x800A3BF5d9C6e42fFe4A57c7968618DdE81fd7cA"
    private_key = "e0a9f2f78b2dca326b4116744b422d2ba1ba5c15392492c3c45a2e3fbe9021b0" # leaving the private key like this is very insecure if you are working on real world project
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
    
    user_donation = User.objects.filter(username = request.user.username).first()
    post = Event.objects.filter(pk = request.POST.get('pk')).first()
    eventHost = userProfile.objects.filter(user = post.user).first()
    block = Donation.objects.create(user= user,transaction_address = str(transaction_receipt.contractAddress),event = post)

    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    store_contact = contact_list.functions.addDonation(
        request.POST.get('pk'),request.POST.get('amount'),eventHost.user.username,eventHost.account_address
    ).buildTransaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})

    # Sign the transaction
    sign_store_contact = w3.eth.account.sign_transaction(
        store_contact, private_key=private_key
    )
    # Send the transaction
    send_store_contact = w3.eth.send_raw_transaction(sign_store_contact.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(send_store_contact)

    print(contact_list.functions.retrieve().call())
    return JsonResponse({"success":1})

def tracking(request,pk):
    event = Event.objects.filter(pk=pk).first()
    donations = Donation.objects.filter(event = event,user = request.user)

    #for account address ------------------>>>>>>>>>>>>

    account = Account.objects.filter(event = event).first()

    with open("account.sol", "r") as file:
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
    with open("account_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Account"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Account"]["metadata"])["output"]["abi"]

    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

    test = w3.eth.contract(address=account.transaction_address, abi=abi)
    print(test.functions.retrieve().call())

    result_address = test.functions.retrieve().call()
    print("result",result_address[0][3])

    #_____________________for donation ___________________________

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

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Donations"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Donations"]["metadata"])["output"]["abi"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    for donation in donations:
        
        test = w3.eth.contract(address= donation.transaction_address, abi=abi)
        print(test.functions.retrieve().call())

        result = test.functions.retrieve().call()
        print("result",result[0][1])
        
        amt = {'username':account.username,"amount":int(result[0][1]),"address":result_address[0][3],"date":donation.date}
        amounts.append(amt)

    
    return render(request,'tracking.html',{"amounts":amounts})


def blog(request):
    b = Blog.objects.all()
    blogs = []
    for blog in b:
        user = userProfile.objects.filter(user = blog.username).first()
        bl = {"username":blog.username.username,"image":blog.image.url, "date":blog.date,"desc":blog.description,"profile":user.image.url,"title":blog.title}
        blogs.append(bl)
    return render(request,'blog.html',{"blogs":blogs})



def charityDonation(request,pk):
    event = Event.objects.filter(pk=pk).first()
    donations = Donation.objects.filter(event = event)

    #for account address ------------------>>>>>>>>>>>>

    account = Account.objects.filter(event = event).first()

    with open("account.sol", "r") as file:
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
    with open("account_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Account"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Account"]["metadata"])["output"]["abi"]

    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))

    test = w3.eth.contract(address=account.transaction_address, abi=abi)
    print(test.functions.retrieve().call())

    result_address = test.functions.retrieve().call()
    print("result",result_address[0][1])

    #_____________________for donation ___________________________

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

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Donations"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Donations"]["metadata"])["output"]["abi"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    for donation in donations:
        
        test = w3.eth.contract(address= donation.transaction_address, abi=abi)
        print(test.functions.retrieve().call())

        result = test.functions.retrieve().call()
        print("result",result[0][1])
        pic = userProfile.objects.filter(user = donation.user).first()
        amt = {'username':donation.user.username,"amount":int(result[0][1]),"address":result_address[0][1],"date":donation.date,"pk":account.pk,"image":pic.image.url}
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

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Donations"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Donations"]["metadata"])["output"]["abi"]

    amounts = []
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    sumAmt = 0
    
        
    test = w3.eth.contract(address= address, abi=abi)
    result = test.functions.retrieve().call()

    return result


def sendDonation(request):
    with open("track.sol", "r") as file:
        contact_list_file = file.read()

    from solcx import compile_standard, install_solc
    install_solc('0.8.0')
    import json #to save the output in a JSON file

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
    with open("track_code.json", "w") as file:
        json.dump(compiled_sol, file)

    bytecode = compiled_sol["contracts"]["ContactList.sol"]["Track"]["evm"]["bytecode"]["object"]
    abi = json.loads(compiled_sol["contracts"]["ContactList.sol"]["Track"]["metadata"])["output"]["abi"]

    from web3 import Web3

    # For connecting to ganache
    w3 = Web3(Web3.HTTPProvider("HTTP://127.0.0.1:7545"))
    chain_id = 1337
    address = "0xCCa4ADE6A069A1229F06f36682bDfdB060DaE65F"
    private_key = "71335f2253f2f60d19830aa04be9f94fdc26b479b8513b50c43ef6297d549f06" # leaving the private key like this is very insecure if you are working on real world project
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
    donation = Donation.objects.filter(pk = request.POST.get('pk')).first()
    details = getDonationDetails(donation.transaction_address)
    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    store_contact = contact_list.functions.addTrackRecord(
        details[0][0],details[0][0],"_educationalInfo","_educationalInfo"
    ).buildTransaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})

    # Sign the transaction
    sign_store_contact = w3.eth.account.sign_transaction(
        store_contact, private_key=private_key
    )
    # Send the transaction
    send_store_contact = w3.eth.send_raw_transaction(sign_store_contact.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(send_store_contact)

    print(contact_list.functions.getTrackingDetails().call())

    # used to get data from blockchain
    test = w3.eth.contract(address="0x6AeD2CE87BAAcd4dDf179bFdC9aC079d3A1b347E", abi=abi)
    print(test.functions.getTrackingDetails().call())

    result = test.functions.getTrackingDetails().call()
    print("result",result[0])
    return JsonResponse({"result":1})