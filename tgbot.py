from telegram.ext import CommandHandler, CallbackContext
from telegram import Update
from web3 import Web3
import time
from telegram.ext import Updater
from threading import Thread

from web3.exceptions import BlockNotFound

TOKEN = '6601151372:AAE_8SWbEx6F-0dnCX0NI1BzNzp_e_KYlDE'
# Infura URL
infura_url = "https://mainnet.infura.io/v3/e869620b99334119bba095c34ccb8558"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Uniswap V2 Factory contract address
UNISWAP_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
YOUR_CHAT_ID = "2075839860"
# Uniswap V2 Factory ABI
uniswap_factory_abi = [{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"token0","type":"address"},{"indexed":True,"internalType":"address","name":"token1","type":"address"},{"indexed":False,"internalType":"address","name":"pair","type":"address"},{"indexed":False,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":True,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]
MAX_RETRIES = 60
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


def start(update: Update, context: CallbackContext):
    update.message.reply_text('Bot started!')

def alert(update: Update, context: CallbackContext):
    update.message.reply_text('Alert received!')

updater = Updater(TOKEN)
dp = updater.dispatcher
dp.add_handler(CommandHandler('start', start))
dp.add_handler(CommandHandler('alert', alert))

# Start the Bot
updater.start_polling()

from web3 import Web3


def monitor_sniper_wallets(pair_address, block_number):
    # Get the timestamp of the block where liquidity was added
    timestamp_liquidity_added = w3.eth.get_block(block_number)['timestamp']
    end_time = timestamp_liquidity_added + 14 # 14 seconds window

    unique_wallets = set()
    current_block_number = block_number + 1

    while True:
        try:
            current_block = w3.eth.get_block(current_block_number)
            current_timestamp = current_block['timestamp']

            # Check if the time window has passed
            if current_timestamp > end_time:
                break

            # Retrieve the transactions that interact with the pair address
            transactions = w3.eth.filter({
                'fromBlock': current_block_number,
                'toBlock': current_block_number,
                'address': pair_address
            }).get_all_entries()

            for txn in transactions:
                # Retrieve the full transaction details
                transaction_details = w3.eth.get_transaction(txn['transactionHash'])
                unique_wallets.add(transaction_details['from'])

            current_block_number += 1
        except BlockNotFound:

            # Wait a moment if the block is not yet available
            time.sleep(1)

    bot_msg = f"The wallets that bought within 14 seconds after liquidity was added are: {', '.join(unique_wallets)}"
    print(bot_msg)
    updater.bot.send_message(chat_id=YOUR_CHAT_ID, text=bot_msg)



    
def handle_event(event):
    token0_address = event['args']['token0']
    token1_address = event['args']['token1']
    token0_contract = w3.eth.contract(address=token0_address, abi=ERC20_ABI)
    token1_contract = w3.eth.contract(address=token1_address, abi=ERC20_ABI)
    token0_name = token0_contract.functions.name().call()
    token1_name = token1_contract.functions.name().call()
    pair_address = event['args']['pair']
    pair_contract = w3.eth.contract(address=pair_address, abi=UNISWAP_PAIR_ABI)
    retries = 0
    while True:
        liquidity = pair_contract.functions.getReserves().call()
        if liquidity[0] > 0 and liquidity[1] > 0:
            bot_msg = f"New pair created with liquidity: {token0_name} ({token0_address}) and {token1_name} ({token1_address})"
            print(bot_msg)
            updater.bot.send_message(chat_id=YOUR_CHAT_ID, text=bot_msg)
            monitor_sniper_wallets(pair_address, event['blockNumber'])
            break
        time.sleep(1)
        retries += 1
        if retries >= MAX_RETRIES:
            print("Maximum retries reached, exiting loop.")
            break


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