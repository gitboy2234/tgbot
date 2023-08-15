
from web3 import Web3
import time

# Infura URL
infura_url = "https://mainnet.infura.io/v3/e869620b99334119bba095c34ccb8558"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Uniswap V2 Factory contract address
UNISWAP_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"

# Uniswap V2 Factory ABI
uniswap_factory_abi = [{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"token0","type":"address"},{"indexed":True,"internalType":"address","name":"token1","type":"address"},{"indexed":False,"internalType":"address","name":"pair","type":"address"},{"indexed":False,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":True,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]

UNISWAP_PAIR_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
    # Additional functions and data structures can be included here as needed
]


# ERC20 Token ABI
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    },
]


# Reference to the Uniswap factory contract
uniswap_factory_contract = w3.eth.contract(address=UNISWAP_FACTORY_ADDRESS, abi=uniswap_factory_abi)


from collections import defaultdict

def monitor_sniper_wallets(pair_address, block_number):
    # Define the time window (e.g., 1/2 block)
    time_window_blocks = 2 # Adjust as needed
    unique_wallets = set()

    # Get all the transactions from the time window
    latest_block_number = w3.eth.block_number
    for current_block_number in range(block_number + 1, min(block_number + time_window_blocks + 1, latest_block_number + 1)):

        block = w3.eth.get_block(current_block_number, full_transactions=True)
        for txn in block['transactions']:
            # Analyze the transaction, check if it's interacting with your token pair contract
            if txn['to'] == pair_address:
                unique_wallets.add(txn['from'])

    print("The sniper wallet count is", len(unique_wallets))

def handle_event(event):
    # Get event data
    token0_address = event['args']['token0']
    token1_address = event['args']['token1']
    
    # Interact with token contracts to get token details
    token0_contract = w3.eth.contract(address=token0_address, abi=ERC20_ABI)
    token1_contract = w3.eth.contract(address=token1_address, abi=ERC20_ABI)
    token0_name = token0_contract.functions.name().call()
    token1_name = token1_contract.functions.name().call()

    # Get the pair contract address from the event data
    pair_address = event['args']['pair']

    # Create a reference to the pair contract
    pair_contract = w3.eth.contract(address=pair_address, abi=UNISWAP_PAIR_ABI)

    # Wait for liquidity to be added
    while True:
        liquidity = pair_contract.functions.getReserves().call() # Adjust based on actual function
        
        if liquidity[0] > 0 and liquidity[1] > 0: # Assuming liquidity is a tuple with reserves for both tokens
            print(f"New pair created with liquidity: {token0_name} ({token0_address}) and {token1_name} ({token1_address})")
            # Monitor the sniper wallets in the defined time window
            monitor_sniper_wallets(pair_address, event['blockNumber'])
            break
        
        time.sleep(1) # Wait before checking again
def setup_filter():
    return uniswap_factory_contract.events.PairCreated.create_filter(fromBlock='latest')

pair_created_filter = setup_filter()

while True:
    try:
        events = pair_created_filter.get_new_entries()
        if events:
            for event in events:
                handle_event(event)
    except ValueError as e:
        if 'filter not found' in str(e):
            print("Filter not found; recreating...")
            pair_created_filter = setup_filter()
        else:
            raise

    time.sleep(1)