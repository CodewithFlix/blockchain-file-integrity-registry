import solcx
from solcx import compile_standard

# Install Solidity compiler versi 0.8.20
solcx.install_solc("0.8.20")

# Load kontrak Solidity
with open("contracts/FileIntegrityRegistry.sol", "r") as f:
    source = f.read()

# Compile
compiled = compile_standard(
    {
        "language": "Solidity",
        "sources": {"FileIntegrityRegistry.sol": {"content": source}},
        "settings": {
            "outputSelection": {
                "*": {"*": ["abi", "evm.bytecode.object"]}
            }
        },
    },
    solc_version="0.8.20",
)

# Simpan output ke file build.json
import json
with open("build.json", "w") as f:
    json.dump(compiled, f, indent=2)

print("Compiled successfully. ABI & bytecode saved to build.json")
