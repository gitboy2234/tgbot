from telegram.ext import CommandHandler, CallbackContext
from telegram import Update
from web3 import Web3
import time
from telegram.ext import Updater
from threading import Thread
import requests
from web3.exceptions import BlockNotFound
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
TOKEN = '6601151372:AAE_8SWbEx6F-0dnCX0NI1BzNzp_e_KYlDE'
# Infura URL
infura_url = "https://autumn-lively-frog.discover.quiknode.pro/a42068299ea81533a410c5dc634efadfa8e8a442/"
w3 = Web3(Web3.HTTPProvider(infura_url))
ETHERSCAN_API_KEY = 'FUMHTQE96FPWIW79ZJFCIXFX5BPCGNQC7T'
# Uniswap V2 Factory contract address
UNISWAP_FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
YOUR_CHAT_ID = "2075839860"
# Uniswap V2 Factory ABI
uniswap_factory_abi = [{"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"token0","type":"address"},{"indexed":True,"internalType":"address","name":"token1","type":"address"},{"indexed":False,"internalType":"address","name":"pair","type":"address"},{"indexed":False,"internalType":"uint256","name":"","type":"uint256"}],"name":"PairCreated","type":"event"},{"constant":True,"inputs":[{"internalType":"uint256","name":"","type":"uint256"}],"name":"allPairs","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"allPairsLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"tokenA","type":"address"},{"internalType":"address","name":"tokenB","type":"address"}],"name":"createPair","outputs":[{"internalType":"address","name":"pair","type":"address"}],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":True,"inputs":[],"name":"feeTo","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[],"name":"feeToSetter","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":True,"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"address","name":"","type":"address"}],"name":"getPair","outputs":[{"internalType":"address","name":"","type":"address"}],"payable":False,"stateMutability":"view","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeTo","type":"address"}],"name":"setFeeTo","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"},{"constant":False,"inputs":[{"internalType":"address","name":"_feeToSetter","type":"address"}],"name":"setFeeToSetter","outputs":[],"payable":False,"stateMutability":"nonpayable","type":"function"}]
MAX_RETRIES = 10
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

