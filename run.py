import random
import time
import threading
import json
from web3 import Web3
from web3.middleware import geth_poa_middleware
from eth_account import Account
import sys

# Fungsi untuk membaca konfigurasi dari file JSON
def load_config(filename):
    with open(filename, 'r') as file:
        config = json.load(file)
    return config

# Load konfigurasi dari config.json
config = load_config('config.json')
taiko_url = config['taiko_url']

def process_message(wallet, num_txs, gwei_input, min_delay, max_delay):
    process_message_contract_address = '0x1670000000000000000000000000000000000001'
    
    def process_message_in_contract(account_address, private_key):
        try:
            w3 = Web3(Web3.HTTPProvider(taiko_url))
            w3.middleware_onion.inject(geth_poa_middleware, layer=0)
            if not w3.is_connected():
                print(f'[ERROR] Gagal terhubung ke jaringan Taiko untuk {account_address}')
                return
            
            nonce = w3.eth.get_transaction_count(account_address)
            function_signature = '0x2035065e'
            transaction = {
                'from': account_address,
                'to': process_message_contract_address,
                'nonce': nonce,
                'gas': 23000,
                'gasPrice': w3.to_wei(gwei_input, 'gwei'),
                'chainId': 167000,
                'value': w3.to_wei(0, 'ether'),
                'data': function_signature
            }
            signed_tx = w3.eth.account.sign_transaction(transaction, private_key=private_key)
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            w3.eth.wait_for_transaction_receipt(tx_hash)
            print(f'[SUCCESS] Transaksi berhasil dengan hash: {tx_hash.hex()}')
        except Exception as e:
            print(f'[ERROR] Gagal memproses pesan: {str(e)}')
    
    def wallet_process_message(account_address, private_key):
        for _ in range(num_txs):
            print("-" * 48)
            print("Mulai memproses pesan...")
            process_message_in_contract(account_address, private_key)
            print("-" * 48)
            sleep_time = random.randint(min_delay, max_delay)
            print(f"[INFO] Tunggu {sleep_time} detik sebelum interaksi berikutnya...")
            time.sleep(sleep_time)
    
    account_address, private_key = wallet
    thread = threading.Thread(target=wallet_process_message, args=(account_address, private_key))
    thread.start()
    thread.join()

print("-" * 60)
print("-                    Push Point Taiko                      -")
print("-" * 60)

# Simpan data yang diperlukan
wallet = ("wallet", "private key")
num_txs = 150  # Contoh jumlah transaksi per wallet
min_delay = 20  # Delay minimum dalam detik
max_delay = 60  # Delay maksimum dalam detik
gwei_input = 0.1  # Nilai gwei untuk transaksi

process_message(wallet, num_txs, gwei_input, min_delay, max_delay)
