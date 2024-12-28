import logging
import os.path
import time
import winsound

import base58
from solana.rpc.api import Client
from solana.rpc.commitment import Confirmed
from solana.rpc.types import TokenAccountOpts
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from solders.rpc.errors import InvalidParamsMessage
from solders.rpc.responses import GetTokenSupplyResp, GetAccountInfoResp, GetTokenAccountsByOwnerResp
from solders.transaction import Transaction
from spl.token.constants import TOKEN_PROGRAM_ID
from spl.token.instructions import get_associated_token_address, create_associated_token_account

import config

# Configure logging
LOG_FILE = "monitor_log.log"
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode='a'),  # Append logs to the file
        logging.StreamHandler()  # Display logs in the console
    ]
)

# Constants for the Solana network
NODE_URL = "https://api.mainnet-beta.solana.com"  # Use your preferred node provider
client = Client(NODE_URL, timeout=180)

# Your wallet details (Use environment variables or secure vaults in production)
PRIVATE_KEY = base58.b58decode(config.solana_wallet_private_key)  # Replace with actual private key
WALLET_KEYPAIR = Keypair.from_bytes(PRIVATE_KEY)
WALLET_PUBLIC_KEY = WALLET_KEYPAIR.pubkey()

# Function to monitor for new token mint events
def monitor_new_tokens():
    logging.info("Monitoring for new token mint events...")
    last_slot = client.get_slot().value
    while True:
        try:
            current_slot = client.get_slot().value

            if current_slot > last_slot:
                for slot in range(last_slot + 1, current_slot + 1):
                    block = client.get_block(slot, encoding="json", max_supported_transaction_version=0)
                    if block and block.value.transactions:
                        for tx in block.value.transactions:
                            for instruction in tx.transaction.message.instructions:
                                # Detect SPL token creation
                                program_idx = instruction.program_id_index
                                program_id = tx.transaction.message.account_keys[program_idx]
                                if program_id == TOKEN_PROGRAM_ID:
                                    logging.info(f"Potential new token detected in slot {slot}: "
                                                 f"recent block hash: {tx.transaction.message.recent_blockhash}")
                                    validate_token(tx)
                last_slot = current_slot

        except Exception as e:
            logging.error(f"Error while monitoring: {e}")
            time.sleep(1)

# Function to validate the token (basic checks)
def validate_token(transaction):
    try:
        # Extract the mint address from the instruction data
        for address in transaction.transaction.message.account_keys:
            # Fetch token supply and other metadata
            supply_data = client.get_token_supply(address)
            if isinstance(supply_data, InvalidParamsMessage):
                # Not a mint address
                time.sleep(1)
                continue
            if isinstance(supply_data, GetTokenSupplyResp):
                supply = int(supply_data.value.amount)
                # Perform validation checks (e.g., minimum supply threshold)
                if supply > 0:
                    logging.info(f"Mint address with supply found: {address}")
                    logging.info(f"Token supply: {supply}")

                    mint_account_info = client.get_account_info(address)
                    if isinstance(mint_account_info, GetAccountInfoResp):
                        data = mint_account_info.value.data
                        mint_authority = Pubkey(data[0:32])
                        freeze_authority = Pubkey(data[36:68]) if data[35] != 0 else None
                        logging.info(f"Mint Authority: {str(mint_authority)}")
                        logging.info(f"Freeze Authority: {str(freeze_authority)}")
                        if not mint_authority.is_on_curve():
                            logging.warning(f"Danger: Mint Authority {str(mint_authority)} is not on Solana curve")
                            continue
                        if mint_authority and freeze_authority:
                            logging.warning("Danger: Both authorities exist. Check if the mint authority has been relinquished.")
                            #continue
                        if mint_authority == freeze_authority:
                            logging.warning("Danger: Mint authority and freeze authority are the same.")
                            continue
                        token_accounts = client.get_token_accounts_by_owner(mint_authority,
                                                                            TokenAccountOpts(mint=address))
                        if not isinstance(token_accounts, GetTokenAccountsByOwnerResp):
                            logging.warning("Validation failed: Cannot retrieve token account owner.")
                            continue
                        if not token_accounts or len(token_accounts.value) == 0:
                            logging.warning(f"WARNING: No token accounts found for this mint")
                            continue

                        logging.info(f"Candidate found: {address}")
                        logging.info(f"Validation passed for token: {address}")
                        logging.info(f"Token supply: {str(supply)}")
                        logging.info(f"Associated token accounts found: {str(len(token_accounts.value))}")
                        logging.info(f"Associated token accounts: {str(token_accounts.value)}")

                else:
                    logging.warning(f"Token validation failed for address {str(address)}: Supply is zero")
                    continue
            else:
                logging.warning(f"Could not fetch token supply for: {str(address)}")
                continue

    except Exception as e:
        logging.error(f"Validation failed: {e}")
        time.sleep(1)

if __name__ == "__main__":
    monitor_new_tokens()
