from telegram.ext import CommandHandler, CallbackContext
from telegram import Update
from web3 import Web3
import time
from telegram.ext import Updater
from threading import Thread
TOKEN = '6601151372:AAE_8SWbEx6F-0dnCX0NI1BzNzp_e_KYlDE'
# Infura URL
infura_url = "https://mainnet.infura.io/v3/e869620b99334119bba095c34ccb8558"
w3 = Web3(Web3.HTTPProvider(infura_url))

# Uniswap V2 Factory contract address
UNISWAP_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
YOUR_CHAT_ID = "2075839860"
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

def monitor_sniper_wallets(pair_address, block_number):
    time_window_blocks = 2
    unique_wallets = set()
    latest_block_number = w3.eth.block_number
    for current_block_number in range(block_number + 1, min(block_number + time_window_blocks + 1, latest_block_number + 1)):
        block = w3.eth.get_block(current_block_number, full_transactions=True)
        for txn in block['transactions']:
            if txn['to'] == pair_address:
                unique_wallets.add(txn['from'])
    bot_msg = f"The sniper wallet count is {len(unique_wallets)}"
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
    while True:
        liquidity = pair_contract.functions.getReserves().call()
        if liquidity[0] > 0 and liquidity[1] > 0:
            bot_msg = f"New pair created with liquidity: {token0_name} ({token0_address}) and {token1_name} ({token1_address})"
            print(bot_msg)
            updater.bot.send_message(chat_id=YOUR_CHAT_ID, text=bot_msg)
            monitor_sniper_wallets(pair_address, event['blockNumber'])
            break
        time.sleep(1)



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