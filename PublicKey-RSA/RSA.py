import argparse
import os
import sys
import textwrap

from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes


def generate_keys(output_dir="."):
    """Generate a 2048-bit RSA key pair and save to PEM files."""
    key = RSA.generate(2048)

    private_path = os.path.join(output_dir, "PrivateKey.pem")
    public_path = os.path.join(output_dir, "PublicKey.pem")

    with open(private_path, "wb") as f:
        f.write(key.export_key())

    with open(public_path, "wb") as f:
        f.write(key.publickey().export_key())

    print(f"Keys generated: '{private_path}', '{public_path}'")
    return True


def rsa_encrypt(public_key_path, plaintext_path, ciphertext_path="EncryptedText.bin"):
    """Encrypt a file using RSA + AES hybrid encryption."""
    try:
        with open(plaintext_path, "rb") as f:
            data = f.read()
    except FileNotFoundError:
        print(f"Error: Plaintext file '{plaintext_path}' not found.", file=sys.stderr)
        return False

    try:
        with open(public_key_path, "r") as f:
            recipient_key = RSA.import_key(f.read())
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: Invalid public key - {e}", file=sys.stderr)
        return False

    session_key = get_random_bytes(16)

    cipher_rsa = PKCS1_OAEP.new(recipient_key)
    enc_session_key = cipher_rsa.encrypt(session_key)

    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    ciphertext, tag = cipher_aes.encrypt_and_digest(data)

    with open(ciphertext_path, "wb") as f:
        for chunk in (enc_session_key, cipher_aes.nonce, tag, ciphertext):
            f.write(chunk)

    print(f"Encrypted '{plaintext_path}' -> '{ciphertext_path}'")
    return True


def rsa_decrypt(private_key_path, ciphertext_path, plaintext_path="Decrypted.txt"):
    """Decrypt a file using RSA + AES hybrid decryption."""
    try:
        with open(private_key_path, "r") as f:
            private_key = RSA.import_key(f.read())
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: Invalid private key - {e}", file=sys.stderr)
        return False

    try:
        with open(ciphertext_path, "rb") as f:
            enc_session_key = f.read(private_key.size_in_bytes())
            nonce = f.read(16)
            tag = f.read(16)
            ciphertext = f.read()
    except FileNotFoundError:
        print(f"Error: Ciphertext file '{ciphertext_path}' not found.", file=sys.stderr)
        return False

    try:
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    except (ValueError, KeyError) as e:
        print(f"Error: Decryption failed - {e}", file=sys.stderr)
        return False

    with open(plaintext_path, "wb") as f:
        f.write(data)

    print(f"Decrypted '{ciphertext_path}' -> '{plaintext_path}'")
    return True


def main():
    desc = textwrap.dedent("""\
        RSA Public Key Encryption/Decryption

        Generate RSA key pairs and encrypt/decrypt files using
        RSA + AES hybrid encryption (RSA for session key, AES-EAX for data).

        Usage:
            python RSA.py generate [--output-dir .]
            python RSA.py encrypt --public-key PublicKey.pem --plaintext Plain.txt
            python RSA.py decrypt --private-key PrivateKey.pem --ciphertext Cipher.bin
    """)

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=desc,
    )
    subparsers = parser.add_subparsers(dest="command")

    gen_parser = subparsers.add_parser("generate", help="Generate RSA key pair")
    gen_parser.add_argument("--output-dir", "-O", type=str, default=".", help="Directory to save keys (default: current directory)")

    enc_parser = subparsers.add_parser("encrypt", help="Encrypt a file")
    enc_parser.add_argument("--public-key", "-PubK", type=str, required=True, help="Path to public key PEM file")
    enc_parser.add_argument("--plaintext", "-P", type=str, required=True, help="Input plaintext file")
    enc_parser.add_argument("--ciphertext", "-C", type=str, default="EncryptedText.bin", help="Output ciphertext file (default: EncryptedText.bin)")

    dec_parser = subparsers.add_parser("decrypt", help="Decrypt a file")
    dec_parser.add_argument("--private-key", "-PrK", type=str, required=True, help="Path to private key PEM file")
    dec_parser.add_argument("--ciphertext", "-C", type=str, required=True, help="Input ciphertext file")
    dec_parser.add_argument("--plaintext", "-P", type=str, default="Decrypted.txt", help="Output plaintext file (default: Decrypted.txt)")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)
    elif args.command == "generate":
        generate_keys(args.output_dir)
    elif args.command == "encrypt":
        rsa_encrypt(args.public_key, args.plaintext, args.ciphertext)
    elif args.command == "decrypt":
        rsa_decrypt(args.private_key, args.ciphertext, args.plaintext)


if __name__ == "__main__":
    main()
