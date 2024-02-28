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


accounts_list = [{"address":"0xA0CFA7cA389f0b6CfCAc8FDA6E99aa2E624Dd788","private_key":"0x0ed987e3c5075e209f949a0823329ba0951f6b99e46f7682e5a0c82f4f30de25"},{"address":"0xd9aE87042D59B742f44a48982cf2691Ff5A88918","private_key":"0xabfd7d84417ccdbc6665e859c6ec4e5451f5e54ffecf5d2a03184326a4d0bdf0"},{"address":"0xe6160e47bbe9FF8014C9a35607ddA403421F44cE","private_key":"0x9a7063fe793bd3c36afbe06f3344de2776b057ad1bf2828a69932085361f4c9b"}]

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
    address = "0x6F8aBFe472811A714f512af550d4c316781d1672"
    private_key = "0xe304b4545f051170df21ea50196c5e74ea8cb6457b80a8c1ff5b3775f8331a52" # leaving the private key like this is very insecure if you are working on real world project
    
    ContactList = w3.eth.contract(abi=abi, bytecode=bytecode)
    
    nonce = w3.eth.get_transaction_count(address)

    transaction = ContactList.constructor().build_transaction(
        {
            "chainId": chain_id,
            "gasPrice": w3.eth.gas_price,
            "from": address,
            "nonce": nonce,
        }
    )
    
    sign_transaction = w3.eth.account.sign_transaction(transaction, private_key=private_key)
    print("Deploying Contract!")
    
    transaction_hash = w3.eth.send_raw_transaction(sign_transaction.rawTransaction)
    
    print("Waiting for transaction to finish...")
    transaction_receipt = w3.eth.wait_for_transaction_receipt(transaction_hash)
    print(f"[+] Done! Contract deployed to {transaction_receipt.contractAddress}")
    block = Account.objects.create(username = request.POST.get('beneficiary'),transaction_address = str(transaction_receipt.contractAddress),event = event)
    eventHost = userProfile.objects.filter(user = event.user).first()
    contact_list = w3.eth.contract(address=transaction_receipt.contractAddress, abi=abi)
    store_contact = contact_list.functions.addAccount(
        str(event.pk),request.POST.get('accAddress'),request.POST.get('beneficiary'),str(eventHost.account_address)
    ).build_transaction({"chainId": chain_id, "from": address, "gasPrice": w3.eth.gas_price, "nonce": nonce + 1})

   
    sign_store_contact = w3.eth.account.sign_transaction(
        store_contact, private_key=private_key
    )
    # Send the transaction
    send_store_contact = w3.eth.send_raw_transaction(sign_store_contact.rawTransaction)
    transaction_receipt = w3.eth.wait_for_transaction_receipt(send_store_contact)
    
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


