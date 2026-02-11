import argparse
import sys
import textwrap

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def aes_encrypt(key, plaintext_path, ciphertext_path="Cipher.txt"):
    """Encrypt a file using AES-CBC with PKCS7 padding."""
    if not isinstance(key, bytes):
        key = key.encode()

    if len(key) != 16:
        print("Error: Key must be exactly 16 bytes.", file=sys.stderr)
        return False

    try:
        with open(plaintext_path, "rb") as f:
            plaintext = f.read()
    except FileNotFoundError:
        print(f"Error: Plaintext file '{plaintext_path}' not found.", file=sys.stderr)
        return False

    cipher = AES.new(key, AES.MODE_CBC)
    ciphertext = cipher.encrypt(pad(plaintext, AES.block_size))

    with open(ciphertext_path, "wb") as f:
        f.write(cipher.iv)
        f.write(ciphertext)

    print(f"Encrypted '{plaintext_path}' -> '{ciphertext_path}'")
    return True


def aes_decrypt(key, ciphertext_path, plaintext_path="Plain.txt"):
    """Decrypt a file using AES-CBC with PKCS7 padding."""
    if not isinstance(key, bytes):
        key = key.encode()

    if len(key) != 16:
        print("Error: Key must be exactly 16 bytes.", file=sys.stderr)
        return False

    try:
        with open(ciphertext_path, "rb") as f:
            iv = f.read(16)
            ciphertext = f.read()
    except FileNotFoundError:
        print(f"Error: Ciphertext file '{ciphertext_path}' not found.", file=sys.stderr)
        return False

    try:
        cipher = AES.new(key, AES.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)
    except (ValueError, KeyError) as e:
        print(f"Error: Decryption failed - {e}", file=sys.stderr)
        return False

    with open(plaintext_path, "wb") as f:
        f.write(plaintext)

    print(f"Decrypted '{ciphertext_path}' -> '{plaintext_path}'")
    return True


def main():
    desc = textwrap.dedent("""\
        AES Symmetric Key Encryption/Decryption

        Encrypt or decrypt files using AES-128-CBC with PKCS7 padding.

        Usage:
            python AES.py encrypt --key YOUR16BYTEKEY --plain Plain.txt --cipher Cipher.txt
            python AES.py decrypt --key YOUR16BYTEKEY --cipher Cipher.txt --plain Plain.txt
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    subparsers = parser.add_subparsers(dest="command")

    encrypt_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    encrypt_parser.add_argument("--key", "-K", type=str, required=True, help="16-byte encryption key")
    encrypt_parser.add_argument("--plain", "-P", type=str, required=True, help="Input plaintext file")
    encrypt_parser.add_argument("--cipher", "-C", type=str, default="Cipher.txt", help="Output ciphertext file (default: Cipher.txt)")

    decrypt_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    decrypt_parser.add_argument("--key", "-K", type=str, required=True, help="16-byte decryption key")
    decrypt_parser.add_argument("--cipher", "-C", type=str, required=True, help="Input ciphertext file")
    decrypt_parser.add_argument("--plain", "-P", type=str, default="Plain.txt", help="Output plaintext file (default: Plain.txt)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)
    elif args.command == "encrypt":
        aes_encrypt(args.key, args.plain, args.cipher)
    elif args.command == "decrypt":
        aes_decrypt(args.key, args.cipher, args.plain)


if __name__ == "__main__":
    main()
