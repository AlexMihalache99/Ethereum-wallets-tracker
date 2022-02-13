from audioop import add
from requests import get
from matplotlib import pyplot as plt
from datetime import datetime

API_KEY = "M3RJ1Q46CDIMUD957PNDUIT1A4RPZTT9J4"
BASE_URL = "https://api.etherscan.io/api"
ETHER_VALUE = 10 ** 18
GWEI_VALUE = 10 ** 9

'''
Method to make all the urls needed
First 3 arguments are always present
Last argument includes all the extra arguments

return - newly created url
'''
def make_api_url(module, action, address, **kwargs):
	url = BASE_URL + f"?module={module}&action={action}&address={address}&apikey={API_KEY}"

	for key, value in kwargs.items():
		url += f"&{key}={value}"

	return url

'''
Method to return the balance of an account
address - the eth address that I am tracking
return - address balance
'''
def get_account_balance(address):
	balance_url = make_api_url("account", "balance", address, tag="latest")
	response = get(balance_url)
	data = response.json()

	value = int(data["result"]) / ETHER_VALUE
	return value

'''
Method to track all the transactions of an address
Plots the account balance of eth since it has been created
address - the eth address that I am tracking
return - plots the account history of transactions
'''
def get_transactions(address):
	transactions_url = make_api_url("account", "txlist", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
	response = get(transactions_url)
	data = response.json()["result"]

	internal_tx_url = make_api_url("account", "txlistinternal", address, startblock=0, endblock=99999999, page=1, offset=10000, sort="asc")
	response2 = get(internal_tx_url)
	data2 = response2.json()["result"]

	data.extend(data2)
	data.sort(key=lambda x: int(x['timeStamp']))

	current_balance = 0
	balances = []
	times = []
	
	for tx in data:
		to = tx["to"]
		from_addr = tx["from"]
		value = int(tx["value"]) / ETHER_VALUE

		if "gasPrice" in tx:
			gas = int(tx["gasUsed"]) * int(tx["gasPrice"]) / ETHER_VALUE
		else:
			gas = int(tx["gasUsed"]) / ETHER_VALUE

		time = datetime.fromtimestamp(int(tx['timeStamp']))
		money_in = to.lower() == address.lower()

		if money_in:
			current_balance += value
		else:
			current_balance -= value + gas

		balances.append(current_balance)
		times.append(time)

	plt.plot(times, balances)
	plt.show()

'''
Method to return the current ETH gas price
base - if the price is needed in hex then true
otherwise false
return - current gas price in hex or decimal
'''
def get_gasPrice(base):
    gasPrice = make_api_url("proxy", "eth_gasPrice", "")
    response = get(gasPrice)
    data = response.json()["result"]
    price = int(data, 16) / GWEI_VALUE;

    if base:
        return data

    return price

'''
Method to return the estimated gas needed for a transaction
address - the address that we want to send eth to
return - gas needed for a transaction
'''
def get_estimatedGas(address):
    estimatedGas = make_api_url("proxy", "eth_estimateGas", "", data = 0x4e71d92d, to = address, value = 0xff22, gasPrice = get_gasPrice(True), gas = 0x5f5e0ff)
    response = get(estimatedGas)
    data = response.json()["result"]
    gas = int(data, 16)

    return gas

"""
Method to return the current ETH price
return - eth price and the timestamp
"""
def get_ethPrice():
    ethPrice = make_api_url("stats", "ethprice", "")
    response = get(ethPrice)
    data = response.json()["result"]
    price = data["ethusd"]
    timestamp = data["ethusd_timestamp"]
    time = datetime.fromtimestamp(int(timestamp))

    return price, time

'''
Method to return the current eth supply
return - eth supply
'''
def get_ethSupply():
    ethSupply = make_api_url("stats", "ethsupply", "")
    response = get(ethSupply)
    data = response.json()["result"]
    supply = int(data) / ETHER_VALUE
    
    return supply

"""
Method to return the current amount of Ether in circulation, 
ETH2 Staking rewards and EIP1559 burnt fees statistics.
return eth supply, eth2 staking rewards and burnt fees statistics
"""
def get_ethSupply2():
    ethSupply2 = make_api_url("stats", "ethsupply2", "")
    response = get(ethSupply2)
    data = response.json()["result"]
    supply = int(data["EthSupply"]) / ETHER_VALUE
    staking = int(data["Eth2Staking"]) / ETHER_VALUE
    burntFees = int(data["BurntFees"]) / ETHER_VALUE

    return supply, staking, burntFees

'''
my OpenSea address - 0x6b2fe2fec120dcb329aba4a6974d20c19bd78746
'''

'''
whale adresses
0x73bceb1cd57c711feac4224d062b0f6ff338501e
0xEA674fdDe714fd979de3EdF0F56AA9716B898ec8
0x829BD824B016326A401d083B33D092293333A830
0x1aD91ee08f21bE3dE0BA2ba6918E714dA6B45836
0x4bC1e40a42af875d98c94280313132e35ffDb067
binance14 - 0x28C6c06298d514Db089934071355E5743bf21d60
gemini - 0xd24400ae8BfEBb18cA49Be86258a3C749cf46853
ftx exchange - 0xC098B2a3Aa256D2140208C3de6543aAEf5cd3A94
coinbase4 - 0x3cD751E6b0078Be393132286c442345e5DC49699
'''
address = "0x28C6c06298d514Db089934071355E5743bf21d60"
get_transactions(address)
print(f"Current gas price for ethereum: {get_gasPrice(False)} gwei")
print(f"Current estimated gas used for a transaction is: {get_estimatedGas(address)} units")
print(f"Current price of Ethereum at {get_ethPrice()[1]} is {get_ethPrice()[0]} USD")
print(f"Current ethereum supply is {get_ethSupply()} ETH")
print(f"Current ethereum staking rewards are {get_ethSupply2()[1]} ETH")
print(f"Current ethereum burnt fees are {get_ethSupply2()[2]} ETH")