UNICRYPT_LOCKER_ABI =  [{"inputs":[{"internalType":"contract IUniFactory","name":"_uniswapFactory","type":"address"}],"stateMutability":"nonpayable","type":"constructor"},{"anonymous":False,"inputs":[{"indexed":True,"internalType":"address","name":"previousOwner","type":"address"},{"indexed":True,"internalType":"address","name":"newOwner","type":"address"}],"name":"OwnershipTransferred","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"lpToken","type":"address"},{"indexed":False,"internalType":"address","name":"user","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"lockDate","type":"uint256"},{"indexed":False,"internalType":"uint256","name":"unlockDate","type":"uint256"}],"name":"onDeposit","type":"event"},{"anonymous":False,"inputs":[{"indexed":False,"internalType":"address","name":"lpToken","type":"address"},{"indexed":False,"internalType":"uint256","name":"amount","type":"uint256"}],"name":"onWithdraw","type":"event"},{"inputs":[],"name":"gFees","outputs":[{"internalType":"uint256","name":"ethFee","type":"uint256"},{"internalType":"contract IERCBurn","name":"secondaryFeeToken","type":"address"},{"internalType":"uint256","name":"secondaryTokenFee","type":"uint256"},{"internalType":"uint256","name":"secondaryTokenDiscount","type":"uint256"},{"internalType":"uint256","name":"liquidityFee","type":"uint256"},{"internalType":"uint256","name":"referralPercent","type":"uint256"},{"internalType":"contract IERCBurn","name":"referralToken","type":"address"},{"internalType":"uint256","name":"referralHold","type":"uint256"},{"internalType":"uint256","name":"referralDiscount","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getLockedTokenAtIndex","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getNumLockedTokens","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"}],"name":"getNumLocksForToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getUserLockForTokenAtIndex","outputs":[{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"uint256","name":"","type":"uint256"},{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getUserLockedTokenAtIndex","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"getUserNumLockedTokens","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"address","name":"_lpToken","type":"address"}],"name":"getUserNumLocksForToken","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"}],"name":"getUserWhitelistStatus","outputs":[{"internalType":"bool","name":"","type":"bool"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"uint256","name":"_index","type":"uint256"}],"name":"getWhitelistedUserAtIndex","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"getWhitelistedUsersLength","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"incrementLock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_amount","type":"uint256"},{"internalType":"uint256","name":"_unlock_date","type":"uint256"},{"internalType":"address payable","name":"_referral","type":"address"},{"internalType":"bool","name":"_fee_in_eth","type":"bool"},{"internalType":"address payable","name":"_withdrawer","type":"address"}],"name":"lockLPToken","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"migrate","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"owner","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_unlock_date","type":"uint256"}],"name":"relock","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"renounceOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address payable","name":"_devaddr","type":"address"}],"name":"setDev","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"uint256","name":"_referralPercent","type":"uint256"},{"internalType":"uint256","name":"_referralDiscount","type":"uint256"},{"internalType":"uint256","name":"_ethFee","type":"uint256"},{"internalType":"uint256","name":"_secondaryTokenFee","type":"uint256"},{"internalType":"uint256","name":"_secondaryTokenDiscount","type":"uint256"},{"internalType":"uint256","name":"_liquidityFee","type":"uint256"}],"name":"setFees","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IMigrator","name":"_migrator","type":"address"}],"name":"setMigrator","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"contract IERCBurn","name":"_referralToken","type":"address"},{"internalType":"uint256","name":"_hold","type":"uint256"}],"name":"setReferralTokenAndHold","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_secondaryFeeToken","type":"address"}],"name":"setSecondaryFeeToken","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"splitLock","outputs":[],"stateMutability":"payable","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"},{"internalType":"uint256","name":"","type":"uint256"}],"name":"tokenLocks","outputs":[{"internalType":"uint256","name":"lockDate","type":"uint256"},{"internalType":"uint256","name":"amount","type":"uint256"},{"internalType":"uint256","name":"initialAmount","type":"uint256"},{"internalType":"uint256","name":"unlockDate","type":"uint256"},{"internalType":"uint256","name":"lockID","type":"uint256"},{"internalType":"address","name":"owner","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"address payable","name":"_newOwner","type":"address"}],"name":"transferLockOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"newOwner","type":"address"}],"name":"transferOwnership","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"uniswapFactory","outputs":[{"internalType":"contract IUniFactory","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"_user","type":"address"},{"internalType":"bool","name":"_add","type":"bool"}],"name":"whitelistFeeAccount","outputs":[],"stateMutability":"nonpayable","type":"function"},{"inputs":[{"internalType":"address","name":"_lpToken","type":"address"},{"internalType":"uint256","name":"_index","type":"uint256"},{"internalType":"uint256","name":"_lockID","type":"uint256"},{"internalType":"uint256","name":"_amount","type":"uint256"}],"name":"withdraw","outputs":[],"stateMutability":"nonpayable","type":"function"}]

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
    {
    "constant": True,
    "inputs": [],
    "name": "totalSupply",
    "outputs": [{"name": "", "type": "uint256"}],
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

def get_eth_price_in_usd():
    url = "https://api.coingecko.com/api/v3/simple/price?ids=ethereum&vs_currencies=usd"
    response = requests.get(url)
    
    if response.status_code == 200:
        eth_price = response.json().get('ethereum', {}).get('usd')
        if eth_price:
            return float(eth_price)

    print("Failed to fetch Ethereum price.")
    return 0

def is_contract_verified(address):
    url = f"https://api.etherscan.io/api?module=contract&action=getsourcecode&address={address}&apikey={ETHERSCAN_API_KEY}"
    response = requests.get(url, verify=False)

    
    if response.status_code == 200:
        result = response.json()
        status = result.get('status')
        message = result.get('message')
        
        if status == '1' and message == 'OK':
            contract_code = result['result'][0]['SourceCode']
            if contract_code.strip():
                return True
            
    return False

def is_token_locked(unicrypt_locker_contract, token_address):
    try:
        num_locks = unicrypt_locker_contract.functions.getNumLocksForToken(token_address).call()
        return num_locks > 0
    except Exception as e:
        print(f"Error checking if token is locked: {e}")
        return False
UNICRYPT_LOCKER_ADDRESS = "0x04bDa42de3bc32Abb00df46004204424d4Cf8287"
def check_liquidity_locked(new_token_address):
    unicrypt_locker_contract = w3.eth.contract(address=UNICRYPT_LOCKER_ADDRESS, abi=UNICRYPT_LOCKER_ABI)
    if not is_token_locked(unicrypt_locker_contract, new_token_address):
        print(f"Token {new_token_address} is not locked on Unicrypt.")
        return (False, {})
    # Assuming the main Unicrypt locker's contract address
  
   

    # Get the number of locked tokens
    num_locked_tokens = unicrypt_locker_contract.functions.getNumLockedTokens().call()

    for index in range(num_locked_tokens):
        locked_token_address = unicrypt_locker_contract.functions.getLockedTokenAtIndex(index).call()
        if locked_token_address.lower() == token_address.lower():
            # You can further fetch more details about the lock here if needed
            # For the purpose of this example, I'm returning a simple message. You can replace it with actual data.
            return True, "Token is locked in Unicrypt."

    return False, None



def monitor_sniper_wallets(pair_address, block_number):
    # Get the timestamp of the block where liquidity was added
    timestamp_liquidity_added = w3.eth.get_block(block_number)['timestamp']
    start_time_05s = timestamp_liquidity_added + 0.5  # 0.5 second window start
    end_time_14s = timestamp_liquidity_added + 14     # 14 seconds window end

    unique_wallets = set()
    current_block_number = block_number + 1

    while True:
        try:
            current_block = w3.eth.get_block(current_block_number)
            current_timestamp = current_block['timestamp']

            # Check if the time window has passed
            if current_timestamp > end_time_14s:
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

                if current_timestamp >= start_time_05s:
                    unique_wallets.add(transaction_details['from'])

            current_block_number += 1
        except BlockNotFound:
            # Wait a moment if the block is not yet available
            time.sleep(1)

    bot_msg = f"The wallets that bought within 0.5 to 14 seconds after liquidity was added are: {', '.join(unique_wallets)}"
    print(bot_msg)
    updater.bot.send_message(chat_id=YOUR_CHAT_ID, text=bot_msg)



    
def handle_event(event):
    if 'args' in event and all(key in event['args'] for key in ['token0', 'token1', 'pair']):
        token0_address = event['args']['token0']
        token1_address = event['args']['token1']
        pair_address = event['args']['pair']
        WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
        
        if token1_address == WETH_ADDRESS:
            new_token_address = token0_address
        elif token0_address == WETH_ADDRESS:
            new_token_address = token1_address
        else:
            print("Neither of the tokens is WETH_ADDRESS. Skipping...")
            return
    else:
        print("Event does not have the expected format. Skipping...")
        return
    
    is_locked, locked_details = check_liquidity_locked(new_token_address)
    locked_status = "YES" if is_locked else "NO"
    
    new_token_contract = w3.eth.contract(address=new_token_address, abi=ERC20_ABI)
    new_token_name = new_token_contract.functions.name().call()
    new_token_symbol = new_token_contract.functions.symbol().call()
    creator_address = token1_address if token1_address != WETH_ADDRESS else token0_address 

    pair_contract = w3.eth.contract(address=pair_address, abi=UNISWAP_PAIR_ABI)
    reserves = pair_contract.functions.getReserves().call()
    
    if reserves[0] == 0 or reserves[1] == 0:
        print("One of the reserves is zero, cannot calculate price.")
        return

    decimals = 18
    price_in_eth = (reserves[0] / 10**decimals) / (reserves[1] / 10**decimals) if token0_address == WETH_ADDRESS else (reserves[1] / 10**decimals) / (reserves[0] / 10**decimals)
    total_supply = new_token_contract.functions.totalSupply().call() / 10**decimals
    market_cap_in_eth = total_supply * price_in_eth
    current_eth_price_in_usd = get_eth_price_in_usd()
    market_cap_in_usd = market_cap_in_eth * current_eth_price_in_usd
    is_verified = is_contract_verified(new_token_address)
    verified_status = "YES" if is_verified else "NO"

    retries = 0
    while True:
        liquidity = pair_contract.functions.getReserves().call()
        if liquidity[0] > 0 and liquidity[1] > 0:
            bot_msg = (
                f"<b>TOKEN NAME:</b> {new_token_name}\n"
                f"<b>CA:</b> <i>{new_token_address}</i>\n"
                f"<b>TOKEN SYMBOL:</b> ${new_token_symbol}\n"
                f"<b>Creator Address:</b> {creator_address}\n"
                f"<b>Market Cap:</b> ${market_cap_in_usd:,.2f}\n"
                f"<b>Verified Contract:</b> {verified_status}\n"
                f"<b>Liquidity Locked:</b> {locked_status} {locked_details if locked_details else ''}"
            )
            print(bot_msg)
            updater.bot.send_message(chat_id=YOUR_CHAT_ID, text=bot_msg, parse_mode='HTML')
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