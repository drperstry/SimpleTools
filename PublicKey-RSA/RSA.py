from Crypto.PublicKey import RSA
from Crypto.Random import get_random_bytes
from Crypto.Cipher import AES, PKCS1_OAEP
import argparse
import textwrap


def Generate_RSA_Keys():
    try:
        key = RSA.generate(2048)
        private_key = key.export_key()
        public_key = key.publickey().export_key()
    except :
        return 'Keys were not Generated due to error in dependincies, make sure you installed requirements.txt'

    with open('.\Question2\PublicKey-RSA\PrivateKey.pem', 'wb') as f:
        f.write(private_key)

    with open('.\Question2\PublicKey-RSA\PublicKey.pem', 'wb') as f:
        f.write(public_key)
    
    return 'Keys are Generated'


def RSA_Encrypt(PublicKey, Plain):
    try:
        with open(Plain, 'rb') as f:
            data=f.read()
    except:
        return 'Plaintext is not found or not a text file'
    
    # data = data.encode("utf-8")

    # getting the publickey
    try:
        recipient_key = RSA.import_key(open(PublicKey).read())
    except:
        return 'Public key is not correct'

    try:
        session_key = get_random_bytes(16)
        # Encrypt the session key with the public RSA key
        cipher_rsa = PKCS1_OAEP.new(recipient_key)
        enc_session_key = cipher_rsa.encrypt(session_key)

        # Encrypt the data with the AES session key, encrypting using AES mode EAX
        cipher_aes = AES.new(session_key, AES.MODE_EAX)
        ciphertext, tag = cipher_aes.encrypt_and_digest(data)
    except:
        return 'Encryption failed due to error in dependincies, make sure you installed requirements.txt'

    # writing chiphertext into the output file
    try:
        with open('./Question2/PublicKey-RSA/EncryptedText.bin', 'wb') as f:
            [ f.write(x) for x in (enc_session_key, cipher_aes.nonce, tag, ciphertext) ]
    except:
        return 'Failed to write Encryption in the output file'
    return 'Encrypted Successfully'


def RSA_Decrypt(PrivateKey, Cipher, Plain=".\Question2\PublicKey-RSA\Plain.txt"):
    try:
        private_key = RSA.import_key(open(PrivateKey).read())
    except:
        return 'Private Key is not correct'
    
    try:
        with open(Cipher, 'rb') as f:
            enc_session_key, nonce, tag, ciphertext = \
            [f.read(x) for x in (private_key.size_in_bytes(), 16, 16, -1) ]
    except:
        return 'CipherText is not correct'

    try:
    # Decrypt the session key with the private RSA key
        cipher_rsa = PKCS1_OAEP.new(private_key)
        session_key = cipher_rsa.decrypt(enc_session_key)

    # Decrypt the data with the AES session key
        cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
        data = cipher_aes.decrypt_and_verify(ciphertext, tag)
    except:
        return 'Decryption failed due to error in dependincies, make sure you installed requirements.txt'
    try:
        with open(Plain, 'wb') as f:
            f.write(data)
    except:
        return 'Issue with Plaintext location'
    return 'Decrypted Successfully'


def main():
    desc=textwrap.dedent('''RSA:
            Encryption/Decryption file using Public Key and Private Key (RSA)
            [opts means optional]
            usage:
                1: python RSA.py GenerateKeys [-h]
                2: python RSA.py Encrypt [-h] --PublicKey PublicKey.bin --Plaintext Plain.txt
                3: python RSA.py Decrypt [-h] --PrivateKey PrivateKey --Ciphertext Cipher.bin [opt] --Plaintext Plain.txt''')
                
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter, description=desc)
    subparser=parser.add_subparsers(dest='Command')
    subparser.add_parser('GenerateKeys')
    Encrypt=subparser.add_parser('Encrypt')
    Decrypt=subparser.add_parser('Decrypt')

    Encrypt.add_argument("--PublicKey", '-PubK',type=str, help="--PublicKey PublicKey.pem", required=True)
    Encrypt.add_argument("--Plaintext", '-P',type=str, help="--Plaintext Plain.txt", required=True)

    Decrypt.add_argument("--PrivateKey", '-PrK',type=str, help="--PrivateKey PrivateKey.pem", required=True)
    Decrypt.add_argument("--Ciphertext", '-C',type=str, help="--Ciphertext Cipher.bin", required=True)
    Decrypt.add_argument("--Plaintext", '-P',type=str, help="--Plaintext Plain.txt", required=False)

    args = parser.parse_args()

    if args.Command == None:
        print("choose one of those commands [GenerateKeys, Encrypt, Decrypt]")
    elif args.Command == 'GenerateKeys':
        print(Generate_RSA_Keys())
    elif args.Command == 'Encrypt':
        print(RSA_Encrypt(args.PublicKey,args.Plaintext))
    elif args.Command == 'Decrypt':
        if(args.Plaintext):
            print(RSA_Decrypt(args.PrivateKey, args.Ciphertext, args.Plaintext))
        else:
            print(RSA_Decrypt(args.PrivateKey, args.Ciphertext))


# Driver Code
if __name__ == '__main__' :
    # Calling main function
    main()