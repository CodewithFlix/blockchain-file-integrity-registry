from web3 import Web3
from pathlib import Path
import json

# RPC Ganache lokal (PAKAI PORT 8546)
RPC_URL = "http://127.0.0.1:8546"

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise RuntimeError("Cannot connect to Ganache at http://127.0.0.1:8546. "
                       "Pastikan 'npx ganache -p 8546' sedang berjalan.")

BASE_DIR = Path(__file__).resolve().parent.parent
build_path = BASE_DIR / "build.json"

if not build_path.exists():
    raise FileNotFoundError(
        f"build.json not found at {build_path}. "
        "Jalankan dulu: python python_scripts/compile_contract.py"
    )

with build_path.open() as f:
    compiled = json.load(f)

contract_interface = compiled["contracts"]["FileIntegrityRegistry.sol"]["FileIntegrityRegistry"]
abi = contract_interface["abi"]
bytecode = contract_interface["evm"]["bytecode"]["object"]

account = w3.eth.accounts[0]
print(f"Using deployer account: {account}")

FileIntegrity = w3.eth.contract(abi=abi, bytecode=bytecode)

print("Deploying contract...")
tx_hash = FileIntegrity.constructor().transact({"from": account})
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

contract_address = tx_receipt.contractAddress
print(f"Contract deployed at: {contract_address}")

out_path = BASE_DIR / "contract_info.json"
with out_path.open("w") as f:
    json.dump(
        {
            "address": contract_address,
            "abi": abi
        },
        f,
        indent=2
    )

print(f"Contract info saved to: {out_path}")
