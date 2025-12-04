from web3 import Web3
from pathlib import Path
import json
import hashlib
from datetime import datetime, timezone

# ---- Konfigurasi dasar ----

# RPC Ganache lokal (harus sama dengan waktu kamu menjalankan: npx ganache -p 8546)
RPC_URL = "http://127.0.0.1:8546"

# BASE_DIR = root project (folder blockchain-file-integrity)
BASE_DIR = Path(__file__).resolve().parent.parent

CONTRACT_INFO_PATH = BASE_DIR / "contract_info.json"

# ---- Setup Web3 & Contract ----

w3 = Web3(Web3.HTTPProvider(RPC_URL))

if not w3.is_connected():
    raise RuntimeError(
        f"Web3 cannot connect to {RPC_URL}. "
        f"Pastikan 'npx ganache -p 8546' sedang berjalan."
    )

if not CONTRACT_INFO_PATH.exists():
    raise FileNotFoundError(
        f"{CONTRACT_INFO_PATH} tidak ditemukan. "
        "Pastikan kamu sudah menjalankan deploy_contract.py dan file contract_info.json sudah dibuat."
    )

with CONTRACT_INFO_PATH.open() as f:
    info = json.load(f)

CONTRACT_ADDRESS = Web3.to_checksum_address(info["address"])
CONTRACT_ABI = info["abi"]

contract = w3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

# Pakai akun pertama Ganache
DEFAULT_ACCOUNT = w3.eth.accounts[0]


# ---- Fungsi utilitas ----

def hash_file_sha256(file_path: str) -> str:
    """
    Hitung SHA-256 dari file (hex string).
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")

    sha = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def register_file(file_path: str, metadata: str = "") -> dict:
    """
    Register file ke blockchain:
    - Hitung hash
    - Panggil kontrak registerFile(hash, metadata)
    """
    file_hash = hash_file_sha256(file_path)
    print(f"[+] File hash (SHA-256): {file_hash}")

    tx_hash = contract.functions.registerFile(file_hash, metadata).transact(
        {"from": DEFAULT_ACCOUNT}
    )
    receipt = w3.eth.wait_for_transaction_receipt(tx_hash)

    return {
        "file_path": str(file_path),
        "file_hash": file_hash,
        "tx_hash": tx_hash.hex(),
        "block_number": receipt.blockNumber,
    }


from datetime import datetime, timezone

def get_file_record(file_hash: str) -> dict | None:
    """
    Ambil record file dari blockchain berdasarkan hash SHA-256 (hex string).
    Mengembalikan:
      - dict berisi owner, stored_hash, timestamp, metadata, dll jika ada
      - None kalau hash belum pernah diregister di smart contract
    """
    try:
        # 1) Ubah hex string → bytes32 (wajib untuk parameter bytes32 di Solidity)
        file_hash_bytes = bytes.fromhex(file_hash)

        # 2) Panggil fungsi kontrak. Sesuaikan nama fungsi dengan ABI kamu.
        #    Di sini asumsi signature:
        #    function getFileRecord(bytes32 fileHash)
        #        public view returns (address owner, uint256 timestamp, bytes32 storedHash, string memory metadata);
        owner, timestamp, stored_hash_bytes, metadata = (
            contract.functions.getFileRecord(file_hash_bytes).call()
        )

    except Exception as e:
        print("Error calling getFileRecord:", e)
        return None

    # 3) Kalau owner = address(0), artinya tidak ada record untuk hash ini
    #    (default value mapping di Solidity)
    if isinstance(owner, str) and owner.lower() == "0x0000000000000000000000000000000000000000":
        return None

    # Kalau Web3 mengembalikan bytes32 → konversi jadi hex string
    if isinstance(stored_hash_bytes, (bytes, bytearray)):
        stored_hash = stored_hash_bytes.hex()
    else:
        # Kalau sudah string '0x...' / hex, pakai apa adanya
        stored_hash = stored_hash_bytes

    # 4) Konversi timestamp
    ts_iso = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()

    return {
        "owner": owner,
        "timestamp": timestamp,
        "timestamp_iso": ts_iso,
        "stored_hash": stored_hash,
        "metadata": metadata,
    }



def verify_file(file_path: str) -> dict:
    """
    Verifikasi integritas file:
    - Hitung hash file sekarang
    - Cek ke blockchain
    """
    file_hash = hash_file_sha256(file_path)
    record = get_file_record(file_hash)

    result = {
        "file_path": str(file_path),
        "file_hash": file_hash,
        "on_chain": record is not None,
        "match": False,
        "record": record,
    }

    if record is not None:
        result["match"] = record["stored_hash"].lower() == file_hash.lower()

    return result
