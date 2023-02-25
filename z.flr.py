
from web3 import Web3
import os

try:
    my_address = os.environ.get('ADDRS')
except:
    pass

def flarebalance():
    address = Web3.toChecksumAddress(my_address)
    print(address)

    # Connect to the Flare network using Web3
    flare = Web3(Web3.HTTPProvider('https://rpc.flare.network'))

    # Connect to the Songbird network using Web3
    songbird = Web3(Web3.HTTPProvider('https://rpc.sgb.network'))


    # Get the balance of Flare and Songbird coins for the specified address
    flare_balance = flare.eth.getBalance(address)
    songbird_balance = songbird.eth.getBalance(address)

    # Convert the balance values to decimal units
    flare_balance = Web3.fromWei(flare_balance, 'ether')
    print(flare_balance)
    songbird_balance = Web3.fromWei(songbird_balance, 'ether')
    print(songbird_balance)


if __name__ == "__main__":
    flarebalance()
