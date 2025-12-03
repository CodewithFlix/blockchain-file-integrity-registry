import argparse
from integrity_client import register_file, verify_file


def cmd_register(args):
    result = register_file(args.file, args.metadata or "")

    print("\n[REGISTER]")
    print(" File       :", result["file_path"])
    print(" Hash       :", result["file_hash"])
    print(" Tx hash    :", result["tx_hash"])
    print(" Block no   :", result["block_number"])


def cmd_verify(args):
    result = verify_file(args.file)

    print("\n[VERIFY]")
    print(" File       :", result["file_path"])
    print(" Hash       :", result["file_hash"])

    if not result["on_chain"]:
        print(" Status     : NOT REGISTERED on blockchain")
        return

    rec = result["record"]
    print(" Status     : REGISTERED")
    print(" Owner      :", rec["owner"])
    print(" Timestamp  :", rec["timestamp_iso"])
    print(" Metadata   :", rec["metadata"])
    print(" Match      :", "YES" if result["match"] else "NO (POSSIBLE TAMPER)")


def main():
    parser = argparse.ArgumentParser(
        description="Blockchain-based File Integrity Tool (Ganache + Solidity)"
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: register
    p_reg = subparsers.add_parser("register", help="Register file to blockchain")
    p_reg.add_argument("file", help="Path ke file")
    p_reg.add_argument(
        "-m",
        "--metadata",
        help="Deskripsi tambahan (opsional)",
    )
    p_reg.set_defaults(func=cmd_register)

    # Subcommand: verify
    p_ver = subparsers.add_parser(
        "verify",
        help="Verifikasi integritas file terhadap data di blockchain",
    )
    p_ver.add_argument("file", help="Path ke file")
    p_ver.set_defaults(func=cmd_verify)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
