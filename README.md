🔐 Blockchain File Integrity Registry
A simple blockchain tool to check whether a file has been modified.
Perfect for cybersecurity, digital forensics, and anti-tampering use cases.

📌 What This Project Does 
This project helps you prove whether a file has ever been changed.
When you “register” a file, the system stores its SHA-256 hash on a blockchain.
Later, when you “verify” the file, the system checks whether the hash still matches.
If the file changed → the hash will be different → the system warns you.
This is the same principle used in digital forensics, evidence protection, and secure auditing.

🚀 Why This Matters in Cybersecurity
Modern attacks often involve tampering with:
log files
configuration files
scripts
documents
forensic evidence
This tool solves that problem by using blockchain as an immutable ledger.
Once a file hash is stored, nobody (not even the owner) can modify or delete it.
This provides:
Tamper-proof evidence storage
Trusted timestamps for investigations
Integrity validation across systems or time
Chain-of-custody support for digital forensics

🧠 How It Works
You → Python CLI → Hash the file → Store hash on blockchain
                ↓
             Verify → Compare file hash vs blockchain record
Everything is powered by:
Solidity smart contract → stores file information
Ganache → local blockchain for testing
Web3.py + Python CLI → simple tools to register and verify files

✨ Features
Register any file (documents, PDFs, logs, configs, images, etc.)
Store SHA-256 hash on blockchain
Add metadata descriptions
Verify whether a file has been modified
Get timestamp + owner address from blockchain
Tamper detection for cybersecurity and forensic purposes
Easy Python CLI (no need for Hardhat, NodeJS, or MetaMask)

🧱 Project Architecture
+------------------+
|   User (CLI)     |
+------------------+
         |
         v
+---------------------------+
| Python Client (Web3.py)   |
| - Hash file               |
| - Register & verify       |
+---------------------------+
         |
         v
+---------------------------+
| Solidity Smart Contract   |
| FileIntegrityRegistry.sol |
+---------------------------+
         |
         v
+---------------------------+
|   Local Blockchain        |
|   (Ganache)               |
+---------------------------+

🛡 Threat Model (Cybersecurity Benefits)
1. File Tampering Detection
If someone modifies a registered file → verification shows MISMATCH.
2. Insider Threat Protection
Even admin/root cannot alter blockchain records.
3. Trusted Timestamps
Blockchain timestamps cannot be forged.
4. Forensic Chain-of-Custody
Each file record stores:
owner address
metadata
original hash
timestamp
5. No Central Point of Failure
Unlike a database that can be modified, blockchain ensures immutability.

🧰 Installation & Setup (Simple)

1️⃣ Install dependencies
pip install web3 py-solc-x eth-tester
python -m solcx.install 0.8.20

2️⃣ Start local blockchain (Ganache)
npx ganache -p 8546
Keep this terminal open.

3️⃣ Compile the smart contract
python python_scripts/compile_contract.py

4️⃣ Deploy the contract
python python_scripts/deploy_contract.py
This creates contract_info.json
→ containing the contract address + ABI needed by the client.

🖥 How to Use the CLI

✔ Register a file
python python_client/cli.py register sample.txt -m "Initial evidence"
Output example:
[REGISTER]
File: sample.txt
Hash: 92a438f7...
Status: Stored on blockchain

✔ Verify file integrity
python python_client/cli.py verify sample.txt
Possible results:
🔵 File is original:
Status: REGISTERED
Match: YES
🔴 File was modified:
Status: REGISTERED
Match: NO (POSSIBLE TAMPER)

📸 Suggested Screenshot Sections
(You can add these after running the tool)
/screenshots/ganache-start.png  
/screenshots/register-example.png  
/screenshots/verify-match.png  
/screenshots/verify-tamper.png  

🧭 Roadmap (Future Enhancements)
Web dashboard (Flask / Streamlit)
IPFS integration for full file storage
Multi-user signatures
Organization-level audit mode
Automatic alerts for file tampering

📄 License
This project is licensed under the MIT License.
See LICENSE for details.

👤 Author
Felix Halim
Cybersecurity & Blockchain Enthusiast
MBA in IT Management
GitHub: https://github.com/CodewithFlix
LinkedIn: https://www.linkedin.com/in/felix-halim-a7642918b/

⭐ If you found this project useful…
Please ⭐ the repository — it helps visibility and supports my learning journey 🙌